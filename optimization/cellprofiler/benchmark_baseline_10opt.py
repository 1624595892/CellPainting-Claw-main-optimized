"""Run UNOPTIMIZED baseline (D:\\CellProfiler-main, before 10 optimizations) on A01+A02."""
import time, os, shutil, subprocess
from pathlib import Path
import pandas as pd

BASE     = Path(r"D:\CellPainting-Claw-main2\CellPainting-Claw-main")
PYTHON   = Path(r"D:\MINICONDA\envs\cellpainting-claw\python.exe")
CP_SRC   = Path(r"D:\CellProfiler-raw\CellProfiler-main\src")  # 无优化 baseline
CP_PP    = os.pathsep.join([str(CP_SRC/"frontend"), str(CP_SRC/"subpackages/core"), str(CP_SRC/"subpackages/library")])
PIPELINE = BASE / "demo/backend/profiling_backend/cellprofiler/CPJUMP1_analysis_smoketest_granularity.cppipe"
REF_DIR  = BASE / "demo/workspace/reference_data/BR00117035"
OUT_BASE = BASE / "demo/workspace/outputs"
PLATE    = "BR00117035"

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
    load_csv = OUT_BASE / f"load_data_{well}_baseline.csv"
    pd.DataFrame([row]).to_csv(load_csv, index=False)

    cp_out = OUT_BASE / f"BR00117035_{well}_baseline10opt"
    if cp_out.exists(): shutil.rmtree(cp_out)
    cp_out.mkdir(parents=True)

    print(f"Running UNOPTIMIZED baseline on {PLATE} {well}...")
    t0 = time.perf_counter()
    cmd = [str(PYTHON), "-m", "cellprofiler", "-c", "-r",
           "-p", str(PIPELINE), "-o", str(cp_out), "-i", str(well_dir),
           "--data-file", str(load_csv),
           "-e", "imageio_reader_v3", "imageio_reader", "ngff_reader", "gcs_reader"]
    env = os.environ.copy()
    env["PYTHONPATH"] = CP_PP + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1500, env=env)
    elapsed = time.perf_counter() - t0
    print(f"  {well}: {elapsed:.1f}s (exit {result.returncode})")

    if result.returncode == 0:
        cells = pd.read_csv(cp_out / "Cells.csv", nrows=0)
        g = sum(1 for c in cells.columns if "Granularity" in c)
        c = sum(1 for c in cells.columns if "Correlation" in c)
        n = len(pd.read_csv(cp_out / "Nuclei.csv"))
        print(f"  {well}: {n} cells, {len(cells.columns)} cols ({g} Granularity, {c} Correlation)")
    else:
        (cp_out / "stderr.txt").write_text(result.stderr[-3000:], encoding="utf-8")
        print(f"  STDERR: {result.stderr[-800:]}")

print("\nDONE baseline run.")
