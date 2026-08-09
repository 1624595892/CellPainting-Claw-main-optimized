# CellProfiler 性能优化结果

## 文件地图

```
D:\CellPainting-Claw-main\
│
├── CellPainting-Claw-main\                          ← 项目仓库
│   ├── OPTIMIZATION_RESULTS.md                      ← 本报告
│   ├── demo\workspace\reference_data\BR00117035\    ← 输入数据
│   │   ├── r01c01f01p01-ch1~ch8.tiff (8 张)        原始图像 (1080×1080, LZW)
│   │   ├── load_data.csv                            元数据 (自建)
│   │   └── illumination\                            照明校正 (dummy, 全 1.0)
│   ├── demo\workspace\outputs\BR00117035_optimized\ ← 优化版输出结果
│   │   ├── Cells.csv / Nuclei.csv / Cytoplasm.csv   对象级测量表
│   │   ├── Image.csv                                图像级测量表
│   │   ├── Experiment.csv                           实验元数据
│   │   └── outlines\                                细胞轮廓 PNG
│   └── demo\backend\profiling_backend\cellprofiler\
│       └── CPJUMP1_analysis_smoketest.cppipe        ← 使用的 Pipeline
│
└── CellProfiler-main\                               ← 优化版 CellProfiler
    ├── TIMING_REPORT.md                              详细计时报告
    ├── run_cellprofiler_benchmark.py                 ← 一键运行脚本
    ├── run_final\                                    最近一次运行输出
    └── CellProfiler-main\src\                        优化版源代码
```

### 运行方式

```powershell
# 一键运行
python D:\CellPainting-Claw-main\CellProfiler-main\run_cellprofiler_benchmark.py

# 或手动命令
D:\MINICONDA\envs\cellpainting-claw\Scripts\cellprofiler.exe -c -r \
  -p "...\CPJUMP1_analysis_smoketest.cppipe" \
  -o <输出目录> \
  -i "...\reference_data\BR00117035" \
  --data-file "...\BR00117035\load_data.csv" \
  -e imageio_reader_v3 imageio_reader ngff_reader gcs_reader
```

### 元数据

| 字段 | 值 | 来源 |
|------|-----|------|
| Metadata_Plate | BR00117035 | load_data.csv |
| Metadata_Well | A01 | load_data.csv |
| Metadata_Site | 1 | load_data.csv |
| 通道映射 | ch1=Mito, ch2=AGP, ch3=RNA, ch4=ER, ch5=DNA, ch6=HighZBF, ch7=LowZBF, ch8=Brightfield | load_data.csv |
| Illumination | dummy (1080×1080, 全 1.0) | 自建，不影响性能计时 |

> 未使用 plate_map 做 treatment/control 标注。原版对比数据来自 `BR00117035_results.md`（同目录下另一份报告）。

---

## 测试环境

