"""异形合并 + 色层叠加。

统一在 B 坐标系下处理：A 先 warp 到 B 坐标，再算四种 mask。

两套着色体系：
  - 合并视图（4 色）：不存在 / A 独占 / B 独占 / 共同
  - 并排视图（叠加在原图上）：A 侧只出现 红(删除)+黄(纹理)，
                              B 侧只出现 绿(新增)+黄(纹理)
"""
from __future__ import annotations

import cv2
import numpy as np


# ===== 合并视图语义色（BGR） =====
COLOR_NONE    = (60, 60, 60)      # 不存在
COLOR_ONLY_A  = (220, 120, 60)    # A 独占（蓝）
COLOR_ONLY_B  = (60, 160, 240)    # B 独占（橙）
COLOR_SHARED  = (100, 200, 100)   # 共同（绿）

# ===== 变化检测语义色 =====
COLOR_REMOVED = (80, 80, 220)     # 删除 → 红
COLOR_ADDED   = (80, 220, 80)     # 新增 → 绿
COLOR_TEXTURE = (60, 220, 240)    # 纹理修改 → 黄


# ============ 基础 mask 运算 ============

def warp_to_B(A: np.ndarray, H: np.ndarray, shapeB):
    """单应路径下的 A→B 变形（TPS 路径请用 registration.warp_A_to_B）。"""
    hB, wB = shapeB[:2]
    warped = cv2.warpPerspective(
        A, H, (wB, hB),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    ones = np.ones(A.shape[:2], dtype=np.uint8) * 255
    maskA = cv2.warpPerspective(
        ones, H, (wB, hB),
        flags=cv2.INTER_NEAREST,
        borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return warped, maskA


def compute_masks(maskA: np.ndarray, maskB: np.ndarray) -> dict:
    ma = maskA > 0
    mb = maskB > 0
    return {
        "overlap": ma & mb,
        "onlyA":   ma & ~mb,
        "onlyB":   mb & ~ma,
        "canvas":  ma | mb,
    }


# ============ 合并视图 ============

def merge_images(A_warped, B, masks, overlap_mode="average"):
    """融合合并图。overlap_mode: average / A / B。"""
    h, w = B.shape[:2]
    out = np.zeros((h, w, 3), dtype=np.float32)
    ov, oa, ob = masks["overlap"], masks["onlyA"], masks["onlyB"]

    out[oa] = A_warped[oa].astype(np.float32)
    out[ob] = B[ob].astype(np.float32)
    if overlap_mode == "A":
        out[ov] = A_warped[ov].astype(np.float32)
    elif overlap_mode == "B":
        out[ov] = B[ov].astype(np.float32)
    else:
        out[ov] = 0.5 * A_warped[ov] + 0.5 * B[ov].astype(np.float32)
    return np.clip(out, 0, 255).astype(np.uint8)


def make_color_overlay(masks) -> np.ndarray:
    """合并视图的 4 色语义图（黑底）。"""
    h, w = masks["canvas"].shape
    canvas = np.full((h, w, 3), COLOR_NONE, dtype=np.uint8)
    canvas[masks["onlyA"]] = COLOR_ONLY_A
    canvas[masks["onlyB"]] = COLOR_ONLY_B
    canvas[masks["overlap"]] = COLOR_SHARED
    return canvas


# ============ 并排视图：在原图上叠加语义色 ============

def _blend(vis: np.ndarray, mask, color, alpha: float) -> None:
    if mask is None:
        return
    mask = np.asarray(mask).astype(bool)
    if not mask.any():
        return
    if vis.ndim != 3 or vis.shape[2] != 3:
        raise ValueError(f"_blend 期望 3 通道图像，收到 shape={vis.shape}")
    c = np.array(color, dtype=np.float32)
    vis[mask] = (1.0 - alpha) * vis[mask] + alpha * c


def make_side_overlay_A(imgA_warped: np.ndarray,
                        removed_mask: np.ndarray,
                        texture_mask: np.ndarray | None = None,
                        alpha: float = 0.5) -> np.ndarray:
    """A 视图（旧图）：在 A_warped 上叠加 红(删除) + 黄(纹理)。"""
    vis = imgA_warped.astype(np.float32).copy()
    _blend(vis, removed_mask, COLOR_REMOVED, alpha)
    if texture_mask is not None:
        _blend(vis, texture_mask, COLOR_TEXTURE, alpha)
    return np.clip(vis, 0, 255).astype(np.uint8)


def make_side_overlay_B(imgB: np.ndarray,
                        added_mask: np.ndarray,
                        texture_mask: np.ndarray | None = None,
                        alpha: float = 0.5) -> np.ndarray:
    """B 视图（新图）：在 B 上叠加 绿(新增) + 黄(纹理)。"""
    vis = imgB.astype(np.float32).copy()
    _blend(vis, added_mask, COLOR_ADDED, alpha)
    if texture_mask is not None:
        _blend(vis, texture_mask, COLOR_TEXTURE, alpha)
    return np.clip(vis, 0, 255).astype(np.uint8)