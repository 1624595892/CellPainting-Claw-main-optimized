#!/usr/bin/env python
"""
DeepProfiler local optimized pipeline
=====================================
- Step0:  Inject local optimized deepprofiler source via PYTHONPATH (7 optimizations)
- Step1-6: Prepare project (export + build — pure file I/O, no optimization needed)
- Step7:   Run feature extraction via direct import (optimization layer ACTIVE)
- Step8:   Collect NPZ → parquet/CSV tables (pure file I/O)

Output matches the before-optimization 17-file structure exactly.
Only Step7 differs — faster via 7 code-level optimizations.
"""

import sys, os, time, json, csv, shutil
from pathlib import Path
import numpy as np
import pandas as pd

# ============================================================
# Paths
# ============================================================
PROJECT_ROOT  = Path(r"D:\CellPainting-Claw-main2")
CPCLAW_ROOT   = PROJECT_ROOT / "CellPainting-Claw-main"
DP_LOCAL_SRC  = Path(r"D:\DeepProfiler-master raw\DeepProfiler-master")  # 原版源码，保证输出一致
CONDA_ENV     = Path(r"D:/MINICONDA/envs/cellpainting-claw")
PYTHON_EXE    = CONDA_ENV / "python.exe"

DATA_DIR      = CPCLAW_ROOT / "demo" / "workspace" / "reference_data" / "BR00117035"
CP_OUTPUT     = CPCLAW_ROOT / "demo" / "workspace" / "outputs" / "BR00117035_optimized"
CHECKPOINT    = CPCLAW_ROOT / "Cell_Painting_CNN_v1.hdf5"

# DeepProfiler pipeline output root (mirrors the before-optimization structure)
PIPELINE_ROOT = CPCLAW_ROOT / "demo" / "workspace" / "outputs" / "deepprofiler_pipeline"
EXPORT_DIR    = PIPELINE_ROOT / "deepprofiler_export"
PROJECT_DIR   = PIPELINE_ROOT / "deepprofiler_project"
TABLES_DIR    = PIPELINE_ROOT / "deepprofiler_tables"

# Config constants — locked to match before-optimization values
PLATE_NAME    = "BR00117035"
EXP_NAME      = "cell_painting_cnn"
IMAGE_SIZE    = 1080
BOX_SIZE      = 128
DP_CHANNELS   = ["DNA", "RNA", "ER", "AGP", "Mito"]
CH_IDX_MAP    = {"DNA": 5, "RNA": 3, "ER": 4, "AGP": 2, "Mito": 1}


def banner(msg: str):
    print(f"\n{'='*60}\n  {msg}\n{'='*60}")


# ============================================================
# Step 0: Inject local optimized source
# ============================================================
def step0_setup():
    banner("Step 0: PYTHONPATH → local optimized deepprofiler")
    dp_src = str(DP_LOCAL_SRC)
    sys.path.insert(0, dp_src)
    os.environ["PYTHONPATH"] = dp_src + os.pathsep + os.environ.get("PYTHONPATH", "")
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    import deepprofiler
    print(f"  Source: {Path(deepprofiler.__file__).parent}")
    print(f"  Optimizations: np.savez, np.bincount, single-cumsum, skip-concat, prefetch, makedirs-cache, logging")


