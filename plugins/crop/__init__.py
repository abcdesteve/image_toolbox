from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF

import os
import cv2
import numpy as np
from PIL import Image

from lib.custom_widgets.ImageCanvas import ImageCanvas
from lib.custom_widgets.RulerWidget import RulerWidget

from .crop_ui import *


# ============================================================
# 0. 工具函数
# ============================================================

def estimate_jpeg_quality(path):
    try:
        with Image.open(path) as im:
            if im.format != 'JPEG':
                return None
            qtables = im.quantization
            if not qtables:
                return None
            table = list(qtables.get(0, []))
            if len(table) < 10:
                return None
            std = [16, 11, 10, 16, 24, 40, 51, 61, 12, 12]
            scales = [table[i] * 100.0 / std[i] for i in range(10)]
            avg = sum(scales) / len(scales)
            if avg <= 0:
                return None
            q = 5000.0 / avg if avg > 100 else (200.0 - avg) / 2.0
            return max(1, min(100, int(round(q))))
    except Exception:
        return None


def detect_solid_segments(image_bgr, uniformity_tol=25, min_segment_size=4):
    """
    ★ 重写版纯色检测：
    一行（或一列）被认为"属于某个纯色带"，当且仅当：
      (a) 行内像素极差 < uniformity_tol（这一行本身足够均匀）
      (b) 与上一行的逐像素平均差 < uniformity_tol（与上一行属于同一色块）

    对第 0 行（列）把条件 (b) 视为恒真——它总是某段的起点。

    返回候选吸附点列表（图片坐标），包含图片首尾边界 0 和 len。
    """
    if image_bgr is None:
        return [], []

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY).astype(np.int16)
    h, w = gray.shape

    # ---------- 水平方向（针对行） ----------
    row_range = gray.max(axis=1) - gray.min(axis=1)          # 每行极差
    row_range = row_range.astype(np.int32)

    row_diff_prev = np.zeros(h, dtype=np.int32)              # 与上一行的平均像素差
    if h > 1:
        row_diff_prev[1:] = np.abs(gray[1:] - gray[:-1]).mean(axis=1).astype(np.int32)

    is_uniform_row = row_range < uniformity_tol
    is_same_block_row = row_diff_prev < uniformity_tol
    is_same_block_row[0] = False                             # 第 0 行永远是段的起点

    # ---------- 垂直方向（针对列） ----------
    col_range = (gray.max(axis=0) - gray.min(axis=0)).astype(np.int32)

    col_diff_prev = np.zeros(w, dtype=np.int32)
    if w > 1:
        col_diff_prev[1:] = np.abs(gray[:, 1:] - gray[:, :-1]).mean(axis=0).astype(np.int32)

    is_uniform_col = col_range < uniformity_tol
    is_same_block_col = col_diff_prev < uniformity_tol
    is_same_block_col[0] = False

    # ---------- 段边界提取 ----------
    def extract_boundaries(is_uniform, is_same_as_prev, min_size):
        n = len(is_uniform)
        boundaries = {0, n}
        i = 0
        while i < n:
            if is_uniform[i]:
                start = i
                j = i + 1
                # 向后延伸：只要还均匀，且与上一行属于同一块
                while j < n and is_uniform[j] and is_same_as_prev[j]:
                    j += 1
                if j - start >= min_size:
                    boundaries.add(start)
                    boundaries.add(j)
                i = j
            else:
                i += 1
        return sorted(boundaries)

    h_candidates = extract_boundaries(
        is_uniform_row, is_same_block_row, min_segment_size)
    v_candidates = extract_boundaries(
        is_uniform_col, is_same_block_col, min_segment_size)

    return h_candidates, v_candidates


