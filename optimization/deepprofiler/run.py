"""
DeepProfiler 本地优化版 — 完整运行命令
======================================
双击运行或在终端执行:
    python run.py
"""

import os, sys, time, subprocess
from pathlib import Path

# ============================================================
# 路径配置
# ============================================================
PYTHON_EXE   = r"D:\MINICONDA\envs\cellpainting-claw\python.exe"
PYTHONPATH   = r"D:\CellPainting-Claw-main2\DeepProfiler-master\DeepProfiler-master"
SCRIPT       = r"D:\CellPainting-Claw-main2\CellPainting-Claw-main\optimization\deepprofiler\pipeline.py"
DATA_DIR     = r"D:\CellPainting-Claw-main2\CellPainting-Claw-main\demo\workspace\reference_data\BR00117035"
OUTPUT_DIR   = r"D:\CellPainting-Claw-main2\CellPainting-Claw-main\demo\workspace\outputs\deepprofiler_pipeline"

# ============================================================
# 清理旧输出
# ============================================================
if os.path.exists(OUTPUT_DIR):
    print(f"[清理] 删除 {OUTPUT_DIR}")
    import shutil
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

# ============================================================
# 运行
# ============================================================
env = os.environ.copy()
env["PYTHONPATH"] = PYTHONPATH + os.pathsep + env.get("PYTHONPATH", "")

print(f"开始: {time.strftime('%H:%M:%S')}")
print(f"数据: {DATA_DIR}")
print(f"输出: {OUTPUT_DIR}")
print()

t0 = time.perf_counter()
result = subprocess.run(
    [PYTHON_EXE, SCRIPT],
    env=env,
    timeout=120,
)
elapsed = time.perf_counter() - t0

print(f"结束: {time.strftime('%H:%M:%S')}  |  耗时: {elapsed:.1f}s  |  exit={result.returncode}")

# ============================================================
# 显示输出
# ============================================================
feat_dir = Path(OUTPUT_DIR) / "deepprofiler_project" / "outputs" / "cell_painting_cnn" / "features"
npz_files = sorted(feat_dir.rglob("*.npz")) if feat_dir.exists() else []
if npz_files:
    print(f"\n特征文件 ({len(npz_files)}):")
    for f in npz_files:
        sz = f.stat().st_size
        print(f"  {f.relative_to(feat_dir)}  ({sz:,} bytes)")
