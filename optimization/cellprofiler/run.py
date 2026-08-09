#!/usr/bin/env python
"""Run optimized CellProfiler on BR00117035 and generate timing report.

Usage:
    python run_cellprofiler_benchmark.py

Requires: conda env cellpainting-claw with optimized CellProfiler installed.
"""

import subprocess
import time
import re
import shutil
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────
CELLPROFILER = Path("D:/MINICONDA/envs/cellpainting-claw/Scripts/cellprofiler.exe")
REPO = Path("D:/CellPainting-Claw-main2/CellPainting-Claw-main")
DATA_DIR = REPO / "demo/workspace/reference_data/BR00117035"
PIPELINE = REPO / "demo/backend/profiling_backend/cellprofiler/CPJUMP1_analysis_smoketest.cppipe"
OUTPUT_ROOT = Path("D:/CellPainting-Claw-main2/CellProfiler-main")

# ── Config ─────────────────────────────────────────────────────
PLATE = "BR00117035"
WELL = "A01"
SITE = "1"
CHANNEL_MAP = {
    "Mito":        "ch1",
    "AGP":         "ch2",
    "RNA":         "ch3",
    "ER":          "ch4",
    "DNA":         "ch5",
    "Brightfield": "ch8",
    "HighZBF":     "ch6",
    "LowZBF":      "ch7",
}

# ── Step 1: Create output directories ──────────────────────────
RUN_DIR = OUTPUT_ROOT / f"run_{time.strftime('%Y%m%d_%H%M%S')}"
RUN_DIR.mkdir(parents=True, exist_ok=True)
print(f"Output dir: {RUN_DIR}")

# ── Step 2: Create load_data.csv with absolute paths ────────────
ILLUM_DIR = DATA_DIR / "illumination"
ILLUM_DIR.mkdir(parents=True, exist_ok=True)

# Create dummy illumination files if not present (1080x1080, all 1.0)
import numpy as np
for ch_name in ["DNA", "Mito", "AGP", "RNA", "ER", "Brightfield", "HighZBF", "LowZBF"]:
    illum_path = ILLUM_DIR / f"Illum{ch_name}.npy"
    if not illum_path.exists():
        np.save(illum_path, np.ones((1080, 1080), dtype=np.float64))

load_data_csv = DATA_DIR / "load_data.csv"
img_dir_str = str(DATA_DIR.resolve()).replace("\\", "/")
illum_dir_str = str(ILLUM_DIR.resolve()).replace("\\", "/")

with open(load_data_csv, "w", newline="") as f:
    import csv
    w = csv.writer(f)
    header = []
    row = [PLATE, WELL, SITE]
    for ch_name, ch_num in CHANNEL_MAP.items():
        header += [f"FileName_Orig{ch_name}", f"PathName_Orig{ch_name}"]
        row += [f"r01c01f01p01-{ch_num}sk1fk1fl1.tiff", img_dir_str]
    for ch_name in ["DNA", "Mito", "AGP", "RNA", "ER", "Brightfield", "HighZBF", "LowZBF"]:
        header += [f"FileName_Illum{ch_name}", f"PathName_Illum{ch_name}"]
        row += [f"Illum{ch_name}.npy", illum_dir_str]
    w.writerow(["Metadata_Plate", "Metadata_Well", "Metadata_Site"] + header)
    w.writerow(row)

print(f"load_data: {load_data_csv}")

# ── Step 3: Verify inputs ──────────────────────────────────────
assert CELLPROFILER.exists(), f"CellProfiler not found: {CELLPROFILER}"
assert PIPELINE.exists(), f"Pipeline not found: {PIPELINE}"
assert load_data_csv.exists(), f"load_data not found: {load_data_csv}"
print(f"CellProfiler: {CELLPROFILER}")
print(f"Pipeline:    {PIPELINE}")

# ── Step 4: Run CellProfiler ───────────────────────────────────
cmd = [
    str(CELLPROFILER), "-c", "-r",
    "-p", str(PIPELINE),
    "-o", str(RUN_DIR),
    "-i", str(DATA_DIR),
    "--data-file", str(load_data_csv),
    "-e", "imageio_reader_v3", "imageio_reader", "ngff_reader", "gcs_reader",
]

print(f"\n{'='*60}")
print(f"Start: {time.strftime('%H:%M:%S')}")
print(f"Command: {' '.join(cmd)}")
print(f"{'='*60}\n")

t0 = time.perf_counter()
modules = []
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

for line in proc.stdout:
    m = re.search(
        r"Image # (\d+), module (.+?) # (\d+): "
        r"CPU_time = ([\d.]+) secs, Wall_time = ([\d.]+) secs", line
    )
    if m:
        img, name, mod_num, cpu, wall = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        modules.append((int(mod_num), name, float(cpu), float(wall)))
        print(f"  #{mod_num:2d} {name:<35s} CPU={cpu:>8s}s  Wall={wall:>8s}s")
    if "pipeline completed" in line:
        print("\n>>> PIPELINE COMPLETED <<<")
    if "pipeline_exception" in line:
        print("\n>>> PIPELINE EXCEPTION <<<")

proc.wait()
elapsed = time.perf_counter() - t0

# ── Step 5: Output summary ─────────────────────────────────────
total_cpu = sum(m[2] for m in modules)
print(f"\n{'='*60}")
print(f"Exit: {proc.returncode}  |  Wall: {elapsed:.1f}s  |  CPU: {total_cpu:.1f}s  |  Modules: {len(modules)}")
print(f"{'='*60}")

csv_files = list(RUN_DIR.glob("*.csv"))
print(f"\nOutput CSV ({len(csv_files)} files):")
for f in sorted(csv_files):
    print(f"  {f.name}  {f.stat().st_size:>10,} bytes")

# ── Step 6: Write timing report ────────────────────────────────
report_path = RUN_DIR / "timing_report.md"
with open(report_path, "w") as f:
    f.write(f"# CellProfiler 优化版 v4.2.8 — 模块计时\n\n")
    f.write(f"**日期:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"**数据:** {PLATE} {WELL} S{SITE}, 1080×1080×8ch\n")
    f.write(f"**Pipeline:** {PIPELINE.name}\n")
    f.write(f"**Wall-clock:** {elapsed:.1f}s  |  **CPU:** {total_cpu:.1f}s  |  **模块:** {len(modules)}\n\n")
    f.write("| # | 模块 | CPU (s) | Wall (s) | 占比 |\n")
    f.write("|---|------|---------|----------|------|\n")
    for num, name, cpu, wall in modules:
        pct = cpu / total_cpu * 100 if total_cpu > 0 else 0
        f.write(f"| {num} | {name} | {cpu:.2f} | {wall:.2f} | {pct:.1f}% |\n")
    f.write(f"\n## Top 5\n\n")
    for num, name, cpu, wall in sorted(modules, key=lambda x: x[2], reverse=True)[:5]:
        f.write(f"- **{name}** (#{num}): {cpu:.1f}s ({cpu/total_cpu*100:.0f}%)\n")

print(f"\nReport: {report_path}")
print(f"Done.")