class CropInterface(QWidget, Ui_cropInterface):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # 业务状态
        self.image_bgr = None
        self.image_path = None
        self.h_candidates = []
        self.v_candidates = []
        self.original_format = None
        self.original_exif = None
        self.original_quality = None

        # 初始化控件属性（.ui 里无法表达的运行时设置）
        self._init_widgets()
        # 连接信号
        self._connect_signals()

    def _init_widgets(self):
        """补齐 .ui 中无法设置的图标、提示、初始状态"""
        self.btn_load.setIcon(FIF.PHOTO)
        self.btn_reset.setIcon(FIF.SYNC)
        self.btn_save.setIcon(FIF.SAVE)

        self.lbl_info.setTextColor("#aaa", "#aaa")

        self.h_ruler = RulerWidget(Qt.Orientation.Horizontal, self)
        self.v_ruler = RulerWidget(Qt.Orientation.Vertical, self)
        self.canvas = ImageCanvas(self)
        self.grid.addWidget(self.h_ruler, 0, 1)
        self.grid.addWidget(self.v_ruler, 1, 0)
        self.grid.addWidget(self.canvas, 1, 1)

        # SplitPushButton 下拉菜单
        menu = RoundMenu(parent=self.btn_save)
        menu.addAction(Action(
            FIF.SAVE_AS, "另存为...",
            triggered=self._on_save_as
        ))
        self.btn_save.setFlyout(menu)

        # 四个 ComboBox 的最小宽度已在 .ui 设置，这里补上信号以外的初始化
        for combo in (self.v_start_combo, self.v_end_combo,
                      self.h_start_combo, self.h_end_combo):
            combo.setMinimumWidth(180)

    def _connect_signals(self):
        """所有信号绑定保留在代码中"""
        self.btn_load.clicked.connect(self._on_load_image)
        self.btn_reset.clicked.connect(self._on_reset)
        self.btn_save.clicked.connect(self._on_quick_save)

        self.canvas.image_dropped.connect(self._load_image_from_path)
        self.canvas.crop_changed.connect(self._on_canvas_crop_changed)

        self.v_start_combo.currentIndexChanged.connect(self._on_combo_changed)
        self.v_end_combo.currentIndexChanged.connect(self._on_combo_changed)
        self.h_start_combo.currentIndexChanged.connect(self._on_combo_changed)
        self.h_end_combo.currentIndexChanged.connect(self._on_combo_changed)

        self.h_ruler.start_picked.connect(
            lambda v: self._on_ruler_pick('x', 'start', v))
        self.h_ruler.end_picked.connect(
            lambda v: self._on_ruler_pick('x', 'end', v))
        self.h_ruler.pick_cancelled.connect(self._update_info)
        self.v_ruler.start_picked.connect(
            lambda v: self._on_ruler_pick('y', 'start', v))
        self.v_ruler.end_picked.connect(
            lambda v: self._on_ruler_pick('y', 'end', v))
        self.v_ruler.pick_cancelled.connect(self._update_info)

    # ---------------- 加载 ----------------
    def _on_load_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff *.webp);;所有文件 (*)"
        )
        if path:
            self._load_image_from_path(path)

    def _load_image_from_path(self, path):
        try:
            img = cv2.imdecode(np.fromfile(path, dtype=np.uint8),
                               cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("无法解码图片")
            self.image_bgr = img
            self.image_path = path
        except Exception as e:
            InfoBar.error(
                title="加载失败", content=str(e),
                orient=Qt.Orientation.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=3000, parent=self
            )
            return

        self.original_format = None
        self.original_exif = None
        self.original_quality = None

        try:
            with Image.open(path) as pil_img:
                self.original_format = pil_img.format
                self.original_exif = pil_img.info.get('exif')
        except Exception:
            pass

        if self.original_format is None:
            ext = os.path.splitext(path)[1].lower().lstrip('.')
            self.original_format = {
                'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG',
                'bmp': 'BMP', 'tif': 'TIFF', 'tiff': 'TIFF', 'webp': 'WEBP'
            }.get(ext, ext.upper())

        if self.original_format == 'JPEG':
            self.original_quality = estimate_jpeg_quality(path)

        h, w = self.image_bgr.shape[:2]
        rgb = cv2.cvtColor(self.image_bgr, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, w, h, rgb.strides[0],
                      QImage.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(qimg)
        self.canvas.set_image(pixmap)

        # ★ 调用新算法
        self.h_candidates, self.v_candidates = detect_solid_segments(
            self.image_bgr, uniformity_tol=25, min_segment_size=4
        )
        self.canvas.set_candidates(self.h_candidates, self.v_candidates)

        self._populate_combos()
        self._update_crop_from_combos()
        QTimer.singleShot(0, self._update_rulers)
        self._update_info()

        self.btn_save.setEnabled(True)
        self.btn_reset.setEnabled(True)
        self.chk_exif.setEnabled(True)

        InfoBar.success(
            title="加载成功",
            content=f"尺寸 {w}×{h}  格式 {self.original_format}"
                    + (f"  质量≈{self.original_quality}" if self.original_quality else "")
                    + f"  水平吸附点 {len(self.v_candidates)}，"
                      f"竖直吸附点 {len(self.h_candidates)}",
            orient=Qt.Orientation.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=4000, parent=self
        )

    def _populate_combos(self):
        if self.image_bgr is None:
            return
        for combo, candidates, prefix in [
            (self.h_start_combo, self.v_candidates, "列"),
            (self.h_end_combo, self.v_candidates, "列"),
            (self.v_start_combo, self.h_candidates, "行"),
            (self.v_end_combo, self.h_candidates, "行"),
        ]:
            combo.blockSignals(True)
            combo.clear()
            for c in candidates:
                combo.addItem(f"{prefix} {c}", userData=c)
            combo.blockSignals(False)

        if self.v_candidates:
            self.h_start_combo.setCurrentIndex(0)
            self.h_end_combo.setCurrentIndex(len(self.v_candidates) - 1)
        if self.h_candidates:
            self.v_start_combo.setCurrentIndex(0)
            self.v_end_combo.setCurrentIndex(len(self.h_candidates) - 1)

    def _on_combo_changed(self):
        self._update_crop_from_combos()
        self._update_rulers()
        self._update_info()

    def _update_crop_from_combos(self):
        if self.image_bgr is None:
            return
        h, w = self.image_bgr.shape[:2]

        x1 = self.h_start_combo.currentData()
        x2 = self.h_end_combo.currentData()
        y1 = self.v_start_combo.currentData()
        y2 = self.v_end_combo.currentData()

        x1 = x1 if x1 is not None else 0
        x2 = x2 if x2 is not None else w
        y1 = y1 if y1 is not None else 0
        y2 = y2 if y2 is not None else h

        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        self.canvas.crop_x1, self.canvas.crop_y1 = x1, y1
        self.canvas.crop_x2, self.canvas.crop_y2 = x2, y2
        self.canvas.update()

    def _on_ruler_pick(self, axis, which, value):
        if axis == 'x':
            combo = self.h_start_combo if which == 'start' else self.h_end_combo
        else:
            combo = self.v_start_combo if which == 'start' else self.v_end_combo
        self._set_combo_value(combo, value)
        self._normalize_range(axis)
        self._update_crop_from_combos()
        self._update_rulers()
        self._update_info()

    def _normalize_range(self, axis):
        if axis == 'x':
            s_combo, e_combo = self.h_start_combo, self.h_end_combo
        else:
            s_combo, e_combo = self.v_start_combo, self.v_end_combo
        s, e = s_combo.currentData(), e_combo.currentData()
        if s is None or e is None:
            return
        if s > e:
            s_combo.blockSignals(True)
            e_combo.blockSignals(True)
            self._set_combo_value(s_combo, e)
            self._set_combo_value(e_combo, s)
            s_combo.blockSignals(False)
            e_combo.blockSignals(False)

    def _set_combo_value(self, combo, value):
        combo.blockSignals(True)
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                break
        combo.blockSignals(False)

    def _on_canvas_crop_changed(self, x1, y1, x2, y2):
        self._set_combo_value(self.h_start_combo, x1)
        self._set_combo_value(self.h_end_combo, x2)
        self._set_combo_value(self.v_start_combo, y1)
        self._set_combo_value(self.v_end_combo, y2)
        self._update_rulers()
        self._update_info()

    def _update_rulers(self):
        if self.image_bgr is None or self.canvas._pixmap is None:
            self.h_ruler.clear()
            self.v_ruler.clear()
            return

        h, w = self.image_bgr.shape[:2]
        rect, scale = self.canvas._get_display_rect()

        canvas_global = self.canvas.mapToGlobal(QPoint(0, 0))
        h_ruler_global = self.h_ruler.mapToGlobal(QPoint(0, 0))
        v_ruler_global = self.v_ruler.mapToGlobal(QPoint(0, 0))

        h_offset = (canvas_global.x() - h_ruler_global.x()) + rect.x()
        v_offset = (canvas_global.y() - v_ruler_global.y()) + rect.y()

        self.h_ruler.set_params(
            w, h_offset, scale, self.v_candidates,
            self.canvas.crop_x1, self.canvas.crop_x2
        )
        self.v_ruler.set_params(
            h, v_offset, scale, self.h_candidates,
            self.canvas.crop_y1, self.canvas.crop_y2
        )

    def _update_info(self):
        if self.image_bgr is None:
            self.lbl_info.setText("尚未加载图片")
            return
        h, w = self.image_bgr.shape[:2]
        x1, x2 = self.canvas.crop_x1, self.canvas.crop_x2
        y1, y2 = self.canvas.crop_y1, self.canvas.crop_y2
        self.lbl_info.setText(
            f"原始 {w}×{h}  →  裁剪 ({x1},{y1})-({x2},{y2})  "
            f"尺寸 {x2 - x1}×{y2 - y1}"
        )

    def _on_reset(self):
        if self.image_bgr is None:
            return
        self._populate_combos()
        self._update_crop_from_combos()
        self._update_rulers()
        self._update_info()

    # ---------------- 保存 ----------------

    def _get_cropped(self):
        if self.image_bgr is None:
            return None
        x1, y1 = self.canvas.crop_x1, self.canvas.crop_y1
        x2, y2 = self.canvas.crop_x2, self.canvas.crop_y2
        if x2 <= x1 or y2 <= y1:
            InfoBar.warning(
                title="无效区域", content="裁剪区域尺寸为零",
                orient=Qt.Orientation.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=3000, parent=self
            )
            return None
        return self.image_bgr[y1:y2, x1:x2]

    def _on_quick_save(self):
        if self.image_bgr is None or not self.image_path:
            return

        base_name = os.path.splitext(os.path.basename(self.image_path))[0]
        ext = os.path.splitext(self.image_path)[1]
        if not ext:
            ext = '.' + (self.original_format or 'PNG').lower().replace('jpeg', 'jpg')
        out_name = f"crop_{base_name}{ext}"
        out_path = os.path.join(os.path.dirname(self.image_path), out_name)
        self._perform_save(out_path)

    def _on_save_as(self):
        if self.image_bgr is None:
            return

        base = os.path.splitext(os.path.basename(self.image_path or ""))[0] or "image"
        default_ext = '.' + (self.original_format or 'PNG').lower().replace('jpeg', 'jpg')
        default_name = f"crop_{base}{default_ext}"

        save_path, _ = QFileDialog.getSaveFileName(
            self, "另存为", default_name,
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;"
            "TIFF (*.tif *.tiff);;WebP (*.webp);;所有文件 (*)"
        )
        if not save_path:
            return

        ext = os.path.splitext(save_path)[1]
        if not ext:
            save_path += default_ext

        self._perform_save(save_path)

    def _perform_save(self, save_path):
        cropped = self._get_cropped()
        if cropped is None:
            return

        ext = os.path.splitext(save_path)[1].lower().lstrip('.')
        fmt_map = {
            'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG',
            'bmp': 'BMP', 'tif': 'TIFF', 'tiff': 'TIFF', 'webp': 'WEBP'
        }
        out_format = fmt_map.get(ext, ext.upper())
        same_format = (out_format == (self.original_format or ''))
        keep_exif = self.chk_exif.isChecked() and self.original_exif is not None

        try:
            self._save_with_pil(cropped, save_path, out_format,
                                same_format, keep_exif)

            msg = f"已保存到 {os.path.basename(save_path)}"
            extras = []
            if same_format:
                extras.append("保持原画质")
            if keep_exif:
                extras.append("已写入 EXIF")
            if extras:
                msg += "（" + "、".join(extras) + "）"

            InfoBar.success(
                title="保存成功", content=msg,
                orient=Qt.Orientation.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=3000, parent=self
            )
        except Exception as e:
            InfoBar.error(
                title="保存失败", content=str(e),
                orient=Qt.Orientation.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self
            )

    def _save_with_pil(self, cropped_bgr, save_path, out_format,
                       same_format, keep_exif):
        rgb = cv2.cvtColor(cropped_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)

        save_kwargs = {}
        if out_format == 'JPEG':
            if same_format:
                q = self.original_quality if self.original_quality else 95
                save_kwargs['quality'] = q
                save_kwargs['optimize'] = True
            else:
                save_kwargs['quality'] = 90
        elif out_format == 'PNG':
            save_kwargs['compress_level'] = 6
        elif out_format == 'WEBP':
            save_kwargs['quality'] = 95 if same_format else 85

        if keep_exif:
            save_kwargs['exif'] = self.original_exif

        pil_img.save(save_path, format=out_format, **save_kwargs)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._update_rulers)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._update_rulers)
