"""Full CellPainting classical pipeline — BR00117035 A01+A02."""
import time, json, os, shutil, subprocess
from pathlib import Path
import pandas as pd, numpy as np

BASE     = Path(r"D:\CellPainting-Claw-main2\CellPainting-Claw-main")
PYTHON   = Path(r"D:\MINICONDA\envs\cellpainting-claw\python.exe")
CP_SRC   = Path(r"D:\CellPainting-Claw-main2\CellProfiler-main\CellProfiler-main\src")
CP_PP    = os.pathsep.join([str(CP_SRC/"frontend"), str(CP_SRC/"subpackages/core"), str(CP_SRC/"subpackages/library")])
PIPELINE = BASE / "demo/backend/profiling_backend/cellprofiler/CPJUMP1_analysis_smoketest.cppipe"
REF_DIR  = BASE / "demo/workspace/reference_data/BR00117035"
OUT_BASE = BASE / "demo/workspace/outputs"
PLATE    = "BR00117035"

timings = {}
t_total = time.perf_counter()

# ============================================================
# 1. CellProfiler: A01 reuse, A02 run fresh
# ============================================================
cp_dirs = {}
cp_dirs["A01"] = OUT_BASE / "BR00117035_optimized"
print(f"A01: reuse {cp_dirs['A01']}  (pre-computed, 287.7s)")

well = "A02"
well_dir = REF_DIR / well
tiff_files = sorted(well_dir.glob("*.tiff"))
row = {"Metadata_Plate": PLATE, "Metadata_Well": well, "Metadata_Site": "1"}
for tag, ch_idx in [("OrigMito",1),("OrigAGP",2),("OrigRNA",3),("OrigER",4),
                      ("OrigDNA",5),("OrigBrightfield",8),("OrigHighZBF",6),("OrigLowZBF",7)]:
    pattern = f"ch{ch_idx}sk1fk1fl1"
    match = [f for f in tiff_files if pattern in f.name]
    row[f"FileName_{tag}"] = match[0].name if match else ""
    row[f"PathName_{tag}"] = str(well_dir)
illum_dir = REF_DIR / "illumination"
for tag, chan in [("DNA","DNA"),("Mito","Mito"),("AGP","AGP"),("RNA","RNA"),
                   ("ER","ER"),("Brightfield","Brightfield"),("HighZBF","HighZBF"),("LowZBF","LowZBF")]:
    row[f"FileName_Illum{chan}"] = f"Illum{chan}.npy"
    row[f"PathName_Illum{chan}"] = str(illum_dir)

load_csv = OUT_BASE / f"load_data_{well}.csv"
pd.DataFrame([row]).to_csv(load_csv, index=False)

cp_out = OUT_BASE / f"{PLATE}_{well}_cp"
if cp_out.exists(): shutil.rmtree(cp_out)
cp_out.mkdir(parents=True)

print(f"A02: running CellProfiler...")
t0 = time.perf_counter()
cmd = [str(PYTHON), "-m", "cellprofiler", "-c", "-r",
       "-p", str(PIPELINE), "-o", str(cp_out), "-i", str(well_dir),
       "--data-file", str(load_csv),
       "-e", "imageio_reader_v3", "imageio_reader", "ngff_reader", "gcs_reader"]
env = os.environ.copy()
env["PYTHONPATH"] = CP_PP + os.pathsep + env.get("PYTHONPATH", "")
result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env)
cp_a02 = time.perf_counter() - t0
print(f"A02 done: {cp_a02:.1f}s (exit {result.returncode})")
cp_dirs["A02"] = cp_out
timings["1. CellProfiler A02"] = cp_a02

# ============================================================
# 2. Build single-cell
# ============================================================
t0 = time.perf_counter()
all_sc = []
for well, cp_dir in cp_dirs.items():
    cells  = pd.read_csv(cp_dir / "Cells.csv")
    nuclei = pd.read_csv(cp_dir / "Nuclei.csv")
    cyto   = pd.read_csv(cp_dir / "Cytoplasm.csv")
    image  = pd.read_csv(cp_dir / "Image.csv")
    sc = cells.merge(nuclei, on=["ImageNumber","ObjectNumber"], suffixes=("","_Nuclei"))
    sc = sc.merge(cyto, on=["ImageNumber","ObjectNumber"], suffixes=("","_Cytoplasm"))
    sc = sc.merge(image, on="ImageNumber", suffixes=("","_Image"))
    for c,v in [("Metadata_Plate",PLATE),("Metadata_Well",well),("Metadata_Site","1")]:
        if c in sc.columns: sc[c] = v
        else: sc.insert(0, c, v)
    all_sc.append(sc)
    print(f"  {well}: {len(sc)} cells, {len(sc.columns)} cols")

sc_all = pd.concat(all_sc, ignore_index=True)
meta_cols = [c for c in sc_all.columns if c.startswith("Metadata_")]
exclude   = meta_cols + ["ImageNumber","ObjectNumber"]
num_cols  = [c for c in sc_all.columns if c not in exclude and pd.api.types.is_numeric_dtype(sc_all[c])]

OUT_DIR = OUT_BASE / "classical_pipeline"
if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
OUT_DIR.mkdir(parents=True)
sc_all[meta_cols+num_cols].to_csv(OUT_DIR/"single_cell.csv.gz", index=False, compression="gzip")
timings["2. Single-cell table"] = time.perf_counter() - t0
print(f"  Total: {len(sc_all)} cells, {len(num_cols)} numeric features")

