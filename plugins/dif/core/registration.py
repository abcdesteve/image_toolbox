"""自动配准：SIFT + MAGSAC 粗配准 + TPS 非刚性精配准。

- 单应矩阵 (H)：全局 3x3，处理平面整体变换
- 薄板样条 (TPS)：在 H 基础上吸收局部视差（笔记本、键帽等 3D 物体）
- 质量判定：inlier_ratio + 重叠区 NCC 双指标

输出 RegistrationResult，用 warp_A_to_B() 把 A 变形到 B 坐标系。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import cv2
import numpy as np


@dataclass
class RegistrationParams:
    # --- 特征 ---
    feature: str = "SIFT"            # SIFT / AKAZE / ORB
    nfeatures: int = 4000
    ratio: float = 0.72              # Lowe 比值
    ransac_thresh: float = 3.0
    min_match_count: int = 12
    use_magsac: bool = True
    max_dim: int = 1280              # 配准降采样上限

    # --- TPS 非刚性 ---
    use_tps: bool = True
    tps_max_control: int = 150       # 控制点上限
    tps_smoothing: float = 0.1       # 平滑（0=精确插值，大=抗噪）
    tps_eval_step: int = 16          # 求值粗网格步长（像素）

    # --- 质量判定 ---
    min_inlier_ratio: float = 0.25
    min_ncc: float = 0.5             # 重叠区 NCC 低于此判失败


@dataclass
class RegistrationResult:
    ok: bool
    H: Optional[np.ndarray] = None               # 原图坐标系下的单应
    tps_src: Optional[np.ndarray] = None         # (N,2) A 坐标系
    tps_dst: Optional[np.ndarray] = None         # (N,2) B 坐标系
    tps_smoothing: float = 0.0
    match_count: int = 0
    inlier_count: int = 0
    inlier_ratio: float = 0.0
    reproj_error: float = 0.0
    overlap_ncc: float = -1.0                    # H 估计后的 NCC（诊断用）
    message: str = ""
    hints: list = field(default_factory=list)
    vis_matches: Optional[np.ndarray] = None


# ============ 内部工具 ============

def _to_gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img


def _downscale(img, max_dim):
    h, w = img.shape[:2]
    scale = min(1.0, max_dim / max(h, w))
    if scale >= 1.0:
        return img, 1.0
    new = cv2.resize(img,
                     (int(round(w * scale)), int(round(h * scale))),
                     interpolation=cv2.INTER_AREA)
    return new, scale


def _make_detector(feature, nfeatures):
    if feature == "SIFT":
        return cv2.SIFT_create(nfeatures=nfeatures)
    if feature == "AKAZE":
        return cv2.AKAZE_create()
    if feature == "ORB":
        return cv2.ORB_create(nfeatures=nfeatures)
    raise ValueError(f"未知特征算法: {feature}")


def _make_matcher(feature):
    norm = cv2.NORM_HAMMING if feature == "ORB" else cv2.NORM_L2
    return cv2.BFMatcher(norm)


def _overlap_ncc(grayA, grayB, H):
    """H warp 后重叠区的归一化互相关。配准对不对，看这个最准。"""
    h, w = grayB.shape[:2]
    warped = cv2.warpPerspective(grayA, H, (w, h), flags=cv2.INTER_LINEAR)
    ones = np.ones(grayA.shape, np.uint8) * 255
    maskA = cv2.warpPerspective(ones, H, (w, h), flags=cv2.INTER_NEAREST)
    mask = (maskA > 0) & (grayB > 0)
    if mask.sum() < 200:
        return -1.0
    a = warped[mask].astype(np.float32)
    b = grayB[mask].astype(np.float32)
    a -= a.mean()
    b -= b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else -1.0


def _grid_sample_indices(points, n_max, shape):
    """从点集里挑空间分散的子集，返回索引（防止 TPS 过拟合/局部堆叠）。"""
    if len(points) <= n_max:
        return np.arange(len(points))
    h, w = shape[:2]
    n_side = max(2, int(np.ceil(np.sqrt(n_max))))
    xs = np.clip((points[:, 0] / w * n_side).astype(int), 0, n_side - 1)
    ys = np.clip((points[:, 1] / h * n_side).astype(int), 0, n_side - 1)
    cell = ys * n_side + xs
    seen = set()
    selected = []
    for i, c in enumerate(cell):
        if c not in seen:
            seen.add(c)
            selected.append(i)
            if len(selected) >= n_max:
                break
    return np.array(selected)


# ============ 主流程 ============

def register(imgA: np.ndarray, imgB: np.ndarray,
             params: RegistrationParams = None) -> RegistrationResult:
    if params is None:
        params = RegistrationParams()

    a_small, sa = _downscale(imgA, params.max_dim)
    b_small, sb = _downscale(imgB, params.max_dim)
    grayA = _to_gray(a_small)
    grayB = _to_gray(b_small)

    # 1. 特征
    detector = _make_detector(params.feature, params.nfeatures)
    kpA, desA = detector.detectAndCompute(grayA, None)
    kpB, desB = detector.detectAndCompute(grayB, None)
    if desA is None or desB is None or len(kpA) < 4 or len(kpB) < 4:
        return RegistrationResult(
            ok=False,
            message=f"特征点不足（A={len(kpA) if kpA else 0}, "
                    f"B={len(kpB) if kpB else 0}）。",
            hints=["纹理可能过弱（大面积纯色）。",
                   "换 AKAZE 特征算法。",
                   "确认两图确实拍摄同一场景。"])

    # 2. KNN + 比值
    matcher = _make_matcher(params.feature)
    knn = matcher.knnMatch(desA, desB, k=2)
    good = []
    for pair in knn:
        if len(pair) < 2:
            continue
        m, n = pair
        if m.distance < params.ratio * n.distance:
            good.append(m)

    if len(good) < params.min_match_count:
        return RegistrationResult(
            ok=False, match_count=len(good),
            message=f"有效匹配不足（{len(good)} < {params.min_match_count}）。",
            hints=["把「Lowe 比值」调大（0.85~0.9）。",
                   "换 AKAZE 特征算法。",
                   "确认重叠区域足够大。"])

    src = np.float32([kpA[m.queryIdx].pt for m in good]).reshape(-1, 2)
    dst = np.float32([kpB[m.trainIdx].pt for m in good]).reshape(-1, 2)

    # 3. MAGSAC++ / RANSAC
    method = (cv2.USAC_MAGSAC
              if (params.use_magsac and hasattr(cv2, "USAC_MAGSAC"))
              else cv2.RANSAC)
    try:
        H, inlier_mask = cv2.findHomography(
            src.reshape(-1, 1, 2), dst.reshape(-1, 1, 2),
            method, params.ransac_thresh, maxIters=10000, confidence=0.9995)
    except cv2.error:
        H, inlier_mask = cv2.findHomography(
            src.reshape(-1, 1, 2), dst.reshape(-1, 1, 2),
            cv2.RANSAC, params.ransac_thresh)

    if H is None:
        return RegistrationResult(
            ok=False, match_count=len(good),
            message="单应矩阵估计失败。",
            hints=["把「RANSAC 阈值」调到 5.0。",
                   "把「Lowe 比值」调到 0.65。",
                   "确认场景为平面。"])
    inlier_mask = inlier_mask.ravel()
    inliers = int(inlier_mask.sum())
    inlier_ratio = inliers / max(len(good), 1)

    proj = cv2.perspectiveTransform(src.reshape(-1, 1, 2), H).reshape(-1, 2)
    err = np.linalg.norm(proj - dst, axis=1)
    reproj = float(err[inlier_mask == 1].mean()) if inliers else 0.0

    # 4. NCC 诊断
    ncc_h = _overlap_ncc(grayA, grayB, H)

    # 5. 采集 TPS 控制点（网格采样保证空间分散）
    inlier_src = src[inlier_mask == 1]
    inlier_dst = dst[inlier_mask == 1]
    idx = _grid_sample_indices(inlier_dst, params.tps_max_control,
                               grayB.shape)
    tps_src = inlier_src[idx] / sa       # 还原到原图坐标
    tps_dst = inlier_dst[idx] / sb

    # 6. H 还原到原图分辨率
    if sa != 1.0 or sb != 1.0:
        Sa = np.diag([sa, sa, 1.0])
        Sb = np.diag([sb, sb, 1.0])
        H = np.linalg.inv(Sb) @ H @ Sa

    # 7. 质量判定
    ok = (inliers >= params.min_match_count
          and inlier_ratio >= params.min_inlier_ratio
          and ncc_h >= params.min_ncc)

    hints = []
    if not ok:
        if inlier_ratio < params.min_inlier_ratio:
            hints.append(f"内点率低（{inlier_ratio:.1%}）：ratio 调到 0.65。")
        if ncc_h < params.min_ncc:
            hints.append(
                f"重叠区 NCC 低（{ncc_h:.2f}）：配准错误，或场景非平面。"
                "尝试：① 缩小拍摄角度差；② 换 AKAZE；③ 确认同场景。")
        if reproj > 5.0:
            hints.append(f"重投影误差 {reproj:.2f}px 偏大：开 ECC 或缩角差。")

    # 8. 可视化
    vis = None
    try:
        n_show = min(80, len(good))
        vis = cv2.drawMatches(
            a_small, kpA, b_small, kpB, good[:n_show], None,
            matchColor=(0, 255, 0),
            matchesMask=inlier_mask[:n_show].tolist(),
            singlePointColor=(255, 0, 0),
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    except Exception:
        pass

    return RegistrationResult(
        ok=ok, H=H,
        tps_src=tps_src, tps_dst=tps_dst,
        tps_smoothing=params.tps_smoothing,
        match_count=len(good), inlier_count=inliers,
        inlier_ratio=inlier_ratio, reproj_error=reproj,
        overlap_ncc=ncc_h,
        message="配准成功" if ok else "配准质量偏低，建议调参后重试。",
        hints=hints, vis_matches=vis)


# ============ 变形 ============

def warp_A_to_B(imgA: np.ndarray, reg: RegistrationResult,
                shapeB, params: RegistrationParams = None):
    """用 TPS（优先）或 H（回退）把 A 变形到 B 坐标系。"""
    if params is None:
        params = RegistrationParams()
    h, w = shapeB[:2]
    if reg.H is None:
        raise ValueError("RegistrationResult 缺少 H")

    use_tps = (params.use_tps
               and reg.tps_src is not None
               and len(reg.tps_src) >= 8)

    if not use_tps:
        warped = cv2.warpPerspective(
            imgA, reg.H, (w, h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
        ones = np.ones(imgA.shape[:2], np.uint8) * 255
        mask = cv2.warpPerspective(
            ones, reg.H, (w, h),
            flags=cv2.INTER_NEAREST,
            borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        return warped, mask

    from scipy.interpolate import RBFInterpolator

    # 反向插值器：给 B 坐标，返回 A 坐标（因为 remap 需要从目标找源）
    interp = RBFInterpolator(
        reg.tps_dst, reg.tps_src,
        kernel='thin_plate_spline',
        smoothing=reg.tps_smoothing)

    # 粗网格求值再上采样（避免 O(pixels) 次 RBF 查询）
    step = max(4, int(params.tps_eval_step))
    y_small = np.arange(0, h, step, dtype=np.float32)
    x_small = np.arange(0, w, step, dtype=np.float32)
    if len(y_small) == 0 or y_small[-1] != h - 1:
        y_small = np.append(y_small, float(h - 1))
    if len(x_small) == 0 or x_small[-1] != w - 1:
        x_small = np.append(x_small, float(w - 1))

    gy, gx = np.meshgrid(y_small, x_small, indexing='ij')
    query = np.stack([gx.ravel(), gy.ravel()], axis=1).astype(np.float64)

    src_coords = interp(query).reshape(len(y_small), len(x_small), 2)
    map_x = cv2.resize(src_coords[..., 0].astype(np.float32), (w, h),
                       interpolation=cv2.INTER_LINEAR)
    map_y = cv2.resize(src_coords[..., 1].astype(np.float32), (w, h),
                       interpolation=cv2.INTER_LINEAR)

    warped = cv2.remap(imgA, map_x, map_y, cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    ones = np.ones(imgA.shape[:2], np.uint8) * 255
    mask = cv2.remap(ones, map_x, map_y, cv2.INTER_NEAREST,
                     borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return warped, mask