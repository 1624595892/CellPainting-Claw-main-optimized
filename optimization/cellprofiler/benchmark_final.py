"""Final benchmark: fork (disk HDF5 + GC gen0 + 3 Colocalization opt) on A01+A02."""
import time, os, shutil, subprocess, json
from pathlib import Path
import pandas as pd

BASE     = Path(r"D:\CellPainting-Claw-main2\CellPainting-Claw-main")
PYTHON   = Path(r"D:\MINICONDA\envs\cellpainting-claw\python.exe")
CP_SRC   = Path(r"D:\CellPainting-Claw-main2\CellProfiler-main\CellProfiler-main\src")
CP_PP    = os.pathsep.join([str(CP_SRC/"frontend"), str(CP_SRC/"subpackages/core"), str(CP_SRC/"subpackages/library")])
PIPELINE = BASE / "demo/backend/profiling_backend/cellprofiler/CPJUMP1_analysis_smoketest_granularity.cppipe"
REF_DIR  = BASE / "demo/workspace/reference_data/BR00117035"
OUT_BASE = BASE / "demo/workspace/outputs"
PLATE    = "BR00117035"

results = {}
t_total = time.perf_counter()

for well in ["A01", "A02"]:
    well_dir = REF_DIR / well
    tiff_files = sorted(well_dir.glob("*.tiff"))
    row = {"Metadata_Plate": PLATE, "Metadata_Well": well, "Metadata_Site": "1"}
    for tag, ch_idx in [("OrigMito",1),("OrigAGP",2),("OrigRNA",3),("OrigER",4),
                          ("OrigDNA",5),("OrigBrightfield",8),("OrigHighZBF",6),("OrigLowZBF",7)]:
        match = [f for f in tiff_files if f"ch{ch_idx}sk1fk1fl1" in f.name]
        row[f"FileName_{tag}"] = match[0].name if match else ""
        row[f"PathName_{tag}"] = str(well_dir)
    illum = REF_DIR / "illumination"
    for tag, chan in [("DNA","DNA"),("Mito","Mito"),("AGP","AGP"),("RNA","RNA"),
                       ("ER","ER"),("Brightfield","Brightfield"),("HighZBF","HighZBF"),("LowZBF","LowZBF")]:
        row[f"FileName_Illum{chan}"] = f"Illum{chan}.npy"
        row[f"PathName_Illum{chan}"] = str(illum)
    load_csv = OUT_BASE / f"load_data_{well}_final.csv"
    pd.DataFrame([row]).to_csv(load_csv, index=False)

    cp_out = OUT_BASE / f"BR00117035_{well}_final"
    if cp_out.exists(): shutil.rmtree(cp_out)
    cp_out.mkdir(parents=True)

    print(f"Running final fork on {PLATE} {well}...")
    t0 = time.perf_counter()
    cmd = [str(PYTHON), "-m", "cellprofiler", "-c", "-r",
           "-p", str(PIPELINE), "-o", str(cp_out), "-i", str(well_dir),
           "--data-file", str(load_csv),
           "-e", "imageio_reader_v3", "imageio_reader", "ngff_reader", "gcs_reader"]
    env = os.environ.copy()
    env["PYTHONPATH"] = CP_PP + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, env=env)
    elapsed = time.perf_counter() - t0
    print(f"  {well}: {elapsed:.1f}s (exit {result.returncode})")

    if result.returncode == 0:
        img = pd.read_csv(cp_out / "Image.csv")
        mod_times = {c.replace("ExecutionTime_",""): img[c].iloc[0] for c in img.columns if c.startswith("ExecutionTime_")}
        n = len(pd.read_csv(cp_out / "Nuclei.csv"))
        results[well] = {"total": elapsed, "modules": mod_times, "nuclei": n}
        # 打印 top 5 模块
        top = sorted(mod_times.items(), key=lambda x: -x[1])[:5]
        print(f"  {well}: {n} cells, top modules: " + ", ".join(f"{k}={v:.1f}s" for k,v in top))
    else:
        print(f"  {well} STDERR: {result.stderr[-500:]}")

total_elapsed = time.perf_counter() - t_total
print("\n" + "=" * 60)
print("  FINAL RESULT (disk HDF5 + GC gen0 + 3 opt)")
print("=" * 60)
for well in ["A01", "A02"]:
    if well in results:
        r = results[well]
        print(f"  {well}: {r['total']:.1f}s ({r['nuclei']} cells)")
print(f"  {'-'*45}")
print(f"  CP total: {sum(r['total'] for r in results.values()):.1f}s")
print(f"  对比: raw 201.7+177.6=379.3s, fork优化前 598.2+736.6=1334.8s")
print("=" * 60)

# 保存结果
with open(OUT_BASE / "final_benchmark_summary.json", "w") as f:
    json.dump({w: {"total": r["total"], "nuclei": r["nuclei"]} for w,r in results.items()}, f, indent=2)
print("\nSummary saved to final_benchmark_summary.json")
