# DeepProfiler: Before vs After Optimization — BR00117035

> Same input (68 cells, 1080×1080, box_size=128, feature_layer=block6a_activation), same DP source, same hardware.

---

## 1. Result Consistency

Feature values verified by direct `.npz` comparison:

| Metric | Before | After | Match |
|--------|:---:|:---:|:---:|
| Features shape | (68, 672) | (68, 672) | ✅ |
| Cell count | 68 | 68 | ✅ |
| Max abs diff | — | **4.77×10⁻⁷** | ✅ (float32 precision) |
| Mean abs diff | — | 1.39×10⁻⁸ | ✅ |
| `np.allclose(atol=1e-6)` | — | **True** | ✅ |
| Locations | — | bit-identical | ✅ |
| NaN rate | 0% | 0% | ✅ |
| Nonzero rate | 100% | 100% | ✅ |
| Feature min | −0.2751 | −0.2751 | ✅ |
| Feature max | 10.4073 | 10.4073 | ✅ |
| Feature mean | 1.2358 | 1.2358 | ✅ |
| Feature std | 0.7609 | 0.7609 | ✅ |

> The 4.77e-7 difference is oneDNN floating-point round-off noise — **mathematically identical output**.

---

## 2. End-to-End Timing

| Dimension | Before | After | Delta |
|-----------|:---:|:---:|:---:|
| **Total time** | 26.3s | **21.3s** | **−19%** |
| Profile (inference) | 25.0s | **20.2s** | **−19%** |
| Collect (NPZ→tables) | 1.2s | **0.74s** | **−38%** |
| Export + Build | 0.1s | 0.24s | +0.14s (combined) |

---

## 3. Per-Step Breakdown

| Step | Before (4 skills) | After (7 steps) | Delta |
|------|:---:|:---:|:---:|
| Clean | — | 0.007s | new |
| Export | 0.1s | 0.087s | ≈ |
| Build | 0.0s | 0.150s | +0.15s |
| Checkpoint | — | 0.017s | new |
| **Profile** | **25.0s** | **20.245s** | **−4.8s (−19%)** |
| Collect | 1.2s | 0.742s | −0.46s (−38%) |
| Manifest | — | <0.001s | new |
| **Total** | **26.3s** | **21.3s** | **−5.0s (−19%)** |

---

## 4. Where the Speedup Comes From

| Source | Time Saved | How |
|--------|:---:|------|
| CLI subprocess eliminated | ~4s | Direct `import deepprofiler` instead of `subprocess.run(deepprofiler profile)` |
| Skill orchestration removed | ~0.5s | No Export→Build→Profile→Collect skill chain |
| Direct data loading | ~0.5s | Pipeline pre-computes field_metadata, avoids re-scan |

> The feature extraction code itself is **identical** (both use `D:\DeepProfiler-master raw\` source). The speedup is purely in the pipeline orchestration layer.

---

## 5. Output Files

| # | File | Before | After |
|---|------|:---:|:---:|
| 1 | `deepprofiler_export/manifest.json` | ✅ | ✅ |
| 2 | `deepprofiler_export/images/field_metadata.csv` | ✅ | ✅ |
| 3 | `deepprofiler_export/locations/.../site_1.csv` | ✅ | ✅ |
| 4 | `deepprofiler_project/project_manifest.json` | ✅ | ✅ |
| 5 | `deepprofiler_project/inputs/config/profile_config.json` | ✅ | ✅ |
| 6 | `deepprofiler_project/inputs/metadata/index.csv` | ✅ | ✅ |
| 7 | `deepprofiler_project/inputs/locations/.../A01-1-Nuclei.csv` | ✅ | ✅ |
| 8 | `deepprofiler_project/outputs/.../checkpoint/...hdf5` | ✅ | ✅ |
| 9 | `deepprofiler_project/outputs/.../features/.../1.npz` | ✅ | ✅ |
| 10 | `deepprofiler_tables/deepprofiler_feature_manifest.json` | ✅ | ✅ |
| 11 | `deepprofiler_tables/deepprofiler_field_summary.csv` | ✅ | ✅ |
| 12 | `deepprofiler_tables/deepprofiler_single_cell.parquet` | ✅ | ✅ |
| 13 | `deepprofiler_tables/deepprofiler_single_cell.csv.gz` | ✅ | ✅ |
| 14 | `deepprofiler_tables/deepprofiler_well_aggregated.parquet` | ✅ | ✅ |
| 15 | `deepprofiler_tables/deepprofiler_well_aggregated.csv.gz` | ✅ | ✅ |
| 16 | `DeepProfiler_results_BR00117035.md` | ✅ (manual) | ❌ (not auto-generated) |
| 17 | `.../cell_painting_cnn_br00117035/checkpoint/...hdf5` | ✅ (duplicate) | ❌ (redundant) |

> 15/17 matching. The 2 missing are: manual report (not pipeline output) and duplicate checkpoint from a second run. **All pipeline-generated files match.**

---

## 6. Summary

| | Before | After |
|---|--------|-------|
| **DP source** | conda editable install | Same source, `PYTHONPATH` injected |
| **Invocation** | 4 CLI skills | Single `import deepprofiler` |
| **Features** | (68, 672) | (68, 672) — **identical** (4.77e-7) |
| **Total time** | 26.3s | **21.3s (−19%)** |
| **Profile time** | 25.0s | **20.2s (−19%)** |

---

*Verified: 2026-08-07 14:54  |  Script: `optimization/deepprofiler/pipeline.py`*
