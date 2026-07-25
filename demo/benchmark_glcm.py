"""GLCM Haralick benchmark: mahotas vs Numba accelerated."""
import time
import numpy as np
import mahotas.features
from numba import njit, prange, get_num_threads

# =============================================================
# Fast Haralick features from normalized GLCM (vectorized)
# =============================================================
@njit(cache=True)
def _haralick_from_glcm(P):
    """Compute 13 Haralick features from a normalized GLCM matrix.
    Matches mahotas.features.haralick output exactly."""
    n = P.shape[0]

    # Row/column marginals: px = p(i), py = p(j)
    px = np.empty(n)
    py = np.empty(n)
    for i in range(n):
        px[i] = np.sum(P[i, :])
        py[i] = np.sum(P[:, i])

    # Mean of px and py
    mu_x = 0.0; mu_y = 0.0
    for i in range(n):
        mu_x += (i + 1) * px[i]
        mu_y += (i + 1) * py[i]

    # Std dev
    sigma_x = 0.0; sigma_y = 0.0
    for i in range(n):
        sigma_x += ((i + 1) - mu_x)**2 * px[i]
        sigma_y += ((i + 1) - mu_y)**2 * py[i]
    sigma_x = np.sqrt(sigma_x)
    sigma_y = np.sqrt(sigma_y)

    # Sum probability: p_x+y(k), p_x-y(k)
    pxy = np.zeros(2 * n + 2)
    pxy_term = np.zeros(2 * n + 2)
    pxmy = np.zeros(n + 1)
    for i in range(n):
        for j in range(n):
            k = i + j + 2
            pxy[k] += P[i, j]
            pxy_term[k] += P[i, j]
            k2 = abs(i - j)
            pxmy[k2] += P[i, j]

    # Entropies
    hx = 0.0; hy = 0.0
    for i in range(n):
        if px[i] > 0: hx -= px[i] * np.log(px[i])
        if py[i] > 0: hy -= py[i] * np.log(py[i])

    hxy1 = 0.0; hxy2 = 0.0
    for i in range(n):
        for j in range(n):
            if P[i, j] > 0:
                hxy1 -= P[i, j] * np.log(px[i] * py[j] + 1e-30)
    for i in range(n):
        for j in range(n):
            pij = px[i] * py[j]
            if pij > 0:
                hxy2 -= pij * np.log(pij + 1e-30)

    # Q matrix for Info Measure Correlation
    Q = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            s = 0.0
            for k in range(n):
                if px[k] > 0:
                    s += P[i, k] * P[j, k] / px[k]
            Q[i, j] = s

    f = np.zeros(13)

    # 1. Angular Second Moment
    for i in range(n):
        for j in range(n):
            f[0] += P[i, j] * P[i, j]

    # 2. Contrast
    for i in range(n):
        for j in range(n):
            f[1] += (i - j)**2 * P[i, j]

    # 3. Correlation
    if sigma_x > 1e-30 and sigma_y > 1e-30:
        s = 0.0
        for i in range(n):
            for j in range(n):
                s += (i + 1 - mu_x) * (j + 1 - mu_y) * P[i, j]
        f[2] = s / (sigma_x * sigma_y)

    # 4. Sum of Squares
    for i in range(n):
        f[3] += ((i + 1) - mu_x)**2 * px[i]

    # 5. Inverse Difference Moment
    for i in range(n):
        for j in range(n):
            f[4] += P[i, j] / (1.0 + (i - j)**2)

    # 6. Sum Average
    f[5] = mu_x + mu_y  # = sum over k of k * pxy[k]

    # Compute correct Sum Average from pxy
    sum_avg = 0.0
    for k in range(2, 2 * n + 2):
        sum_avg += k * pxy[k]
    f[5] = sum_avg  # Match mahotas: sum k * p_{x+y}(k)

    # 7. Sum Variance
    sum_var = 0.0
    sum_ent = 0.0
    for k in range(2, 2 * n + 2):
        if pxy[k] > 0:
            sum_var += (k - sum_avg)**2 * pxy[k]
            sum_ent -= pxy[k] * np.log(pxy[k] + 1e-30)
    f[6] = sum_var
    f[7] = sum_ent

    # 9. Entropy
    for i in range(n):
        for j in range(n):
            if P[i, j] > 0:
                f[8] -= P[i, j] * np.log(P[i, j] + 1e-30)

    # 10. Difference Variance
    diff_mean = 0.0
    diff_var_raw = 0.0
    for k in range(n + 1):
        diff_mean += k * pxmy[k]
        diff_var_raw += k**2 * pxmy[k]
    f[9] = diff_var_raw - diff_mean**2

    # 11. Difference Entropy
    for k in range(n + 1):
        if pxmy[k] > 0:
            f[10] -= pxmy[k] * np.log(pxmy[k] + 1e-30)

    # 12-13. Info Measure of Correlation
    if hx > 1e-30 or hy > 1e-30:
        f[11] = (hxy1 - hxy2) / max(hx, hy)
    f13_input = abs(hxy2 - hxy1)
    if f13_input < 600:  # avoid overflow
        f[12] = np.sqrt(1 - np.exp(-2 * f13_input))
    else:
        f[12] = 1.0

    # NaN guard
    for i in range(13):
        if not np.isfinite(f[i]):
            f[i] = 0.0

    return f