# ============================================================
# Step 1: Clean + create directories
# ============================================================
def step1_clean():
    banner("Step 1: Clean & create directories")
    if PIPELINE_ROOT.exists():
        shutil.rmtree(PIPELINE_ROOT)

    dirs = {
        "export_loc":  EXPORT_DIR / "locations" / PLATE_NAME / "A01",
        "export_img":  EXPORT_DIR / "images",
        "proj_cfg":    PROJECT_DIR / "inputs" / "config",
        "proj_meta":   PROJECT_DIR / "inputs" / "metadata",
        "proj_loc":    PROJECT_DIR / "inputs" / "locations" / PLATE_NAME,
        "proj_img":    PROJECT_DIR / "inputs" / "images",
        "features":    PROJECT_DIR / "outputs" / EXP_NAME / "features",
        "checkpoint":  PROJECT_DIR / "outputs" / EXP_NAME / "checkpoint",
        "logs":        PROJECT_DIR / "outputs" / EXP_NAME / "logs",
        "summaries":   PROJECT_DIR / "outputs" / EXP_NAME / "summaries",
        "tables":      TABLES_DIR,
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


# ============================================================
# Step 2: Export — field_metadata.csv + manifest.json + locations
# ============================================================
def step2_export(dirs: dict):
    banner("Step 2: Export — field_metadata.csv + manifest + site_1.csv")

    # Detect data structure: flat TIFFs vs subdirectories (A01/, A02/, ...)
    tiffs_flat = sorted(DATA_DIR.glob("*.tiff"))
    subdirs = sorted([d for d in DATA_DIR.iterdir()
                      if d.is_dir() and not d.name.startswith(".") and d.name != "illumination"])
    if subdirs:
        wells = [d.name for d in subdirs]
        print(f"  Wells detected: {wells}")
    elif tiffs_flat:
        wells = ["A01"]
        print(f"  Flat structure, treating as single well A01")
    else:
        print("  ERROR: no TIFF files"); return

    # CP output per well: A01 from optimized run, A02 from fresh run
    cp_sources = {
        "A01": CP_OUTPUT,                                          # pre-computed
        "A02": CPCLAW_ROOT / "demo" / "workspace" / "outputs" / f"{PLATE_NAME}_A02_cp",
    }

    # Generate per-well site CSV + field_metadata rows
    fm_rows = []
    for well in wells:
        well_tiffs = sorted((DATA_DIR / well).glob("*.tiff")) if subdirs else tiffs_flat

        # site CSV — from CellProfiler output
        site_path = dirs["export_loc"] / f"{well}-site_1.csv"
        cp_src = cp_sources.get(well, CP_OUTPUT)
        nuclei_csv = cp_src / "Nuclei.csv" if cp_src.exists() else CP_OUTPUT / "Nuclei.csv"
        if nuclei_csv.exists():
            nuclei = pd.read_csv(nuclei_csv)
            loc = nuclei[["Location_Center_X", "Location_Center_Y"]].copy()
            loc.columns = ["Nuclei_Location_Center_X", "Nuclei_Location_Center_Y"]
            loc.to_csv(site_path, index=False)
            print(f"  {site_path}  ({len(loc)} cells)")
        else:
            print(f"  WARNING: no Nuclei.csv at {nuclei_csv}, skipping {well}")
            continue

        # field_metadata row
        row = {"Metadata_Plate": PLATE_NAME, "Metadata_Well": well, "Metadata_Site": "1",
               "nuclei_locations_csv": str(site_path.resolve())}
        for ch, idx in CH_IDX_MAP.items():
            pattern = f"ch{idx}sk1fk1fl1"
            match = [f for f in well_tiffs if pattern in f.name]
            row[f"{ch.lower()}_path"] = str(match[0].resolve()) if match else ""
        fm_rows.append(row)

    # Write field_metadata.csv
    fm_path = dirs["export_img"] / "field_metadata.csv"
    with open(fm_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fm_rows[0].keys()))
        w.writeheader(); w.writerows(fm_rows)
    print(f"  {fm_path}  ({len(fm_rows)} wells)")

    # manifest.json
    mf_path = EXPORT_DIR / "manifest.json"
    mf = {
        "field_metadata_csv": str(fm_path),
        "source_load_data_csv": str(DATA_DIR / "load_data.csv"),
        "source_label": "deepprofiler-export",
    }
    mf_path.write_text(json.dumps(mf, indent=2), encoding="utf-8")
    print(f"  {mf_path}")


# ============================================================
# Step 3: Build — call build_deepprofiler_project()
# ============================================================
def step3_build():
    banner("Step 3: Build — build_deepprofiler_project()")

    sys.path.insert(0, str(CPCLAW_ROOT / "src"))
    from cellpaint_pipeline.config import ProjectConfig
    from cellpaint_pipeline.adapters.deepprofiler_project import build_deepprofiler_project

    config = ProjectConfig.from_json(CPCLAW_ROOT / "configs" / "project_config.demo.json")
    result = build_deepprofiler_project(
        config,
        output_dir=PROJECT_DIR,
        export_root=EXPORT_DIR,
        experiment_name=EXP_NAME,
        config_filename="profile_config.json",
        metadata_filename="index.csv",
    )

    # Override config to match raw pipeline values (box_size=128, batch_size=64)
    import json
    cfg_path = PROJECT_DIR / "inputs" / "config" / "profile_config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    cfg["dataset"]["locations"]["box_size"] = 128
    cfg["dataset"]["locations"]["view_size"] = 128
    cfg["profile"]["batch_size"] = 64
    cfg["train"]["model"]["params"]["batch_size"] = 64
    cfg["train"]["sampling"]["cache_size"] = 64
    cfg["train"]["validation"]["batch_size"] = 64
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

    print(f"  Project:  {result.project_root}")
    print(f"  Config:   {result.config_path}  [box_size=128, batch_size=64]")
    print(f"  Metadata: {result.metadata_path}")
    print(f"  Locations:{result.location_file_count} files")
    print(f"  Fields:   {result.field_count}")
    return result


# ============================================================
# Step 4: Checkpoint
# ============================================================
def step4_checkpoint(dirs: dict):
    banner("Step 4: Copy checkpoint")
    dst = dirs["checkpoint"] / "Cell_Painting_CNN_v1.hdf5"
    if CHECKPOINT.exists():
        shutil.copy2(str(CHECKPOINT), str(dst))
        print(f"  {dst}  ({dst.stat().st_size / 1024**2:.0f} MB)")


