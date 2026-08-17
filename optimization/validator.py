#!/usr/bin/env python
"""CellPainting 结果一致性验证器（Validator Module）

实现 AI Agent 一致性机制中的「输出等价性检验门控」(Equivalence Gates)：

- 验证两个 CellProfiler 输出目录的 5 个 CSV 是否 bit-identical
- 区分「生物学测量值」(必须一致) vs 「运行时元信息」(可不同)
- 输出结构化验证报告 (pass/fail)，可作为 CI / Agent 流水线的门控

对应机制：
  第 1 点「状态感知与前置条件校验」→ DataState 状态树
  第 4 点「输出等价性检验门控」→ validate_csv_consistency / equivalence_gate

用法:
    python validator.py --baseline <dir> --optimized <dir>
    python validator.py --baseline BR00117035_A01_baseline10opt \
                        --optimized BR00117035_A01_final
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


# ============================================================
# 1. 状态树（第 1 点：隐式状态显示化）
# ============================================================
class DataState(str, Enum):
    """数据管线状态树，记录数据当前处于哪个阶段。

    顺序: RAW → SEGMENTED → SINGLE_CELL → AGGREGATED → NORMALIZED
          → FEATURE_SELECTED → PCA
    """
    RAW = "raw"
    SEGMENTED = "segmented"
    SINGLE_CELL = "single_cell"
    AGGREGATED = "aggregated"
    NORMALIZED = "normalized"
    FEATURE_SELECTED = "feature_selected"
    PCA = "pca"

    def next(self) -> "DataState":
        order = list(DataState)
        idx = order.index(self)
        return order[min(idx + 1, len(order) - 1)]


# ============================================================
# 运行时元信息列（不影响生物学结果，可不同）
# ============================================================
RUNTIME_METADATA_PATTERNS: Tuple[str, ...] = (
    "ExecutionTime_",   # 模块执行时间
    "ModuleError_",     # 模块错误标记
    "PathName_",        # 输出路径
    "FileName_",        # 输出文件名（如轮廓图文件名）
    "URL_",             # 输出 URL
    "Run_Timestamp",    # 运行时间戳
)

# 标识列（非测量值，不参与对比，拆分/合并时编号会变）
IDENTIFIER_COLUMNS: Tuple[str, ...] = ("ImageNumber", "ObjectNumber")

# 必须 bit-identical 的对象级测量表
MEASUREMENT_TABLES: Tuple[str, ...] = ("Cells.csv", "Nuclei.csv", "Cytoplasm.csv")
# 含元信息的表（测量值部分应一致，元信息可不同）
METADATA_TABLES: Tuple[str, ...] = ("Image.csv", "Experiment.csv")
# 纯元信息表（Key/Value 结构，全为运行时元数据，无测量值）
PURE_METADATA_TABLES: Tuple[str, ...] = ("Experiment.csv",)


# ============================================================
# 数据结构
# ============================================================
@dataclass
class ColumnDiff:
    """单列差异。"""
    column: str
    max_diff: float
    category: str  # "measurement" | "runtime_metadata"


@dataclass
class TableResult:
    """单表的验证结果。"""
    filename: str
    shape_baseline: Tuple[int, int] = (0, 0)
    shape_optimized: Tuple[int, int] = (0, 0)
    measurement_diffs: List[ColumnDiff] = field(default_factory=list)
    metadata_diffs: List[ColumnDiff] = field(default_factory=list)

    @property
    def shape_ok(self) -> bool:
        return self.shape_baseline == self.shape_optimized

    @property
    def measurement_identical(self) -> bool:
        """生物学测量值是否 bit-identical。"""
        return len(self.measurement_diffs) == 0

    @property
    def passed(self) -> bool:
        """门控是否通过：shape 一致 + 测量值 bit-identical。"""
        return self.shape_ok and self.measurement_identical


@dataclass
class ValidationReport:
    """整体验证报告。"""
    baseline_dir: Path
    optimized_dir: Path
    tables: Dict[str, TableResult]

    @property
    def passed(self) -> bool:
        return all(t.passed for t in self.tables.values())

    def summary(self, verbose: bool = False, max_cols: int = 15) -> str:
        lines = [f"验证: {self.baseline_dir.name} vs {self.optimized_dir.name}"]
        lines.append("=" * 60)
        for name, t in self.tables.items():
            status = "PASS" if t.passed else "FAIL"
            md = len(t.metadata_diffs)
            lines.append(
                f"  [{status}] {name:20s} "
                f"shape={t.shape_baseline}→{t.shape_optimized} "
                f"测量值差异={len(t.measurement_diffs)} "
                f"元信息差异={md}"
            )
            if verbose and t.measurement_diffs:
                # 按 max_diff 降序，列出前 max_cols 个差异列
                top = sorted(t.measurement_diffs, key=lambda d: -d.max_diff)[:max_cols]
                for d in top:
                    lines.append(f"        {d.column:50s} diff={d.max_diff:.6f}")
                if len(t.measurement_diffs) > max_cols:
                    lines.append(f"        ... 其余 {len(t.measurement_diffs)-max_cols} 列")
        lines.append("=" * 60)
        lines.append(f"  总判定: {'PASS' if self.passed else 'FAIL'}")
        return "\n".join(lines)


# ============================================================
# 分类逻辑
# ============================================================
def classify_column(column: str) -> str:
    """将列分类为「测量值」或「运行时元信息」。"""
    for pattern in RUNTIME_METADATA_PATTERNS:
        if column.startswith(pattern):
            return "runtime_metadata"
    return "measurement"


# ============================================================
# 等价性门控（第 4 点）
# ============================================================
def validate_csv_consistency(
    baseline_dir: Path,
    optimized_dir: Path,
    tables: Tuple[str, ...] = MEASUREMENT_TABLES + METADATA_TABLES,
    atol: float = 1e-6,
) -> ValidationReport:
    """验证两个 CellProfiler 输出目录的一致性。

    对每个 CSV：
      - 对比 shape
      - 逐列对比：数值列用 np.allclose(atol)（浮点容差内一致，浮点微差不算差异），非数值列用 equals
      - 分类差异为「测量值」或「运行时元信息」

    Args:
        baseline_dir: 基准输出目录（如 raw）
        optimized_dir: 优化输出目录（如 final）
        tables: 要对比的 CSV 文件名
        atol: 浮点容差（默认 1e-6），小于此值的浮点差异视为「一致」，不算优化差异

    Returns:
        ValidationReport，含每个表的差异明细和总判定。
    """
    results: Dict[str, TableResult] = {}
    for fname in tables:
        b_path = baseline_dir / fname
        o_path = optimized_dir / fname
        result = TableResult(filename=fname)

        if not b_path.exists() or not o_path.exists():
            # 缺失文件记为 FAIL
            results[fname] = result
            continue

        b_df = pd.read_csv(b_path)
        o_df = pd.read_csv(o_path)
        result.shape_baseline = b_df.shape
        result.shape_optimized = o_df.shape

        if not result.shape_ok:
            results[fname] = result
            continue

        pure_metadata = fname in PURE_METADATA_TABLES
        for col in b_df.columns:
            if col in IDENTIFIER_COLUMNS:
                continue  # 跳过标识列（ImageNumber/ObjectNumber）
            category = classify_column(col)
            if pd.api.types.is_numeric_dtype(b_df[col]):
                b_vals = b_df[col].fillna(0).to_numpy()
                o_vals = o_df[col].fillna(0).to_numpy()
                if not np.allclose(b_vals, o_vals, atol=atol, rtol=0):
                    diff = ColumnDiff(
                        column=col,
                        max_diff=float(np.abs(b_vals - o_vals).max()),
                        category=category,
                    )
                    (result.metadata_diffs if (category == "runtime_metadata" or pure_metadata)
                     else result.measurement_diffs).append(diff)
            else:
                if not b_df[col].equals(o_df[col]):
                    diff = ColumnDiff(column=col, max_diff=0.0, category=category)
                    (result.metadata_diffs if (category == "runtime_metadata" or pure_metadata)
                     else result.measurement_diffs).append(diff)

        results[fname] = result

    return ValidationReport(baseline_dir=baseline_dir, optimized_dir=optimized_dir, tables=results)


# ============================================================
# CLI
# ============================================================
def main() -> int:
    parser = argparse.ArgumentParser(description="CellPainting 结果一致性验证器")
    parser.add_argument("--baseline", required=True, type=Path, help="基准输出目录")
    parser.add_argument("--optimized", required=True, type=Path, help="优化输出目录")
    parser.add_argument("--tables", nargs="*", default=None, help="要对比的 CSV（默认 5 个）")
    parser.add_argument("--verbose", action="store_true", help="输出具体差异列名 + 幅度")
    parser.add_argument("--atol", type=float, default=1e-6, help="浮点容差（默认 1e-6），小于此值的浮点差异视为一致")
    args = parser.parse_args()

    tables = tuple(args.tables) if args.tables else MEASUREMENT_TABLES + METADATA_TABLES
    report = validate_csv_consistency(args.baseline, args.optimized, tables, atol=args.atol)
    print(report.summary(verbose=args.verbose))

    # 等价性门控：测量值有任何差异则退出码非 0
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
