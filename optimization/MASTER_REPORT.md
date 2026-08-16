# CellPainting-Claw Optimization Report

> Date: 2026-08-07  |  Data: BR00117035 A01+A02  
> Hardware: CPU Intel Genuine 2.68 GHz, 20 cores, AVX2 + oneDNN

---

## 1. Overview

```
BR00117035 Microscopy Images (1080x1080, 8ch TIFF)
    │
    ├──→ CellProfiler (optimized 4.2.8)  → Classical features  →  PCA
    │      165.9s                          1,941 features (A01)
    │
    └──→ DeepProfiler (pipeline optimized) → Deep features      →  Collect
           24.1s                              672 features
```

---

## 2. CellProfiler — Segmentation + Classical Pipeline

### 2.1 Optimization: Before vs After

| | Before (4.2.6) | After (4.2.8) | Speedup |
|---|:---:|:---:|:---:|
| **Total time** | 594.7s | **287.7s** | **2.1×** |
| Common modules | 428.9s | 278.0s | 1.5× |
| Cells detected | 68 | 68 | identical |
| Output | 5 CSVs | 5 CSVs | identical |

### 2.2 Full Classical Pipeline: A01+A02 (optimized)

| Step | Time | Share |
|------|:---:|:---:|
| CellProfiler A01 | 418.7s | 43.3% |
| CellProfiler A02 | 515.3s | 53.2% |
| Single-cell table | 12.0s | 1.2% |
| Aggregate | 2.8s | 0.3% |
| Annotate | 2.1s | 0.2% |
| Normalize | 9.0s | 0.9% |
| Feature select | 4.9s | 0.5% |
| PCA + Summary | 3.1s | 0.3% |
| **Total** | **967.9s (16.1 min)** | **100%** |

Output: A01 68 cells + A02 55 cells = 123 total, 14,992 features selected from 15,524 raw
Result: **A01 & A02 Cells.csv both bit-identical to pre-optimization (0/1941 column diffs)**

### 2.3 Colocalization Optimization (NEW — result bit-identical)

Profile 定位 Colocalization 瓶颈后，追加三个算法级优化（不砍模块，结果 bit-identical）：

| # | Optimization | Function | Speedup |
|---|-------------|----------|:---:|
| 1 | `lexsort` → `argsort` (stable) | `get_image_rank` (RWC) | 2.0× |
| 2 | `ndimage.maximum` → `np.maximum.at` | `get_threshold_values_for_objects` | 18× |
| 3 | `ndimage.sum` → `np.bincount` | `get_thresholded_sum` | 1.6× |

| | Before | After | Speedup |
|---|:---:|:---:|:---:|
| A01 | 598.2s | **418.7s** | −30% (−179.5s) |
| A02 | 736.6s | **515.3s** | −30% (−221.3s) |
| **合计** | **1334.8s** | **934.0s** | **−30% (−400.8s)** |

| 一致性 | A01 | A02 |
|---|:---:|:---:|
| Cells.csv | (68, 1941) → (68, 1941) | (55, 1941) → (55, 1941) |
| 数值差异列 | **0 (bit-identical)** | **0 (bit-identical)** |

> 关键：dense rank 只依赖像素值，`labels` 次键无影响；`np.maximum.at` / `np.bincount` 与 `scipy.ndimage` 等价（含空 label 边界）。三个优化逐一验证 `array_equal = True`，端到端 Cells.csv 1941 列全部一致。

### 2.4 内存 HDF5 负优化发现 + 最终版

用完全没优化的 `D:\CellProfiler-raw` 作为真基准，对比后发现 **10 项优化里的"内存 HDF5"是严重负优化**：

| 版本 | 优化状态 | A01 | A02 |
|------|---------|:---:|:---:|
| raw | 完全没优化（磁盘 HDF5）| 201.7s | 177.6s |
| fork（内存 HDF5 + 三个优化）| 10 项含内存 HDF5 | 418.7s | 515.3s |
| **fork 最终（磁盘 HDF5 + 三个优化）** | 去掉内存 HDF5 | **165.9s** | **161.3s** |

**根因**：内存 HDF5（`driver=core, backing_store=False`）在 MeasureTexture 大量纹理测量写入时导致内存膨胀，把 MeasureTexture 从 68s 拖慢到 290s（4.3×）。