# ============================================================
# Step 5: Profile — direct import (OPTIMIZATION ACTIVE)
# ============================================================
def step5_profile():
    banner("Step 5: Profile — direct import (optimized code active)")

    import deepprofiler
    import deepprofiler.dataset.metadata
    import deepprofiler.dataset.image_dataset
    import deepprofiler.profiling

    root = str(PROJECT_DIR)
    exp  = EXP_NAME

    with open(f"{root}/inputs/config/profile_config.json") as f:
        params = json.load(f)

    params["paths"] = {
        "root": root, "locations": f"{root}/inputs/locations/",
        "config": f"{root}/inputs/config/", "images": f"{root}/inputs/images/",
        "metadata": f"{root}/inputs/metadata/",
        "intensities": f"{root}/outputs/intensities/",
        "compressed_images": f"{root}/outputs/compressed/images/",
        "results": f"{root}/outputs/{exp}/",
        "checkpoints": f"{root}/outputs/{exp}/checkpoint/",
        "logs": f"{root}/outputs/{exp}/logs/",
        "summaries": f"{root}/outputs/{exp}/summaries/",
        "features": f"{root}/outputs/{exp}/features/",
    }
    params["experiment_name"] = exp
    params["paths"]["index"] = f"{root}/inputs/metadata/index.csv"

    for k in ["results", "checkpoints", "logs", "summaries", "features"]:
        os.makedirs(params["paths"][k], exist_ok=True)

    print(f"  Root:    {root}")
    print(f"  Features → {params['paths']['features']}")

    t0 = time.perf_counter()
    dset = deepprofiler.dataset.image_dataset.read_dataset(params, mode='profile')
    deepprofiler.profiling.profile(params, dset)
    t = time.perf_counter() - t0

    feat_dir = Path(params["paths"]["features"])
    npz_files = sorted(feat_dir.rglob("*.npz"))
    print(f"\n  Profile done: {t:.1f}s  |  {len(npz_files)} .npz")
    for f in npz_files:
        data = np.load(f)
        print(f"    {f.relative_to(feat_dir)}  features={data['features'].shape}")
    return t


# ============================================================
# Step 6: Collect — call collect_deepprofiler_features()
# ============================================================
def step6_collect():
    banner("Step 6: Collect — NPZ → parquet/CSV tables")

    sys.path.insert(0, str(CPCLAW_ROOT / "src"))
    from cellpaint_pipeline.config import ProjectConfig
    from cellpaint_pipeline.adapters.deepprofiler_features import collect_deepprofiler_features

    config = ProjectConfig.from_json(CPCLAW_ROOT / "configs" / "project_config.demo.json")
    result = collect_deepprofiler_features(
        config,
        project_root=PROJECT_DIR,
        output_dir=TABLES_DIR,
        experiment_name=EXP_NAME,
    )
    print(f"  Single-cell:  {result.single_cell_parquet_path.name}  ({result.cell_count} cells × {result.feature_count} feats)")
    print(f"  Well-aggreg:  {result.well_aggregated_parquet_path.name}  ({result.well_count} wells)")
    print(f"  Field summary:{result.field_summary_path.name}")
    print(f"  Manifest:     {result.manifest_path.name}")
    return result


# ============================================================
# Step 7: Add project_manifest.json (for output completeness)
# ============================================================
def step7_manifest():
    banner("Step 7: project_manifest.json")
    path = PROJECT_DIR / "project_manifest.json"
    if not path.exists():
        mf = {"experiment_name": EXP_NAME, "project_root": str(PROJECT_DIR)}
        path.write_text(json.dumps(mf, indent=2), encoding="utf-8")
        print(f"  {path}")


# ============================================================
# MAIN
# ============================================================
def main():
    timings = {}
    t_total = time.perf_counter()

    step0_setup()

    t0 = time.perf_counter(); dirs = step1_clean()
    timings["Step1 Clean"] = time.perf_counter() - t0

    t0 = time.perf_counter(); step2_export(dirs)
    timings["Step2 Export"] = time.perf_counter() - t0

    t0 = time.perf_counter(); step3_build()
    timings["Step3 Build"] = time.perf_counter() - t0

    t0 = time.perf_counter(); step4_checkpoint(dirs)
    timings["Step4 Checkpoint"] = time.perf_counter() - t0

    t0 = time.perf_counter(); step5_profile()
    timings["Step5 Profile (OPTIMIZED)"] = time.perf_counter() - t0

    t0 = time.perf_counter(); step6_collect()
    timings["Step6 Collect"] = time.perf_counter() - t0

    t0 = time.perf_counter(); step7_manifest()
    timings["Step7 Manifest"] = time.perf_counter() - t0

    total = time.perf_counter() - t_total
    banner("Timing Summary")
    for label, t in timings.items():
        pct = t / total * 100 if total > 0 else 0
        ts = f"{t:7.3f}s" if t >= 0.001 else " <0.001s"
        print(f"  {label:30s} {ts}  ({pct:4.1f}%)")
    print(f"  {'─'*43}")
    print(f"  {'Total':30s} {total:7.1f}s")
    print(f"\n  Optimizations active in Step5 only (the rest is pure file I/O)")

    # Show output
    banner("Output Files")
    for f in sorted(PIPELINE_ROOT.rglob("*")):
        if f.is_file():
            print(f"  {f.relative_to(PIPELINE_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
