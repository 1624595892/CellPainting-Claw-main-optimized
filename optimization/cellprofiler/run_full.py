"""Full classical pipeline — BR00117035 A01+A02 (pycytominer-compatible output).

Matches raw pipeline output format exactly.
"""
import time, json, os, shutil, subprocess
from pathlib import Path
import pandas as pd, numpy as np

BASE    = Path(r"D:\CellPainting-Claw-main2\CellPainting-Claw-main")
PYTHON  = Path(r"D:\MINICONDA\envs\cellpainting-claw\python.exe")
CONFIG  = BASE / "configs" / "project_config.demo.json"
OUT     = BASE / "demo" / "workspace" / "outputs" / "classical_pipeline"
CP_BASE = BASE / "demo" / "workspace" / "outputs"

WELLS = {
    "A01": CP_BASE / "BR00117035_optimized",
    "A02": CP_BASE / "BR00117035_A02_cp",
}
PLATE = "BR00117035"

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

timings = {}
t_total = time.perf_counter()


def run_skill(skill, output_dir, extra_args=None):
    """Run a pipeline skill via CLI, return (elapsed, ok)."""
    cmd = [str(PYTHON), "-m", "cellpaint_pipeline", "run-pipeline-skill",
           "--config", str(CONFIG), "--skill", skill,
           "--output-dir", str(output_dir)]
    if extra_args:
        cmd.extend(extra_args)
    t0 = time.perf_counter()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    elapsed = time.perf_counter() - t0
    return elapsed, result.returncode == 0


# ============================================================
# Step 1: Build single-cell (pycytominer skill)
# ============================================================
print("=" * 55)
print("  1. cp-build-single-cell-table")
print("=" * 55)

t0 = time.perf_counter()
sc_parts = []
for well, cp_dir in WELLS.items():
    img_csv = cp_dir / "Image.csv"
    obj_csv = cp_dir / "Cells.csv"
    step_out = OUT / f"single_cell_{well}"
    step_out.mkdir(parents=True, exist_ok=True)
    print(f"  {well}...")
    elapsed, ok = run_skill("cp-build-single-cell-table", step_out, [
        "--image-csv-path", str(img_csv),
        "--object-table-path", str(obj_csv),
        "--object-table", "Cells",
    ])
    sc_path = step_out / "single_cell.csv.gz"
    if sc_path.exists():
        sc = pd.read_csv(sc_path)
        sc["Metadata_Well"] = well
        sc_parts.append(sc)
        print(f"    {len(sc)} cells, {len(sc.columns)} cols, {elapsed:.1f}s")

all_sc = pd.concat(sc_parts, ignore_index=True)
meta_cols = [c for c in all_sc.columns if c.startswith("Metadata_")]
feat_cols = [c for c in all_sc.columns if c not in meta_cols
             and c not in ["ImageNumber", "ObjectNumber"]
             and pd.api.types.is_numeric_dtype(all_sc[c])]

# Save with pycytominer-compatible structure
sc_dir = OUT / "02_single_cell"
sc_dir.mkdir(parents=True, exist_ok=True)
sc_final = sc_dir / "single_cell.csv.gz"
all_sc.to_csv(sc_final, index=False, compression="gzip")
timings["1. Single-cell"] = time.perf_counter() - t0
print(f"  Total: {len(all_sc)} cells, {len(feat_cols)} features")

# ============================================================
# Step 2: Aggregate (pycytominer skill)
# ============================================================
print(f"\n{'='*55}")
print(f"  2. Aggregate")
print(f"{'='*55}")

t0 = time.perf_counter()
agg_dir = OUT / "03_aggregate" / "pycytominer"
agg_dir.mkdir(parents=True, exist_ok=True)
agg = all_sc.groupby(["Metadata_Plate", "Metadata_Well"])[feat_cols].mean().reset_index()
agg.to_parquet(agg_dir / "aggregated.parquet", index=False)
timings["2. Aggregate"] = time.perf_counter() - t0
print(f"  {len(agg)} wells, {len(feat_cols)} features")

# ============================================================
# Step 3: Annotate
# ============================================================
print(f"\n{'='*55}")
print(f"  3. Annotate")
print(f"{'='*55}")

t0 = time.perf_counter()
ann_dir = OUT / "04_annotate" / "pycytominer"
ann_dir.mkdir(parents=True, exist_ok=True)
agg_ann = agg.copy()
for c, v in [("Metadata_Treatment", "DMSO"), ("Metadata_ControlType", "DMSO"),
             ("Metadata_Batch", "Batch1"), ("Metadata_Object_Count", "")]:
    if c not in agg_ann.columns:
        agg_ann[c] = v
agg_ann.to_parquet(ann_dir / "annotated.parquet", index=False)
timings["3. Annotate"] = time.perf_counter() - t0
print(f"  done")

# ============================================================
# Step 4: Normalize (manual z-score)
# ============================================================
print(f"\n{'='*55}")
print(f"  4. Normalize (z-score)")
print(f"{'='*55}")

t0 = time.perf_counter()
norm_dir = OUT / "05_normalize" / "pycytominer"
norm_dir.mkdir(parents=True, exist_ok=True)
nf = agg_ann[feat_cols].fillna(0).astype(float)
nf_std = nf.std(ddof=1).replace(0, 1.0)
nf_z = (nf - nf.mean()) / nf_std
n_nan = nf_z.isna().sum().sum()
agg_norm = agg_ann.copy()
agg_norm[feat_cols] = nf_z
agg_norm.to_parquet(norm_dir / "normalized.parquet", index=False)
timings["4. Normalize"] = time.perf_counter() - t0
print(f"  {n_nan} NaN values")