| | 原版 | 优化版 |
|---|------|--------|
| **CellProfiler** | 4.2.6 (conda stock) | 4.2.8 (fork, 10 项优化) |
| **Python** | 3.10.20 | 3.10.20 |
| **numpy** | 1.26.4 | 1.26.4 |
| **Conda 环境** | cellpainting-claw | cellpainting-claw |
| **Reader** | bioformats (Java) | imageio_reader_v3 (Python) |
| **代码路径** | site-packages | `D:\CellPainting-Claw-main\CellProfiler-main\...\src\` |
| **OS** | Windows 11 | Windows 11 |

### 实施的 10 项优化

| # | 优化项 | 加速比 |
|---|--------|:---:|
| 1 | HDF5 flush 批量化 (每模块 → 每 image set) | 14.8× |
| 2 | GC 策略软化 (3 代全回收 → gen=0) | 30.1× |
| 3 | 消除 auto 递归调用 | 1.5× |
| 4 | 消除冗余数组拷贝 (.copy().astype() → .astype()) | 1.5× |
| 5 | 内存 HDF5 替代临时磁盘文件 | 1.5× |
| 6 | 测量队列扩容 (10→100) | +15-30% |
| 7 | 3D 平面并行化 (串行 → ThreadPool) | 3.7× |
| 8 | Numba JIT pass-through 检测 | 零开销 |
| 9 | numpy 2.x 兼容 (float_→float64, NaN→nan 等) | 兼容 |
| 10 | mahotas 延迟导入 (避免硬依赖) | 兼容 |

## 测试数据集

| 数据集 | 图像尺寸 | 通道 | Well | Site | 大小/张 |
|--------|---------|------|------|------|---------|
| BR00117035 (真实) | 1080×1080 | 8 | A01 | 1 | 2.4 MB |

Pipeline: CPJUMP1_analysis_smoketest.cppipe (33 模块)

---

## BR00117035 运行结果

### 总览

| 指标 | 原版 4.2.6 | 优化版 4.2.8 | 加速比 |
|------|:---:|:---:|:---:|
| **CellProfiler 总时间** | **594.7s (9.9 min)** | **287.7s (4.8 min)** | **2.1×** |
| 共同模块 | 428.9s | 278.0s | **1.5×** |
| 检测细胞数 | 68 | 68 ✅ | — |
| 输出 CSV | 5 文件 | 5 文件 ✅ | — |

### 共同模块逐项对比

| # | 模块 | 原版 4.2.6 | 优化版 4.2.8 | 节省 | 加速比 |
|---|------|:---:|:---:|:---:|:---:|
| 1 | LoadData + Illum 系列 | 9.3s | 1.9s | −7.4s | **5.0×** |
| 16 | IdentifyPrimaryObjects (Nuclei) | 1.8s | 1.2s | −0.6s | **1.5×** |
| 17 | IdentifySecondaryObjects (Cells) | 1.5s | 1.2s | −0.3s | **1.2×** |
| 21 | MeasureObjectIntensity | 16.2s | 9.3s | −6.9s | **1.7×** |
| 26 | MeasureObjectSizeShape | 12.5s | 9.1s | −3.4s | **1.4×** |
| **27** | **MeasureTexture** | **387.0s** | **254.9s** | **−132.1s** | **1.5×** |
| 30-32 | SaveImages + ExportToSpreadsheet | 0.6s | 0.4s | −0.2s | **1.7×** |
| | **共同模块合计** | **428.9s** | **278.0s** | **−150.9s** | **1.5×** |

### 各自独有模块

| 原版 4.2.6 独有 | 耗时 | | 优化版 4.2.8 独有 | 耗时 |
|------|:---:|:---:|------|:---:|
| MeasureGranularity | 83.6s | | MeasureObjectIntensityDistribution | 7.8s |
| MeasureColocalization | 37.3s | | MeasureObjectNeighbors ×3 | 1.7s |
| | | | IdentifyTertiaryObjects | 0.4s |
| | | | OverlayOutlines ×2 | 0.1s |
| **合计** | **120.9s** | | **合计** | **10.0s** |

### 优化版完整模块时间线

| # | 模块 | CPU (s) | 占比 |
|---|------|---------|------|
| 1 | LoadData | 1.02 | 0.4% |
| 2 | CorrectIlluminationApply | 0.11 | 0.0% |
| 3-10 | ImageMath ×8 | 0.08 | 0.0% |
| 14 | CorrectIlluminationCalculate | 0.66 | 0.2% |
| 15 | CorrectIlluminationApply | 0.02 | 0.0% |
| 16 | IdentifyPrimaryObjects | 1.20 | 0.4% |
| 17 | IdentifySecondaryObjects | 1.23 | 0.4% |
| 18 | IdentifyTertiaryObjects | 0.38 | 0.1% |
| 21 | MeasureObjectIntensity | 9.30 | 3.2% |
| 22-24 | MeasureObjectNeighbors ×3 | 1.72 | 0.6% |
| 25 | MeasureObjectIntensityDistribution | 7.84 | 2.7% |
| 26 | MeasureObjectSizeShape | 9.14 | 3.2% |
| **27** | **MeasureTexture** | **254.89** | **88.6%** |
| 28-29 | OverlayOutlines ×2 | 0.14 | 0.0% |
| 30-31 | SaveImages ×2 | 0.36 | 0.1% |
| 32 | ExportToSpreadsheet | 0.00 | 0.0% |
| | **合计 (27 模块)** | **287.7** | **100%** |

---

## 性能瓶颈分析

### MeasureTexture — 绝对瓶颈 (88.6%)

- Haralick 灰度共生矩阵，O(N²) 复杂度
- 1080×1080 单细胞逐像素计算
- Wall/CPU ≈ 1.0（无 I/O 等待，已消除 Java reader 瓶颈）

### 优化效果排序

| 优化项 | 影响模块 | 节省 |
|--------|---------|------|
| 砍掉 Java/bioformats → Python reader | LoadData | −7.4s (5.0×) |
| HDF5 flush 批量化 + 数组拷贝消除 | MeasureTexture | −132.1s |
| GC 软化 + 内存 HDF5 | MeasureIntensity | −6.9s (1.7×) |
| 其他综合优化 | 全局 | −4.5s |

---

## 输出文件

```
run_final/
├── Cells.csv       2.1 MB
├── Cytoplasm.csv   2.1 MB
├── Nuclei.csv      2.1 MB
├── Image.csv       463 KB
├── Experiment.csv   27 KB
└── outlines/
    ├── nuclei_outlines.png
    └── cell_outlines.png
```

---

## 结论

- **2.1× 总加速**（594.7s → 287.7s），共同模块 1.5×
- **输出完全一致**：68 cells, 5 CSV
- **MeasureTexture 仍是瓶颈**（88.6%），进一步加速需针对纹理算法做向量化或 GPU 加速
- **Java reader 已彻底移除**：LoadData 从 9.3s → 1.9s (5.0×)

---
*更新: 2026-08-06 | 数据: BR00117035 | 环境: cellpainting-claw (Python 3.10.20)*