| 模块（A01）| raw | 内存HDF5 | 最终 | 最终 vs raw |
|-----------|:---:|:---:|:---:|:---:|
| MeasureTexture | 68.23s | 290.38s | **59.80s** | −8.4s |
| MeasureGranularity | 49.09s | 51.47s | **41.20s** | −7.9s |
| MeasureColocalization | 24.95s | 18.80s | **17.89s** | −7.1s |
| 其他模块合计 | ~32.7s | ~38.4s | ~29.8s | −2.9s |
| **模块时间合计** | **174.98s** | 399.03s | **148.73s** | **−26.3s (−15%)** |

**最终结论**：
- 真正可靠的优化只有**三个 Colocalization 优化**（结果 bit-identical）
- "内存 HDF5"是负优化，应去掉（保持磁盘 HDF5）
- GC 软化 `gen=0` 在磁盘 HDF5 场景因 `get_conserve_memory()` 默认 False 会完全不 GC 导致超时，应保持全代回收
- **最终版 327.2s（A01+A02）比 raw 379.3s 快 13.7%，且测量结果 bit-identical**

---

## 3. DeepProfiler — Feature Extraction

### 3.1 Optimization: Before vs After

| | Before | After | Delta |
|---|:---:|:---:|:---:|
| **Total time** | 26.3s | **24.1s** | **−8%** |
| Profile | 25.0s | **22.8s** | −9% |
| Collect | 1.2s | **1.0s** | −17% |
| **Features** | (68, 672) | (68, 672) | **identical (4.77e-7)** |
| Invocation | CLI subprocess | direct `import` | — |

### 3.2 Full DeepProfiler Pipeline: A01+A02

| Step | Time | Share |
|------|:---:|:---:|
| Export | 0.175s | 0.7% |
| Build | 0.125s | 0.5% |
| Checkpoint | 0.021s | 0.1% |
| **Profile** | **22.803s** | **94.6%** |
| Collect (NPZ→tables) | 0.977s | 4.1% |
| **Total** | **24.1s** | **100%** |

Output: A01 68 cells × 672-d, A02 55 cells × 672-d (18 files)

---

## 4. Full Stack Timing

| Stage | CellProfiler (A01) | DeepProfiler |
|-------|:---:|:---:|
| Setup | — | 0.3s |
| Processing | 165.9s | 22.8s |
| Collect/Tables | — | 1.0s |
| pycytominer | 26.6s | — |
| **Total** | **192.5s** | **24.1s** |
| **Per-well marginal** | ~160s | ~0.2s (after cold start) |

---

## 5. Result Consistency

### CellProfiler: 13.7% faster, measurements bit-identical

最终版（磁盘 HDF5 + 三个优化）vs 完全没优化的 raw：

| 文件 | 结果 |
|------|:---:|
| Cells.csv (1941 列) | ✅ 0 差异（bit-identical）|
| Nuclei.csv (1934 列) | ✅ 0 差异 |
| Cytoplasm.csv (1926 列) | ✅ 0 差异 |
| Image.csv | ⚠️ 仅 ExecutionTime + 输出路径不同（元信息）|
| Experiment.csv | ⚠️ 仅 Run_Timestamp 不同（元信息）|

> 3 个对象级测量表（Cells/Nuclei/Cytoplasm）的**生物学测量值全部 bit-identical**。
> Image/Experiment 的差异只是模块执行时间、输出路径、运行时间戳等**运行时元信息**，不是测量值。

### DeepProfiler: 8% faster, features identical to float32 precision

| | Before | After |
|---|:---:|:---:|
| Cell count | 68 | 68 |
| Locations | bit-identical | bit-identical |
| Features (max diff) | — | 4.77×10⁻⁷ |
| NaN rate | 0% | 0% |

---

## 6. Scripts

```
optimization/
├── MASTER_REPORT.md
├── optimization_notebook.ipynb
├── cellprofiler/
│   ├── README.md                     ← 10-optimization report
│   ├── TIMING_REPORT.md              ← Detailed timing
│   ├── BEFORE_AFTER_COMPARISON.md    ← 594.7s→287.7s, 2.1×
│   ├── run.py                        ← Benchmark script
│   └── run_full.py                   ← Full classical pipeline
└── deepprofiler/
    ├── README.md                     ← 7-optimization report
    ├── BEFORE_AFTER_COMPARISON.md    ← 26.3s→24.1s, features identical
    ├── run.py                        ← Run command
    ├── run.bat                       ← Double-click run
    └── pipeline.py                   ← Full DP pipeline
```

---

*Generated: 2026-08-07 | Data: BR00117035 A01+A02*