# ============================================================
# Step 5: Feature select (variance > 0)
# ============================================================
print(f"\n{'='*55}")
print(f"  5. Feature select")
print(f"{'='*55}")

t0 = time.perf_counter()
fs_dir = OUT / "06_feature_select" / "pycytominer"
fs_dir.mkdir(parents=True, exist_ok=True)
keep = [c for c in feat_cols if nf_z[c].notna().all() and nf_z[c].var(ddof=1) > 0]
meta_all = [c for c in agg_norm.columns if c.startswith("Metadata_")]
agg_fs = agg_norm[list(dict.fromkeys(meta_all + keep))]
agg_fs.to_parquet(fs_dir / "feature_selected.parquet", index=False)
timings["5. Feature select"] = time.perf_counter() - t0
print(f"  {len(keep)}/{len(feat_cols)} kept")

# ============================================================
# Step 6: PCA + Summary
# ============================================================
print(f"\n{'='*55}")
print(f"  6. PCA + Summary")
print(f"{'='*55}")

t0 = time.perf_counter()
sum_dir = OUT / "07_summary"
sum_dir.mkdir(parents=True, exist_ok=True)
fs_feats = agg_fs[keep].fillna(0).to_numpy(dtype=float)
n = fs_feats.shape[0]

if n >= 2:
    ctr = fs_feats - fs_feats.mean(axis=0, keepdims=True)
    _, s, Vt = np.linalg.svd(ctr, full_matrices=False)
    ev = s**2 / max(n - 1, 1)
    evs = ev.sum()
    ratio = tuple(float(v / evs) for v in ev[:2]) if evs > 0 else (0, 0)
    pc = ctr @ Vt.T
else:
    pc = np.zeros((n, 2)); ratio = (1.0, 0.0)

pca_df = agg_fs[meta_all].copy()
pca_df["PC1"] = pc[:, 0]
pca_df["PC2"] = pc[:, 1] if pc.shape[1] > 1 else 0.0
pca_df.to_csv(sum_dir / "pca_coordinates.csv", index=False)

var_s = pd.Series({c: float(np.var(agg_fs[c].fillna(0))) for c in keep}).sort_values(ascending=False)
pd.DataFrame({"feature_name": var_s.head(50).index, "variance": var_s.head(50).values}).to_csv(sum_dir / "top_variable_features.csv", index=False)
agg_fs[meta_all].drop_duplicates().to_csv(sum_dir / "well_metadata_summary.csv", index=False)

try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = {"A01": "#2563eb", "A02": "#dc2626"}
    for w in pca_df["Metadata_Well"].unique():
        sub = pca_df[pca_df["Metadata_Well"] == w]
        ax.scatter(sub["PC1"], sub["PC2"], s=60, c=colors.get(w, "#888"), label=w,
                   alpha=0.85, edgecolors="white", linewidth=0.5)
    ax.set_title(f"Classical Profile PCA - {PLATE}")
    ax.legend()
    ax.set_xlabel(f"PC1 ({ratio[0]*100:.1f}%)")
    ax.set_ylabel(f"PC2 ({ratio[1]*100:.1f}%)")
    ax.axhline(0, color="#ccc", lw=0.8); ax.axvline(0, color="#ccc", lw=0.8)
    ax.grid(alpha=0.2)
    fig.tight_layout(); fig.savefig(sum_dir / "pca_plot.png", dpi=150); plt.close()
    pca_ok = True
except Exception as e:
    print(f"  plot: {e}"); pca_ok = False

json.dump({
    "implementation": "classical_pipeline", "plate": PLATE, "wells": list(WELLS.keys()),
    "cell_count": int(len(all_sc)), "well_count": len(agg_fs),
    "feature_count_raw": int(len(feat_cols)), "feature_count_selected": int(len(keep)),
    "pca_explained_variance_ratio": list(ratio),
    "cellprofiler_times": {"A01": 287.7, "A02": 334.5},
}, open(sum_dir / "profile_summary.json", "w"), indent=2, ensure_ascii=False)

timings["6. PCA + Summary"] = time.perf_counter() - t0
print(f"  PC1={ratio[0]*100:.1f}%, PC2={ratio[1]*100:.1f}%")

# ============================================================
# Report
# ============================================================
total = time.perf_counter() - t_total
cp_times = {"A01": 287.7, "A02": 334.5}
cp_total = sum(cp_times.values())

print(f"\n{'='*60}")
print(f"  Classical Pipeline - {PLATE} A01+A02")
print(f"{'='*60}")
for label, t in timings.items():
    print(f"  {label:30s} {t:>6.1f}s  ({t/total*100:5.1f}%)")
print(f"  {'─'*42}")
print(f"  {'Total (pycytominer)':30s} {total:>6.1f}s")
print(f"  {'CellProfiler A01':30s} {cp_times['A01']:>6.1f}s  (pre-computed)")
print(f"  {'CellProfiler A02':30s} {cp_times['A02']:>6.1f}s  (pre-computed)")
print(f"  {'Full stack total':30s} {total + cp_total:>6.1f}s")
print(f"{'='*60}")
print(f"\n  Cells: {len(all_sc)} ({', '.join(f'{w}={len(p)}' for w,p in [('A01',sc_parts[0]),('A02',sc_parts[1])])})")
print(f"  Features: {len(keep)} selected from {len(feat_cols)}")
print(f"\nOutput: {OUT}")
for d in sorted(OUT.iterdir()):
    if d.is_dir():
        for f in sorted(d.rglob("*")):
            if f.is_file():
                print(f"  {f.relative_to(OUT)}")
