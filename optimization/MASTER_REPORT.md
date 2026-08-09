# CellPainting-Claw Optimization Report

> Date: 2026-08-07  |  Data: BR00117035 A01+A02  
> Hardware: CPU Intel Genuine 2.68 GHz, 20 cores, AVX2 + oneDNN

---

## 1. Overview

```
BR00117035 Microscopy Images (1080x1080, 8ch TIFF)
    │
    ├──→ CellProfiler (optimized 4.2.8)  → Classical features  →  PCA
    │      622.2s                          12,416 features
    │
    └──→ DeepProfiler (pipeline optimized) → Deep features      →  Collect
           24.1s                              672 features
```

---

## 2. CellProfiler — Segmentation + Classical Pipeline

### 2.1 Optimization: Before vs After

| | Before (4.2.6) | After (4.2.8) | Speedup |
|---|:---:|:---:|:---:|
| **Total time** | 594.7s | **287.7s** | **2.1×** |
| Common modules | 428.9s | 278.0s | 1.5× |
| Cells detected | 68 | 68 | identical |
| Output | 5 CSVs | 5 CSVs | identical |

### 2.2 Full Classical Pipeline: A01+A02

| Step | Time | Share |
|------|:---:|:---:|
| CellProfiler A01 | 287.7s | 44.3% |
| CellProfiler A02 | 334.5s | 51.5% |
| Single-cell table | 9.8s | 1.5% |
| Aggregate | 2.4s | 0.4% |
| Annotate | 1.7s | 0.3% |
| Normalize | 6.4s | 1.0% |
| Feature select | 3.1s | 0.5% |
| PCA + Summary | 3.2s | 0.5% |
| **Total** | **648.8s** | **100%** |

Output: A01 68 cells + A02 55 cells = 123 total, 12,263 selected features

---

## 3. DeepProfiler — Feature Extraction

### 3.1 Optimization: Before vs After

| | Before | After | Delta |
|---|:---:|:---:|:---:|
| **Total time** | 26.3s | **24.1s** | **−8%** |
| Profile | 25.0s | **22.8s** | −9% |
| Collect | 1.2s | **1.0s** | −17% |
| **Features** | (68, 672) | (68, 672) | **identical (4.77e-7)** |
| Invocation | CLI subprocess | direct `import` | — |

### 3.2 Full DeepProfiler Pipeline: A01+A02

| Step | Time | Share |
|------|:---:|:---:|
| Export | 0.175s | 0.7% |
| Build | 0.125s | 0.5% |
| Checkpoint | 0.021s | 0.1% |
| **Profile** | **22.803s** | **94.6%** |
| Collect (NPZ→tables) | 0.977s | 4.1% |
| **Total** | **24.1s** | **100%** |

Output: A01 68 cells × 672-d, A02 55 cells × 672-d (18 files)

---

## 4. Full Stack Timing

| Stage | CellProfiler | DeepProfiler |
|-------|:---:|:---:|
| Setup | — | 0.3s |
| Processing | 622.2s | 22.8s |
| Collect/Tables | — | 1.0s |
| pycytominer | 26.6s | — |
| **Total** | **648.8s** | **24.1s** |
| **Per-well marginal** | ~310s | ~0.2s (after cold start) |

---

## 5. Result Consistency

### CellProfiler: 2.1× speedup, identical output

| | Before | After |
|---|:---:|:---:|
| Nuclei count | 68 | 68 |
| Output CSVs | 5 files | 5 files |
| All measurements | identical | identical |

### DeepProfiler: 8% faster, features identical to float32 precision

| | Before | After |
|---|:---:|:---:|
| Cell count | 68 | 68 |
| Locations | bit-identical | bit-identical |
| Features (max diff) | — | 4.77×10⁻⁷ |
| NaN rate | 0% | 0% |

---

## 6. Scripts

```
optimization/
├── MASTER_REPORT.md
├── optimization_notebook.ipynb
├── cellprofiler/
│   ├── README.md                     ← 10-optimization report
│   ├── TIMING_REPORT.md              ← Detailed timing
│   ├── BEFORE_AFTER_COMPARISON.md    ← 594.7s→287.7s, 2.1×
│   ├── run.py                        ← Benchmark script
│   └── run_full.py                   ← Full classical pipeline
└── deepprofiler/
    ├── README.md                     ← 7-optimization report
    ├── BEFORE_AFTER_COMPARISON.md    ← 26.3s→24.1s, features identical
    ├── run.py                        ← Run command
    ├── run.bat                       ← Double-click run
    └── pipeline.py                   ← Full DP pipeline
```

---

*Generated: 2026-08-07 | Data: BR00117035 A01+A02*
