"""光度归一化：消除两图之间的曝光、色彩差异。

只在重叠区域内估计参数，避免非重叠区干扰。
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class PhotometricParams:
    method: str = "linear"   # linear / reinhard / hist_match


def _mask_ok(mask: np.ndarray) -> bool:
    return mask is not None and (mask > 0).sum() >= 100


def linear_correct(A: np.ndarray, B: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """逐通道拟合 B ≈ k·A + t，返回校正后的 A。"""
    if not _mask_ok(mask):
        return A.copy()
    m = mask > 0
    out = A.astype(np.float32).copy()
    channels = range(A.shape[2]) if A.ndim == 3 else [0]
    for c in channels:
        a_c = A[..., c][m].astype(np.float32)
        b_c = B[..., c][m].astype(np.float32)
        M = np.stack([a_c, np.ones_like(a_c)], axis=1)
        (k, t), *_ = np.linalg.lstsq(M, b_c, rcond=None)
        if not np.isfinite(k) or k <= 1e-3:
            continue
        out[..., c] = out[..., c] * k + t
    return np.clip(out, 0, 255).astype(np.uint8)


def reinhard_transfer(A: np.ndarray, B: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Lab 空间均值/标准差迁移。对整体色偏更自然。"""
    if not _mask_ok(mask):
        return A.copy()
    m = mask > 0
    labA = cv2.cvtColor(A, cv2.COLOR_BGR2LAB).astype(np.float32)
    labB = cv2.cvtColor(B, cv2.COLOR_BGR2LAB).astype(np.float32)
    for c in range(3):
        muA, sdA = labA[..., c][m].mean(), labA[..., c][m].std() + 1e-6
        muB, sdB = labB[..., c][m].mean(), labB[..., c][m].std() + 1e-6
        labA[..., c] = (labA[..., c] - muA) * (sdB / sdA) + muB
    return cv2.cvtColor(np.clip(labA, 0, 255).astype(np.uint8),
                        cv2.COLOR_LAB2BGR)


def hist_match(A: np.ndarray, B: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """直方图匹配。全局统计，非重叠区也会被影响，慎用。"""
    if not _mask_ok(mask):
        return A.copy()
    from skimage.exposure import match_histograms
    return match_histograms(A, B, channel_axis=-1).astype(np.uint8)


def normalize(A, B, mask, params: PhotometricParams) -> np.ndarray:
    if params.method == "linear":
        return linear_correct(A, B, mask)
    if params.method == "reinhard":
        return reinhard_transfer(A, B, mask)
    if params.method == "hist_match":
        return hist_match(A, B, mask)
    return A.copy()