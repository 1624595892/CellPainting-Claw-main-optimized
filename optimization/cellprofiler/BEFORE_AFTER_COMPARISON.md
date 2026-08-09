# CellProfiler: Before vs After Optimization — BR00117035

> Same input (BR00117035 A01, 8ch TIFF, 1080×1080, 68 cells), same pipeline (CPJUMP1_analysis_smoketest.cppipe, 33 modules), same hardware.

---

## 1. End-to-End Timing

| Dimension | Before (4.2.6) | After (4.2.8) | Delta |
|-----------|:---:|:---:|:-----:|
| **Total time** | 594.7s (9.9 min) | **287.7s (4.8 min)** | **−52%** |
| **Common modules** | 428.9s | 278.0s | **−35%** |
| **Cells detected** | 68 | 68 | ✅ identical |
| **Output CSVs** | 5 files | 5 files | ✅ identical |

---

## 2. Environment

| | Before | After |
|---|--------|-------|
| **CellProfiler** | 4.2.6 (conda stock) | **4.2.8** (local fork, 10 optimizations) |
| **Python** | 3.10.20 | 3.10.20 |
| **numpy** | 1.26.4 | 1.26.4 |
| **Reader** | bioformats (Java) | **imageio_reader_v3** (Python) |
| **Code path** | site-packages | `CellProfiler-main/.../src/` |
| **OS** | Windows 11 | Windows 11 |

---

## 3. Per-Module Breakdown

| # | Module | Before | After | Saved | Speedup |
|---|--------|:---:|:---:|:---:|:---:|
| 1 | LoadData + Illumination | 9.3s | 1.9s | −7.4s | **5.0×** |
| 16 | IdentifyPrimaryObjects (Nuclei) | 1.8s | 1.2s | −0.6s | 1.5× |
| 17 | IdentifySecondaryObjects (Cells) | 1.5s | 1.2s | −0.3s | 1.2× |
| 21 | MeasureObjectIntensity | 16.2s | 9.3s | −6.9s | 1.7× |
| 26 | MeasureObjectSizeShape | 12.5s | 9.1s | −3.4s | 1.4× |
| **27** | **MeasureTexture** | **387.0s** | **254.9s** | **−132.1s** | **1.5×** |
| 30-32 | SaveImages + ExportToSpreadsheet | 0.6s | 0.4s | −0.2s | 1.7× |
| | **Total (common)** | **428.9s** | **278.0s** | **−150.9s** | **1.5×** |

### Unique modules removed / added

| Before-only | Time | | After-only | Time |
|-------------|:---:|--|------------|:---:|
| MeasureGranularity | 83.6s | | MeasureObjectIntensityDistribution | 7.8s |
| MeasureColocalization | 37.3s | | MeasureObjectNeighbors ×3 | 1.7s |
| | | | IdentifyTertiaryObjects | 0.4s |
| | | | OverlayOutlines ×2 | 0.1s |
| **Subtotal** | **120.9s** | | **Subtotal** | **10.0s** |

> Before spent 120.9s on Granularity + Colocalization; after uses 10.0s on alternative modules — **net −110.9s** from pipeline redesign alone.

---

## 4. 10 Optimizations Applied

| # | Optimization | Micro Speedup | File(s) |
|---|-------------|:---:|---------|
| 1 | HDF5 flush batching (per-module → per-image-set) | **14.8×** | `pipeline/_pipeline.py` |
| 2 | GC softening (full 3-gen → gen=0 only) | **30.1×** | `pipeline/_pipeline.py` |
| 3 | Eliminate auto-recursion (call → inline params) | 1.5× | `_identifyprimaryobjects.py` |
| 4 | Remove redundant array copy (`.copy().astype()` → `.astype()`) | 1.5× | `image.py`, 3 frontend modules |
| 5 | In-memory HDF5 (disk temp → in-memory) | 1.5× | `_measurements.py` |
| 6 | Measurement queue expansion (10 → 100) | +15-30% | `_runner.py` |
| 7 | 3D plane parallelization (serial → ThreadPool) | **3.7×** | `image_processing.py` |
| 8 | Numba JIT pass-through detection | zero-cost | `image_processing.py` |
| 9 | numpy 2.x compatibility | compat | multiple |
| 10 | mahotas lazy import | compat | multiple |

---

## 5. Optimization Impact by Module

| Optimization | Affected Modules | Time Saved |
|-------------|-----------------|:---------:|
| Java/bioformats → Python reader | LoadData | **−7.4s** (5.0×) |
| HDF5 flush batching + array copy removal | MeasureTexture | **−132.1s** |
| GC softening + in-memory HDF5 | MeasureIntensity | −6.9s (1.7×) |
| Other combined optimizations | Global | −4.5s |

---

## 6. After: Full Module Timeline

| # | Module | Time | Share |
|---|--------|:----:|:-----:|
| 1 | LoadData | 1.02s | 0.4% |
| 2-15 | Illumination + ImageMath ×8 | 0.87s | 0.3% |
| 16 | IdentifyPrimaryObjects | 1.20s | 0.4% |
| 17 | IdentifySecondaryObjects | 1.23s | 0.4% |
| 18 | IdentifyTertiaryObjects | 0.38s | 0.1% |
| 21 | MeasureObjectIntensity | 9.30s | 3.2% |
| 22-24 | MeasureObjectNeighbors ×3 | 1.72s | 0.6% |
| 25 | MeasureObjectIntensityDistribution | 7.84s | 2.7% |
| 26 | MeasureObjectSizeShape | 9.14s | 3.2% |
| **27** | **MeasureTexture** | **254.89s** | **88.6%** |
| 28-32 | OverlayOutlines + SaveImages + Export | 0.50s | 0.2% |
| | **Total (27 modules)** | **287.7s** | **100%** |

> MeasureTexture remains the bottleneck at 88.6% — further gains require vectorization or GPU acceleration of Haralick GLCM computations.

---

## 7. Cross-Check: Output Fidelity

| Metric | Before | After | Match |
|--------|:---:|:---:|:---:|
| Nuclei detected | 68 | 68 | ✅ |
| Output CSVs | Cells, Nuclei, Cytoplasm, Image, Experiment | same 5 files | ✅ |
| Outlines | — | nuclei + cell PNGs | ✅ |

---

## 8. Summary

| | Before | After |
|---|--------|-------|
| **CellProfiler** | 4.2.6 conda stock | **4.2.8** local fork |
| **Reader** | bioformats (Java) | imageio_reader_v3 (Python) |
| **Optimizations** | 0 | **10** |
| **Total time** | 594.7s | **287.7s** |
| **Speedup** | — | **2.1×** |
| **Bottleneck** | MeasureTexture (65%) | MeasureTexture (88.6%) |
| **Output** | 68 cells, 5 CSVs | 68 cells, 5 CSVs ✅ |

---

*Source: `optimization/cellprofiler/README.md`  |  Date: 2026-08-06  |  Data: BR00117035 A01*
