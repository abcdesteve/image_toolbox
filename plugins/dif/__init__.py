"""dif 插件主界面：双图自动配准 + 异形合并 + 变化检测。"""
from __future__ import annotations

import traceback
from pathlib import Path

import cv2
import numpy as np
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from lib.custom_widgets.ImageView import ImageView
from lib.custom_widgets.SegmentedToggleWidget import SegmentedToggleWidget
from lib.custom_widgets.FluentDrawer import FluentDrawer, DrawerSide, AutoHideMode

from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF

from .dif_ui import Ui_DifInterface
from .advance_panel_ui import Ui_AdvancePanel
from .core.registration import *
from .core.photometric import *
from .core.merge import *
from .core.diff import *


# ============================================================
# 工具
# ============================================================

_IMG_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff"}


def _safe_imread(path: str):
    """兼容中文路径的读图。"""
    data = np.fromfile(path, dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


# ============================================================
# 后台 Worker
# ============================================================

class _Signals(QObject):
    finished = Signal(object)
    failed = Signal(object)


class _Step1Worker(QRunnable):
    def __init__(self, A, B, reg_p, photo_p, signals):
        super().__init__()
        self.A, self.B = A, B
        self.reg_p = reg_p
        self.photo_p = photo_p
        self.signals = signals

    @Slot()
    def run(self):
        try:
            reg = register(self.A, self.B, self.reg_p)
            if not reg.ok:
                self.signals.failed.emit(reg)
                return
            A_warp, maskA = warp_A_to_B(
                self.A, reg, self.B.shape, self.reg_p)
            maskB = np.full(self.B.shape[:2], 255, np.uint8)
            masks = compute_masks(maskA, maskB)
            A_norm = normalize(A_warp, self.B, masks["overlap"],
                               self.photo_p)
            merged = merge_images(A_norm, self.B, masks, "average")
            color_overlay = make_color_overlay(masks)
            self.signals.finished.emit({
                "reg": reg,
                "A_warp": A_warp,
                "maskA": maskA,
                "masks": masks,
                "A_norm": A_norm,
                "merged": merged,
                "color_overlay": color_overlay,
            })
        except Exception as e:
            traceback.print_exc()
            self.signals.failed.emit(f"处理时发生异常：{e}")


class _Step2Worker(QRunnable):
    def __init__(self, A_norm, B, overlap, diff_p, signals):
        super().__init__()
        self.A_norm = A_norm
        self.B = B
        self.overlap = overlap
        self.diff_p = diff_p
        self.signals = signals

    @Slot()
    def run(self):
        try:
            vis, masks = compute_change(
                self.A_norm, self.B, self.overlap, self.diff_p)
            self.signals.finished.emit((vis, masks))
        except Exception as e:
            traceback.print_exc()
            self.signals.failed.emit(f"处理时发生异常：{e}")


# ============================================================
# 主界面
# ============================================================
class AdvancePanel(FluentDrawer, Ui_AdvancePanel):
    def __init__(self, parent=None):
        FluentDrawer.__init__(self, '高级设置', DrawerSide.BOTTOM, parent, checkbox_enabled=True,expanded=False, autohide=AutoHideMode.CHECKBOX)
        self.container = QWidget(self)
        self.contentLayout().addWidget(self.container)
        Ui_AdvancePanel.setupUi(self, self.container)


class DifInterface(QWidget, Ui_DifInterface):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # --- 状态 ---
        self.img_A: np.ndarray | None = None
        self.img_B: np.ndarray | None = None
        self.rot_A_deg = 0
        self.rot_B_deg = 0

        self.reg = None
        self.A_warp = None
        self.maskA = None
        self.masks = None
        self.A_norm = None
        self.merged = None
        self.color_overlay = None
        self.change_vis = None
        self.change_masks = None

        self._busy = False
        self._pool = QThreadPool.globalInstance()

        self.view_A = ImageView(self)
        self.view_B = ImageView(self)
        self.view_merge = ImageView(self)
        self.page_side.layout().addWidget(self.view_A)
        self.page_side.layout().addWidget(self.view_B)
        self.page_merged.layout().addWidget(self.view_merge)
        self.advance_panel = AdvancePanel(self)
        self.layout().addWidget(self.advance_panel)

        self.overlay_seg = SegmentedToggleWidget(self)
        self.overlay_seg.setFixedWidth(250)
        self.overlay_seg.addItem("align", "对齐映射叠加")
        self.overlay_seg.addItem("dif", "差异叠加")
        self.overlay_seg.currentItemChanged.connect(self._on_overlay_changed)
        self.view_row.addWidget(self.overlay_seg)
        self.view_seg.addItem("side", "A / B 并排")
        self.view_seg.addItem("merged", "合并结果")
        self.view_seg.currentItemChanged.connect(self._on_seg_changed)
        self.view_seg.setCurrentItem("side")
        self.btn_rot_A.setIcon(FIF.ROTATE)
        self.btn_rot_B.setIcon(FIF.ROTATE)
        self.advance_panel.combo_feature.addItems(["SIFT", "AKAZE", "ORB"])
        self.advance_panel.combo_feature.setCurrentIndex(0)
        self.advance_panel.combo_photo_method.addItems(["linear", "reinhard", "hist_match"])
        self.advance_panel.combo_photo_method.setCurrentIndex(0)

        # --- 信号 ---
        self.btn_pick_A.clicked.connect(self._on_pick_A)
        self.btn_pick_B.clicked.connect(self._on_pick_B)
        self.btn_rot_A.clicked.connect(self._on_rot_A)
        self.btn_rot_B.clicked.connect(self._on_rot_B)

        self.btn_step1.clicked.connect(self._on_step1)
        self.btn_step2.clicked.connect(self._on_step2)
        self.btn_export.clicked.connect(self._on_export)

        # --- ImageView 拖拽 ---
        self.view_A.file_dropped.connect(self._on_drop_A)
        self.view_B.file_dropped.connect(self._on_drop_B)
        self.view_merge.file_dropped.connect(self._on_drop_merged)

        # --- 初始状态 ---
        self._update_state()
        self._refresh_views()

    # ============================================================
    # 视图切换
    # ============================================================

    def _on_seg_changed(self, key: str) -> None:
        if key == "side":
            self.view_stack.setCurrentIndex(0)
        elif key == "merged":
            self.view_stack.setCurrentIndex(1)

    def _on_overlay_changed(self, key: str) -> None:
        self._refresh_views()

    # ============================================================
    # 选图 / 旋转
    # ============================================================

    def _on_pick_A(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片 A", "", "图片 (*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff)")
        if path:
            self._load_A(path)

    def _on_pick_B(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片 B", "", "图片 (*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff)")
        if path:
            self._load_B(path)

    def _on_drop_A(self, path: str):
        if Path(path).suffix.lower() in _IMG_EXTS:
            self._load_A(path)

    def _on_drop_B(self, path: str):
        if Path(path).suffix.lower() in _IMG_EXTS:
            self._load_B(path)

    def _on_drop_merged(self, path: str):
        if Path(path).suffix.lower() in _IMG_EXTS:
            if self.img_A is None:
                self._load_A(path)
            else:
                self._load_B(path)

    def _load_A(self, path: str):
        img = _safe_imread(path)
        if img is None:
            InfoBar.error("读取失败", f"无法读取：{path}",
                          parent=self, duration=4000)
            return
        self.img_A = img
        self.rot_A_deg = 0
        self.lbl_path_A.setText(Path(path).name)
        self._invalidate_results()
        self._refresh_views()
        self._update_state()

    def _load_B(self, path: str):
        img = _safe_imread(path)
        if img is None:
            InfoBar.error("读取失败", f"无法读取：{path}",
                          parent=self, duration=4000)
            return
        self.img_B = img
        self.rot_B_deg = 0
        self.lbl_path_B.setText(Path(path).name)
        self._invalidate_results()
        self._refresh_views()
        self._update_state()

    def _on_rot_A(self):
        if self.img_A is None:
            return
        self.img_A = cv2.rotate(self.img_A, cv2.ROTATE_90_CLOCKWISE)
        self.rot_A_deg = (self.rot_A_deg + 90) % 360
        self._invalidate_results()
        self._refresh_views()

    def _on_rot_B(self):
        if self.img_B is None:
            return
        self.img_B = cv2.rotate(self.img_B, cv2.ROTATE_90_CLOCKWISE)
        self.rot_B_deg = (self.rot_B_deg + 90) % 360
        self._invalidate_results()
        self._refresh_views()

    # ============================================================
    # 参数收集
    # ============================================================

    def _collect_reg_params(self) -> RegistrationParams:
        return RegistrationParams(
            feature=self.advance_panel.combo_feature.currentText(),
            ratio=self.advance_panel.spin_ratio.value(),
            ransac_thresh=self.advance_panel.spin_ransac.value(),
            min_match_count=self.advance_panel.spin_min_match.value(),
            min_inlier_ratio=self.advance_panel.spin_min_inlier.value(),
            use_tps=self.chk_tps.isChecked(),
            tps_max_control=self.advance_panel.spin_tps_ctrl.value(),
            tps_smoothing=self.advance_panel.spin_tps_smooth.value(),
            tps_eval_step=self.advance_panel.spin_tps_step.value(),
        )

    def _collect_photo_params(self) -> PhotometricParams:
        return PhotometricParams(
            method=self.advance_panel.combo_photo_method.currentText(),
        )

    def _collect_diff_params(self) -> DiffParams:
        return DiffParams(
            intensity_thresh=self.advance_panel.spin_lab_thresh.value(),
            ssim_thresh=self.advance_panel.spin_ssim_thresh.value(),
            min_area=self.advance_panel.spin_min_area.value(),
            morph_kernel=self.advance_panel.spin_morph.value(),
        )

    # ============================================================
    # Step 1
    # ============================================================

    def _on_step1(self):
        if self.img_A is None or self.img_B is None or self._busy:
            return
        self._set_busy(True)
        signals = _Signals()
        signals.finished.connect(self._on_step1_ok)
        signals.failed.connect(self._on_step1_fail)
        worker = _Step1Worker(
            self.img_A, self.img_B,
            self._collect_reg_params(),
            self._collect_photo_params(),
            signals)
        self._pool.start(worker)

    def _on_step1_ok(self, data: dict):
        self._set_busy(False)
        self.reg = data["reg"]
        self.A_warp = data["A_warp"]
        self.maskA = data["maskA"]
        self.masks = data["masks"]
        self.A_norm = data["A_norm"]
        self.merged = data["merged"]
        self.color_overlay = data["color_overlay"]
        # Step2 结果作废
        self.change_vis = None
        self.change_masks = None

        self._refresh_views()
        self._update_state()

        self.overlay_seg.setCurrentItem('align')

        InfoBar.success(
            "Step 1 完成",
            f"匹配 {self.reg.match_count} / 内点 {self.reg.inlier_count} "
            f"/ 内点率 {self.reg.inlier_ratio:.1%} / NCC {self.reg.overlap_ncc:.2f}",
            parent=self, duration=5000)

    def _on_step1_fail(self, info):
        self._set_busy(False)
        self._update_state()

        if isinstance(info, str):
            MessageBox("处理失败", info, self).exec()
            return
        # RegistrationResult
        lines = [info.message, ""]
        if info.hints:
            lines.append("建议：")
            lines.extend(f"· {h}" for h in info.hints)
            lines.append("")
        lines.append(f"匹配 = {info.match_count}")
        lines.append(f"内点 = {info.inlier_count}")
        lines.append(f"内点率 = {info.inlier_ratio:.1%}")
        lines.append(f"重叠区 NCC = {info.overlap_ncc:.2f}")
        lines.append(f"重投影误差 = {info.reproj_error:.2f}px")
        MessageBox("配准失败", "\n".join(lines), self).exec()

    # ============================================================
    # Step 2
    # ============================================================

    def _on_step2(self):
        if self.A_norm is None or self._busy:
            return
        self._set_busy(True)
        signals = _Signals()
        signals.finished.connect(self._on_step2_ok)
        signals.failed.connect(self._on_step2_fail)
        worker = _Step2Worker(
            self.A_norm, self.img_B, self.masks["overlap"],
            self._collect_diff_params(), signals)
        self._pool.start(worker)

    def _on_step2_ok(self, data):
        self._set_busy(False)
        vis, masks = data
        self.change_vis = vis
        self.change_masks = masks
        self._refresh_views()
        self._update_state()

        self.overlay_seg.setCurrentItem('dif')

        counts = {k: int(v.sum()) for k, v in masks.items()}
        InfoBar.success(
            "Step 2 完成",
            f"新增 {counts['added']} px / 删除 {counts['removed']} px "
            f"/ 纹理 {counts['texture']} px",
            parent=self, duration=5000)

    def _on_step2_fail(self, msg):
        self._set_busy(False)
        self._update_state()
        MessageBox("变化检测失败", str(msg), self).exec()

    # ============================================================
    # 视图刷新
    # ============================================================

    def _refresh_views(self):
        show_align = self.overlay_seg.currentRouteKey() == "align"
        show_dif = self.overlay_seg.currentRouteKey() == "dif"
        has_diff = self.change_masks is not None

        # ---------- A 视图 ----------
        if self.img_A is None:
            self.view_A.clear_image()
        else:
            img = self.A_warp if self.A_warp is not None else self.img_A
            if has_diff and show_dif:
                vis = make_side_overlay_A(img, self.change_masks["removed"],
                                          texture_mask=self.change_masks["texture"])
                self.view_A.set_image_bgr(vis)
            elif self.A_warp is not None and show_align:
                vis = img.astype(np.float32).copy()
                if self.masks is not None:
                    onlyA = self.masks["onlyA"]
                    c = np.array(COLOR_ONLY_A, np.float32)
                    vis[onlyA] = 0.5 * vis[onlyA] + 0.5 * c
                if self.maskA is not None:
                    vis[self.maskA == 0] = 0
                self.view_A.set_image_bgr(np.clip(vis, 0, 255).astype(np.uint8))
            else:
                self.view_A.set_image_bgr(img)

        # ---------- B 视图 ----------
        if self.img_B is None:
            self.view_B.clear_image()
        else:
            if has_diff and show_dif:
                vis = make_side_overlay_B(self.img_B, self.change_masks["added"],
                                          texture_mask=self.change_masks["texture"])
                self.view_B.set_image_bgr(vis)
            elif self.A_warp is not None and show_align:
                vis = self.img_B.astype(np.float32).copy()
                if self.masks is not None:
                    onlyB = self.masks["onlyB"]
                    c = np.array(COLOR_ONLY_B, np.float32)
                    vis[onlyB] = 0.5 * vis[onlyB] + 0.5 * c
                self.view_B.set_image_bgr(np.clip(vis, 0, 255).astype(np.uint8))
            else:
                self.view_B.set_image_bgr(self.img_B)

        # ---------- 合并视图 ----------
        if self.merged is None:
            self.view_merge.clear_image()
        elif has_diff and show_dif:
            self.view_merge.set_image_bgr(self.change_vis)
        elif show_align:
            self.view_merge.set_image_bgr(self.color_overlay)
        else:
            self.view_merge.set_image_bgr(self.merged)

    # ============================================================
    # 状态机
    # ============================================================

    def _update_state(self):
        ready = (self.img_A is not None) and (self.img_B is not None) and (not self._busy)
        step1_done = self.merged is not None and not self._busy
        step2_done = self.change_vis is not None and not self._busy

        self.btn_step1.setEnabled(ready)
        self.btn_step2.setEnabled(step1_done)
        [v.setEnabled({'align': step1_done, 'dif': step2_done}[k]) for k, v in self.overlay_seg.items.items()]
        self.btn_export.setEnabled(step1_done)
        self.advance_panel.checkbox().setEnabled(ready)
        if not ready:
            self.advance_panel.checkbox().setChecked(False)

    def _set_busy(self, busy: bool):
        self._busy = busy
        self._update_state()
        if busy:
            self.btn_step1.setEnabled(False)
            self.btn_step2.setEnabled(False)
            self.btn_export.setEnabled(False)

    def _invalidate_results(self):
        self.reg = None
        self.A_warp = None
        self.maskA = None
        self.masks = None
        self.A_norm = None
        self.merged = None
        self.color_overlay = None
        self.change_vis = None
        self.change_masks = None

        self.view_merge.clear_image()
        self._update_state()

    # ============================================================
    # 导出
    # ============================================================

    def _on_export(self):
        if self.btn_diff.isChecked() and self.change_vis is not None:
            img = self.change_vis
            default_name = "diff_result.png"
            kind = "变化检测"
        elif self.merged is not None:
            img = self.merged
            default_name = "merged_result.png"
            kind = "合并图"
        else:
            InfoBar.warning("无可导出内容", "请先执行 Step 1。", parent=self, duration=3000)
            return

        path, _ = QFileDialog.getSaveFileName(self, f"导出{kind}", default_name,
                                              "PNG (*.png);;JPEG (*.jpg *.jpeg)")
        if not path:
            return
        ext = Path(path).suffix.lower() or ".png"
        ok, buf = cv2.imencode(ext, img)
        if not ok:
            InfoBar.error("保存失败", "cv2.imencode 失败", parent=self, duration=4000)
            return
        try:
            buf.tofile(path)
            InfoBar.success("已保存", path, parent=self, duration=4000)
        except Exception as e:
            InfoBar.error("保存失败", str(e), parent=self, duration=4000)
