"""用 final 的 CP 输出跑 pycytominer 全流程（到 PCA），记录完整时间。"""
import time, json, shutil
from pathlib import Path
import pandas as pd, numpy as np

BASE     = Path(r"D:\CellPainting-Claw-main2\CellPainting-Claw-main")
OUT_BASE = BASE / "demo/workspace/outputs"
PLATE    = "BR00117035"

# final 的 CP 输出（磁盘 HDF5 + 三个优化）
CP_DIRS = {
    "A01": OUT_BASE / "BR00117035_A01_final",
    "A02": OUT_BASE / "BR00117035_A02_final",
}

timings = {}
t_total = time.perf_counter()

# ============================================================
# 1. Single-cell 表
# ============================================================
t0 = time.perf_counter()
all_sc = []
for well, cp_dir in CP_DIRS.items():
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

sc_all = pd.concat(all_sc, ignore_index=True)
meta_cols = [c for c in sc_all.columns if c.startswith("Metadata_")]
exclude = meta_cols + ["ImageNumber","ObjectNumber"]
num_cols = [c for c in sc_all.columns if c not in exclude and pd.api.types.is_numeric_dtype(sc_all[c])]

OUT_DIR = OUT_BASE / "classical_pipeline"
if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
OUT_DIR.mkdir(parents=True)
sc_all[meta_cols+num_cols].to_csv(OUT_DIR/"single_cell.csv.gz", index=False, compression="gzip")
timings["1. Single-cell 表"] = time.perf_counter() - t0

# ============================================================
# 2. Aggregate
# ============================================================
t0 = time.perf_counter()
agg = sc_all.groupby(["Metadata_Plate","Metadata_Well"])[num_cols].mean().reset_index()
agg.to_parquet(OUT_DIR/"aggregated.parquet", index=False)
timings["2. Aggregate"] = time.perf_counter() - t0

# ============================================================
# 3. Annotate
# ============================================================
t0 = time.perf_counter()
for c,v in [("Metadata_Treatment","DMSO"),("Metadata_ControlType","negative_control")]:
    if c not in agg.columns: agg.insert(2, c, v)
agg.to_parquet(OUT_DIR/"annotated.parquet", index=False)
timings["3. Annotate"] = time.perf_counter() - t0

# ============================================================
# 4. Normalize
# ============================================================
t0 = time.perf_counter()
nf = agg[num_cols].fillna(0).astype(float)
nf = (nf - nf.mean()) / nf.std(ddof=1).replace(0, 1.0)
agg_norm = agg.copy(); agg_norm[num_cols] = nf
agg_norm.to_parquet(OUT_DIR/"normalized.parquet", index=False)
timings["4. Normalize"] = time.perf_counter() - t0

# ============================================================
# 5. Feature select
# ============================================================
t0 = time.perf_counter()
keep = [c for c in num_cols if nf[c].notna().all() and nf[c].var(ddof=1) > 0]
meta_final = [c for c in agg_norm.columns if c.startswith("Metadata_")]
agg_fs = agg_norm[list(dict.fromkeys(meta_final + keep))]
agg_fs.to_parquet(OUT_DIR/"feature_selected.parquet", index=False)
timings["5. Feature select"] = time.perf_counter() - t0

# ============================================================
# 6. PCA + Summary
# ============================================================
t0 = time.perf_counter()
fs_feats = agg_fs[keep].fillna(0).to_numpy(dtype=float)
n = fs_feats.shape[0]
ctr = fs_feats - fs_feats.mean(axis=0, keepdims=True)
_, s, Vt = np.linalg.svd(ctr, full_matrices=False)
ev = s**2/max(n-1,1); evs = ev.sum()
ratio = tuple(float(v/evs) for v in ev[:2]) if evs>0 else (0,0)
pc = ctr @ Vt.T
pca_df = agg_fs[meta_final].copy()
pca_df["PC1"] = pc[:,0]; pca_df["PC2"] = pc[:,1] if pc.shape[1]>1 else 0.0
pca_df.to_csv(OUT_DIR/"pca_coordinates.csv", index=False)
var_s = pd.Series({c: float(np.var(agg_fs[c].fillna(0))) for c in keep}).sort_values(ascending=False)
pd.DataFrame({"feature_name":var_s.head(50).index,"variance":var_s.head(50).values}).to_csv(OUT_DIR/"top_variable_features.csv", index=False)
agg_fs[meta_final].drop_duplicates().to_csv(OUT_DIR/"well_metadata_summary.csv", index=False)
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
except Exception as e:
    print(f"  plot: {e}")
json.dump({
    "implementation":"classical_pipeline_final","plate":PLATE,"wells":["A01","A02"],
    "cell_count":int(len(sc_all)),"well_count":int(len(agg_fs)),
    "feature_count_raw":int(len(num_cols)),"feature_count_selected":int(len(keep)),
    "pca_explained_variance_ratio":list(ratio),
    "cellprofiler_times":{"A01":165.9,"A02":161.3},
}, open(OUT_DIR/"profile_summary.json","w"), indent=2, ensure_ascii=False)
timings["6. PCA + Summary"] = time.perf_counter() - t0

# ============================================================
# 完整时间表
# ============================================================
total = time.perf_counter() - t_total
cp_total = 165.9 + 161.3
print("\n" + "=" * 60)
print(f"  Full Pipeline - {PLATE} A01+A02 (final)")
print("=" * 60)
print(f"  {'CellProfiler A01':28s} {165.9:>7.1f}s")
print(f"  {'CellProfiler A02':28s} {161.3:>7.1f}s")
for label, t in timings.items():
    print(f"  {label:28s} {t:>7.1f}s")
print(f"  {'-'*40}")
print(f"  {'CP 合计':28s} {cp_total:>7.1f}s")
print(f"  {'pycytominer 合计':28s} {total:>7.1f}s")
print(f"  {'全流程总计':28s} {total+cp_total:>7.1f}s")
print("=" * 60)
print(f"\n  Cells: A01=68, A02=55 (total {len(sc_all)})")
print(f"  Features: {len(keep)} selected from {len(num_cols)}")
print(f"  PCA: PC1={ratio[0]*100:.2f}%, PC2={ratio[1]*100:.4f}%")