# ============================================================
# 3. Aggregate
# ============================================================
t0 = time.perf_counter()
agg = sc_all.groupby(["Metadata_Plate","Metadata_Well"])[num_cols].mean().reset_index()
agg.to_parquet(OUT_DIR/"aggregated.parquet", index=False)
timings["3. Aggregate"] = time.perf_counter() - t0
print(f"  Aggregate: {len(agg)} wells")

# ============================================================
# 4. Annotate
# ============================================================
t0 = time.perf_counter()
for c,v in [("Metadata_Treatment","DMSO"),("Metadata_ControlType","negative_control")]:
    if c not in agg.columns: agg.insert(2, c, v)
agg.to_parquet(OUT_DIR/"annotated.parquet", index=False)
timings["4. Annotate"] = time.perf_counter() - t0

# ============================================================
# 5. Normalize
# ============================================================
t0 = time.perf_counter()
nf = agg[num_cols].fillna(0).astype(float)
nf = (nf - nf.mean()) / nf.std(ddof=1).clip(lower=1e-12)
agg_norm = agg.copy(); agg_norm[num_cols] = nf
agg_norm.to_parquet(OUT_DIR/"normalized.parquet", index=False)
timings["5. Normalize"] = time.perf_counter() - t0

# ============================================================
# 6. Feature select
# ============================================================
t0 = time.perf_counter()
keep = [c for c in num_cols if nf[c].var(ddof=1) > 0]
meta_all = [c for c in agg_norm.columns if c.startswith("Metadata_")]
agg_fs = agg_norm[list(dict.fromkeys(meta_all+keep))]
agg_fs.to_parquet(OUT_DIR/"feature_selected.parquet", index=False)
timings["6. Feature select"] = time.perf_counter() - t0
print(f"  Feature select: {len(keep)}/{len(num_cols)} kept")

# ============================================================
# 7. PCA + Summary
# ============================================================
t0 = time.perf_counter()
fs_feats = agg_fs[keep].fillna(0).to_numpy(dtype=float)
n = fs_feats.shape[0]
if n >= 2:
    ctr = fs_feats - fs_feats.mean(axis=0, keepdims=True)
    _, s, Vt = np.linalg.svd(ctr, full_matrices=False)
    ev = s**2/max(n-1,1); evs = ev.sum()
    ratio = tuple(float(v/evs) for v in ev[:2]) if evs>0 else (0,0)
    pc = ctr @ Vt.T
else:
    pc = np.zeros((n,2)); ratio = (1.0,0.0)

pca_df = agg_fs[meta_all].copy()
pca_df["PC1"] = pc[:,0]; pca_df["PC2"] = pc[:,1] if pc.shape[1]>1 else 0.0
pca_df.to_csv(OUT_DIR/"pca_coordinates.csv", index=False)

var_s = pd.Series({c: float(np.var(agg_fs[c].fillna(0))) for c in keep}).sort_values(ascending=False)
pd.DataFrame({"feature_name":var_s.head(50).index,"variance":var_s.head(50).values}).to_csv(OUT_DIR/"top_variable_features.csv", index=False)
agg_fs[meta_all].drop_duplicates().to_csv(OUT_DIR/"well_metadata_summary.csv", index=False)

try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(7,5))
    colors={"A01":"#2563eb","A02":"#dc2626"}
    for w in pca_df["Metadata_Well"].unique():
        sub=pca_df[pca_df["Metadata_Well"]==w]
        ax.scatter(sub["PC1"],sub["PC2"],s=60,c=colors.get(w,"#888"),label=w,alpha=0.85,edgecolors="white",linewidth=0.5)
    ax.set_title(f"Classical Profile PCA - {PLATE}"); ax.legend()
    ax.set_xlabel(f"PC1 ({ratio[0]*100:.1f}%)"); ax.set_ylabel(f"PC2 ({ratio[1]*100:.1f}%)")
    ax.axhline(0,color="#ccc",lw=0.8); ax.axvline(0,color="#ccc",lw=0.8); ax.grid(alpha=0.2)
    fig.tight_layout(); fig.savefig(OUT_DIR/"pca_plot.png",dpi=150); plt.close()
    pca_ok = True
except Exception as e:
    print(f"  plot: {e}"); pca_ok = False

json.dump({
    "implementation":"classical_pipeline", "plate":PLATE, "wells":["A01","A02"],
    "cell_count":int(len(sc_all)), "well_count":int(len(agg_fs)),
    "feature_count_raw":int(len(num_cols)), "feature_count_selected":int(len(keep)),
    "pca_explained_variance_ratio":list(ratio),
    "cellprofiler_a01_seconds": 287.7, "cellprofiler_a02_seconds": cp_a02,
}, open(OUT_DIR/"profile_summary.json","w"), indent=2, ensure_ascii=False)

timings["7. PCA + Summary"] = time.perf_counter() - t0
print(f"  PCA: PC1={ratio[0]*100:.1f}%, PC2={ratio[1]*100:.1f}%")

# ============================================================
total = time.perf_counter() - t_total
print(f"\n{'='*55}")
print(f"  CellPainting Full Pipeline - {PLATE} A01+A02")
print(f"{'='*55}")
for label, t in timings.items():
    print(f"  {label:30s} {t:>6.1f}s  ({t/total*100:5.1f}%)")
print(f"  {'-'*42}")
print(f"  {'CellProfiler A01 (reuse)':30s} {287.7:>6.1f}s  (pre-computed)")
print(f"  {'Full stack total':30s} {total+287.7:>6.1f}s")
print(f"{'='*55}")
print(f"\nOutput: {OUT_DIR}")
for f in sorted(OUT_DIR.iterdir()):
    if f.is_file():
        print(f"  {f.name:35s} {f.stat().st_size:>10,} bytes")