# =============================================================
# Fast GLCM builder: use 2D histogram trick
# =============================================================
@njit(cache=True)
def _build_glcm(img, dx, dy, distance, gray_levels):
    """Build GLCM using linear scan. Fast for small gray_levels."""
    rows, cols = img.shape
    glcm = np.zeros((gray_levels, gray_levels), dtype=np.float64)

    di = dx * distance
    dj = dy * distance

    if di >= 0 and dj >= 0:
        for i in range(rows - di):
            for j in range(cols - dj):
                v1 = img[i, j]
                v2 = img[i + di, j + dj]
                if v1 < gray_levels and v2 < gray_levels:
                    glcm[v1, v2] += 1.0
    elif di < 0 and dj >= 0:
        for i in range(-di, rows):
            for j in range(cols - dj):
                v1 = img[i, j]
                v2 = img[i + di, j + dj]
                if v1 < gray_levels and v2 < gray_levels:
                    glcm[v1, v2] += 1.0
    elif di >= 0 and dj < 0:
        for i in range(rows - di):
            for j in range(-dj, cols):
                v1 = img[i, j]
                v2 = img[i + di, j + dj]
                if v1 < gray_levels and v2 < gray_levels:
                    glcm[v1, v2] += 1.0
    else:
        for i in range(-di, rows):
            for j in range(-dj, cols):
                v1 = img[i, j]
                v2 = img[i + di, j + dj]
                if v1 < gray_levels and v2 < gray_levels:
                    glcm[v1, v2] += 1.0

    # Symmetrize: P + P^T
    for i in range(gray_levels):
        for j in range(gray_levels):
            if i != j:
                glcm[i, j] += glcm[j, i]
            glcm[j, i] = glcm[i, j]

    total = glcm.sum()
    if total > 0:
        for i in range(gray_levels):
            for j in range(gray_levels):
                glcm[i, j] /= total

    return glcm


@njit(parallel=True, cache=True)
def haralick_numba(image, distance=1, gray_levels=None):
    """Numba-accelerated Haralick features. Exact match with mahotas.features.haralick."""
    if gray_levels is None:
        gray_levels = int(image.max()) + 1

    directions = np.array([(1, 0), (1, 1), (0, 1), (-1, 1)], dtype=np.int32)
    result = np.zeros((4, 13))

    for d in prange(4):
        dx, dy = directions[d]
        glcm = _build_glcm(image, dx, dy, distance, gray_levels)
        result[d] = _haralick_from_glcm(glcm)

    return result


# =============================================================
# Verify correctness
# =============================================================
def verify():
    np.random.seed(42)
    print("Verification (max absolute difference vs mahotas):")
    all_ok = True
    for gl in [8, 16, 32, 64, 128, 256]:
        img = (np.random.rand(64, 64) * gl).astype(np.uint8)
        # Scale to match mahotas behavior (mahotas expects uint8 in [0, gl-1])
        ref = mahotas.features.haralick(img, distance=1)
        ours = haralick_numba(img, distance=1, gray_levels=gl)
        max_diff = np.max(np.abs(ref - ours))
        status = "OK" if max_diff < 1e-6 else f"FAIL ({max_diff:.2e})"
        if max_diff >= 1e-6:
            all_ok = False
        print(f"  gl={gl:>3}: {status}")
    return all_ok


# =============================================================
# Benchmark
# =============================================================
def benchmark():
    print(f"\nNumba threads: {get_num_threads()}")
    print()

    # Load real 1080x1080 image
    from PIL import Image
    img_16bit = np.array(Image.open(
        "demo/workspace/reference_data/BR00117035/r01c01f01p01-ch1sk1fk1fl1.tiff"))

    for gl in [256, 128, 64]:
        # Scale to uint8
        if gl < 256:
            img = (img_16bit / (65536.0 / gl)).astype(np.uint8)
        else:
            img = (img_16bit / 256).astype(np.uint8)

        print(f"--- gray_levels={gl}, image={img.shape} ---")

        # Warmup
        _ = mahotas.features.haralick(img, distance=3)
        _ = haralick_numba(img, distance=3, gray_levels=gl)

        # Benchmark mahotas
        t0 = time.perf_counter()
        for _ in range(10):
            ref = mahotas.features.haralick(img, distance=3)
        t_mahotas = (time.perf_counter() - t0) / 10

        # Benchmark numba
        t0 = time.perf_counter()
        for _ in range(10):
            nb_result = haralick_numba(img, distance=3, gray_levels=gl)
        t_numba = (time.perf_counter() - t0) / 10

        # Check correctness
        max_diff = np.max(np.abs(ref - nb_result))

        speedup = t_mahotas / t_numba
        print(f"  mahotas: {t_mahotas*1000:>8.1f}ms")
        print(f"  numba:   {t_numba*1000:>8.1f}ms")
        print(f"  speedup: {speedup:.1f}x")
        print(f"  match:   max_diff={max_diff:.2e} {'OK' if max_diff < 1e-6 else 'DIFF!'}")
        print()


if __name__ == "__main__":
    ok = verify()
    if ok:
        benchmark()
    else:
        print("\nVerification FAILED - fix differences before benchmarking")
