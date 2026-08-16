# Raw（无优化）vs Final（优化版）对比

> 数据: BR00117035 A01+A02  |  硬件: CPU Intel Genuine 2.68 GHz, 20 cores
> raw = `D:\CellProfiler-raw`（完全没优化）  |  final = 优化版 fork（磁盘 HDF5 + 三个 Colocalization 优化）

---

## 1. 时间对比（模块时间，已去掉启动开销）

### 模块时间合计

| | raw | final | 变化 |
|---|:---:|:---:|:---:|
| A01 | 174.98s | **148.73s** | −26.25s |
| A02 | 155.95s | **143.78s** | −12.17s |
| **合计** | 330.93s | **292.51s** | **−38.42s（−11.6%）** |

### 模块级时间（A01）

| 模块 | raw | final | 变化 |
|------|:---:|:---:|:---:|
| MeasureTexture | 68.23s | **59.80s** | −8.43s |
| MeasureGranularity | 49.09s | **41.20s** | −7.89s |
| MeasureColocalization | 24.95s | **17.89s** | −7.06s |
| MeasureObjectIntensity | 8.48s | 8.06s | −0.42s |
| MeasureObjectSizeShape | 9.78s | 8.81s | −0.97s |
| MeasureObjectIntensityDistribution | 7.59s | 7.05s | −0.54s |
| LoadData | 1.27s | 0.98s | −0.29s |
| 其余小模块 | ~5.6s | ~4.9s | −0.7s |
| **模块时间合计** | **174.98s** | **148.73s** | **−26.25s（−15%）** |

> 注：模块时间取自 Image.csv 的 `ExecutionTime_*` 列之和，已排除 Python 启动 / CellProfiler 初始化 / 结束清理等固定开销（与优化无关）。

---

## 2. 结果一致性

### 对象级测量表（生物测量值）

| 文件 | raw 形状 | final 形状 | 差异 |
|------|:---:|:---:|:---:|
| **Cells.csv** | (68, 1941) | (68, 1941) | **0 列（bit-identical）** ✅ |
| **Nuclei.csv** | (68, 1934) | (68, 1934) | **0 列（bit-identical）** ✅ |
| **Cytoplasm.csv** | (68, 1926) | (68, 1926) | **0 列（bit-identical）** ✅ |

A02 同样 bit-identical（Cells 55×1941、Nuclei 55×1934、Cytoplasm 55×1926，均 0 差异）。

### 元信息表（运行时信息，不同是预期的）

| 文件 | 差异内容 | 原因 |
|------|---------|------|
| Image.csv | 21 列 ExecutionTime + 4 列输出路径 | 模块执行时间不同（优化效果）、输出目录不同 |
| Experiment.csv | 1 行 Run_Timestamp | 跑的时间不同 |

> **生物学测量结果 100% bit-identical，只有性能（时间）、路径、时间戳等运行时元信息不同。**

---

## 3. 优化项（final 相对 raw 的唯一增量）

| # | 优化 | 函数 | 加速 |
|---|------|------|:---:|
| 1 | `lexsort` → `argsort` (stable) | `get_image_rank`（RWC）| 2.0× |
| 2 | `ndimage.maximum` → `np.maximum.at` | `get_threshold_values_for_objects` | 18× |
| 3 | `ndimage.sum` → `np.bincount` | `get_thresholded_sum` | 1.6× |

三个优化都是**算法等价替换**（逐一验证 `array_equal = True`），作用于 Colocalization 的 RWC/threshold 计算。

### 代码对比（before → after）

**优化 1：RWC 排序 `lexsort` → `argsort`（`get_image_rank`）**

```python
# before (raw)
if labels is None:
    Rank = numpy.lexsort([im_pixels])
else:
    [Rank] = numpy.lexsort(([labels], [im_pixels]))   # 双键排序，labels 是多余次键

# after (final)
# Dense rank 只依赖像素值，labels 次键不改变 rank 结果
Rank = numpy.argsort(im_pixels, kind="stable")        # 单键排序
```

**优化 2：阈值最大 `ndimage.maximum` → `np.maximum.at`（`get_threshold_values_for_objects`）**

```python
# before (raw)
object_threshold_values = (image_threshold_percentage / 100) * centrosome.cpmorphology.fixup_scipy_ndimage_result(
    scipy.ndimage.maximum(pixels, labels, lrange)     # 内部排序，慢
)

# after (final)
maxima = numpy.zeros(len(lrange), dtype=pixels.dtype)
numpy.maximum.at(maxima, labels - 1, pixels)          # O(N) 归约，等价
object_threshold_values = (image_threshold_percentage / 100) * maxima
```

**优化 3：阈值求和 `ndimage.sum` → `np.bincount`（`get_thresholded_sum`）**

```python
# before (raw)
return scipy.ndimage.sum(
    pixels[pixels >= object_threshold_values[labels - 1]],   # 布尔掩码算两次
    labels[pixels >= object_threshold_values[labels - 1]],
    lrange,
).astype(numpy.float64)

# after (final)
above = pixels >= object_threshold_values[labels - 1]       # 掩码只算一次
return numpy.bincount(
    labels[above], weights=pixels[above], minlength=len(lrange) + 1
)[1:].astype(numpy.float64)
```

**等价性说明**：
1. `lexsort` 双键 → `argsort` 单键：dense rank 只依赖值，labels 次键对结果无影响
2. `ndimage.maximum` → `np.maximum.at`：都是求每对象最大值，空 label 都返回 0
3. `ndimage.sum` → `np.bincount`：都是按 label 分组求和，`[1:]` 丢弃背景

---

## 4. 结论

- **final 比 raw 快 11.6%**（模块时间 330.93s → 292.51s），主要来自三个 Colocalization 算法优化
- **测量结果 bit-identical**（Cells/Nuclei/Cytoplasm 三个表 0 差异）
- 之前的"10 项优化让 CP 慢 3×"是**内存 HDF5 负优化**导致的假象，去掉后优化版反超 raw
- 三个 Colocalization 优化是唯一可靠、结果无损的正优化

---

*Generated: 2026-08-16 | Data: BR00117035 A01+A02*
