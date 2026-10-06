"""变化检测：新增（绿）/ 删除（红）/ 纹理修改（黄）。

前提：A_warped 与 B 已在同一坐标系，且已做光度归一化。
方向假设：A = 旧图，B = 新图。
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim_fn

from .merge import COLOR_ADDED, COLOR_REMOVED, COLOR_TEXTURE


@dataclass
class DiffParams:
    intensity_thresh: float = 25.0   # Lab 距离阈值
    ssim_thresh: float = 0.60        # SSIM 低于此值算结构变化
    min_area: int = 80               # 最小变化面积（px）
    morph_kernel: int = 3


def _clean(mask: np.ndarray, min_area: int, k: np.ndarray) -> np.ndarray:
    mm = mask.astype(np.uint8) * 255
    mm = cv2.morphologyEx(mm, cv2.MORPH_OPEN, k)
    mm = cv2.morphologyEx(mm, cv2.MORPH_CLOSE, k)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mm, 8)
    out = np.zeros_like(mm)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            out[labels == i] = 255
    return out > 0


def _estimate_bg(grayB: np.ndarray, mask_overlap: np.ndarray) -> float:
    """粗略估计背景灰度：用 overlap 区域的中位数。"""
    m = mask_overlap > 0
    return float(np.median(grayB[m])) if m.sum() else 128.0


def compute_change(A_warped: np.ndarray, B: np.ndarray,
                   mask_overlap: np.ndarray,
                   params: DiffParams):
    """返回 (标注图, masks_dict)。masks 含 added / removed / texture。"""
    h, w = B.shape[:2]
    m = mask_overlap > 0

    # 1. Lab 距离
    labA = cv2.cvtColor(A_warped, cv2.COLOR_BGR2LAB).astype(np.float32)
    labB = cv2.cvtColor(B, cv2.COLOR_BGR2LAB).astype(np.float32)
    diff_lab = np.linalg.norm(labA - labB, axis=2)

    # 2. SSIM
    grayA = cv2.cvtColor(A_warped, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(B, cv2.COLOR_BGR2GRAY)
    _, ssim_map = ssim_fn(grayA, grayB, full=True, data_range=255)

    # 3. 候选变化区
    intensity = (diff_lab > params.intensity_thresh) & m
    texture   = (ssim_map < params.ssim_thresh) & m

    # 4. 形态学 + 面积过滤
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                  (params.morph_kernel, params.morph_kernel))
    intensity = _clean(intensity, params.min_area, k)
    texture   = _clean(texture,   params.min_area, k)

    # 5a. 纹理变但亮度变化小 → 纹理修改
    texture_only = texture & ~intensity

    # 5b. 亮度显著变化 → 判断方向
    added = np.zeros((h, w), dtype=bool)
    removed = np.zeros((h, w), dtype=bool)
    bg = _estimate_bg(grayB, mask_overlap)

    n, labels, _, _ = cv2.connectedComponentsWithStats(
        intensity.astype(np.uint8), 8)
    for i in range(1, n):
        comp = labels == i
        a_mean = float(grayA[comp].mean())
        b_mean = float(grayB[comp].mean())
        if abs(b_mean - bg) < abs(a_mean - bg):
            removed |= comp      # B 露背景 → 物体在 B 里消失了
        else:
            added |= comp        # B 里有物体 → 新增

    # 6. 可视化（半透明叠加在 B 上）
    vis = B.copy().astype(np.float32)
    for mask, color in ((added, COLOR_ADDED),
                        (removed, COLOR_REMOVED),
                        (texture_only, COLOR_TEXTURE)):
        if mask.any():
            c = np.array(color, dtype=np.float32)
            vis[mask] = 0.5 * vis[mask] + 0.5 * c
    vis = np.clip(vis, 0, 255).astype(np.uint8)

    return vis, {"added": added, "removed": removed, "texture": texture_only}