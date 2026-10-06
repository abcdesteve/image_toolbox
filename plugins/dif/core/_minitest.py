"""dif 插件 core 层最小验证脚本。

流程：读两张图 → 配准 → 光度归一化 → 异形合并 + 色层 → 变化检测
结果图片输出到同目录 _minimal_output/ 下。

用法：
    1. 改下面 PATH_A / PATH_B 两行常量
    2. python _minitest.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# ============================================================
# 用户配置
# ============================================================
PATH_A = r"D:\HONOR Share\Honor Share\a.jpg"      # 旧图（基准）
PATH_B = r"D:\HONOR Share\Honor Share\b.jpg"      # 新图（参考坐标系）

OUT_DIR = Path(__file__).resolve().parent / "_minimal_output"
SHOW_WINDOWS = False              # True 时弹窗预览，按任意键关闭
# ============================================================

import cv2
import numpy as np

# 让 `dif` 包能被 import 进来（脚本在 plugins/dif/core/ 下）
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.registration import (
    RegistrationParams, register, warp_A_to_B,
)
from core.photometric import PhotometricParams, normalize
from core.merge import (
    compute_masks, merge_images,
    make_color_overlay,
    make_side_overlay_A, make_side_overlay_B,
)
from core.diff import DiffParams, compute_change


# ---------- 小工具 ----------

def _log(msg: str) -> None:
    print(f"[dif] {msg}")


def _save(name: str, img: np.ndarray) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUT_DIR / name), img)
    _log(f"已保存 {name}")


def _show(title: str, img: np.ndarray) -> None:
    if not SHOW_WINDOWS:
        return
    h, w = img.shape[:2]
    if max(h, w) > 1400:
        s = 1400 / max(h, w)
        img = cv2.resize(img, (int(w * s), int(h * s)))
    cv2.imshow(title, img)


def _safe_imread(path: Path):
    """兼容中文路径的读图。"""
    data = np.fromfile(str(path), dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


# ---------- 主流程 ----------

def main() -> None:
    pa, pb = Path(PATH_A), Path(PATH_B)
    if not pa.exists() or not pb.exists():
        _log(f"图片路径不存在：\n  A = {pa}\n  B = {pb}")
        _log("请修改文件顶部的 PATH_A / PATH_B 常量后重试。")
        sys.exit(1)

    A = _safe_imread(pa)
    B = _safe_imread(pb)
    if A is None or B is None:
        _log("cv2.imdecode 失败，检查文件格式是否为常见图片。")
        sys.exit(1)
    _log(f"A: {A.shape[1]}x{A.shape[0]}   B: {B.shape[1]}x{B.shape[0]}")

    # ================= Step 1 =================
    _log("==== Step1 配准 ====")
    reg = register(A, B, RegistrationParams())
    _log(f"match={reg.match_count}  inlier={reg.inlier_count}  "
         f"inlier_ratio={reg.inlier_ratio:.1%}  reproj={reg.reproj_error:.2f}px  "
         f"NCC={reg.overlap_ncc:.3f}")
    _log(f"结果：{reg.message}")
    for hint in reg.hints:
        _log(f"  · {hint}")
    if reg.vis_matches is not None:
        _save("00_matches.png", reg.vis_matches)
    if not reg.ok or reg.H is None:
        _log("配准失败，无法继续。")
        sys.exit(2)

    # A → B 坐标系（TPS）
    A_warp, maskA = warp_A_to_B(A, reg, B.shape)
    maskB = np.full(B.shape[:2], 255, dtype=np.uint8)
    masks = compute_masks(maskA, maskB)
    canvas_px = int(masks["canvas"].sum())
    ov_ratio = masks["overlap"].sum() / max(canvas_px, 1)
    _log(f"重叠区占并集：{ov_ratio:.1%}   "
         f"onlyA={int(masks['onlyA'].sum())}px  "
         f"onlyB={int(masks['onlyB'].sum())}px  "
         f"overlap={int(masks['overlap'].sum())}px")

    # 光度归一化（只在重叠区估计参数）
    _log("==== 光度归一化（linear） ====")
    A_norm = normalize(A_warp, B, masks["overlap"],
                       PhotometricParams(method="linear"))

    # ================= Step1 合并图 =================
    merged = merge_images(A_norm, B, masks, overlap_mode="average")
    color_overlay = make_color_overlay(masks)

    _save("01_input_A.png", A)
    _save("02_input_B.png", B)
    _save("03_warpA.png", A_warp)
    _save("04_merged.png", merged)
    _save("05_color_overlay.png", color_overlay)

    # ================= Step2 变化检测 =================
    _log("==== Step2 变化检测 ====")
    change_vis, change_masks = compute_change(
        A_norm, B, masks["overlap"], DiffParams())
    _save("06_change.png", change_vis)
    for k, m in change_masks.items():
        _log(f"  {k}: {int(m.sum())} px")

    # ===== 并排色层（A 红+黄，B 绿+黄） =====
    tex = change_masks["texture"]
    sideA = make_side_overlay_A(A_warp, change_masks["removed"],
                                texture_mask=tex)
    sideB = make_side_overlay_B(B, change_masks["added"],
                                texture_mask=tex)
    _save("05a_side_A.png", sideA)
    _save("05b_side_B.png", sideB)

    # 预览
    if SHOW_WINDOWS:
        _show("A (input)", A)
        _show("B (input)", B)
        _show("A warped to B", A_warp)
        _show("Merged", merged)
        _show("Color Overlay", color_overlay)
        _show("Change Detection", change_vis)
        _log("按任意键关闭所有窗口...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()