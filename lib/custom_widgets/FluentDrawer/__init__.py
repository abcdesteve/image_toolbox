# coding: utf-8
"""
FluentDrawer — 基于 QFluentWidgets (PySide6) 的自定义抽屉容器组件

架构:
    FluentDrawer  = 布局占位符（transparent），只负责尺寸/事件
    DrawerPanel   = 视觉本体，与 FluentDrawer 同一父容器的兄弟控件，不在布局中
                    - 挤压模式：Panel geometry 与占位符矩形同步
                    - 悬浮模式：占位符尺寸不动，Panel geometry 扩展到展开尺寸
    Panel 内部 = header + content，content 通过自身几何滑动，超出部分由 Qt 裁剪
"""

from __future__ import annotations
from enum import Enum, Flag, auto

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from qfluentwidgets import *


# ═══════════════════════════════════════════════
# 枚举 / Flag
# ═══════════════════════════════════════════════

class DrawerSide(Enum):
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"


class AutoHideMode(Flag):
    """可叠加的自动隐藏触发模式。用 & 判断。"""
    NONE = 0
    CHECKBOX = auto()   # CheckBox 状态 <-> 展开/收起 双向联动
    HOVER = auto()      # 鼠标进入/离开（悬浮模式展开）
    FOCUS = auto()      # 全局鼠标按下：内展开/外收起


# ═══════════════════════════════════════════════
# 旋转文本 Label
# ═══════════════════════════════════════════════

class RotatedLabel(BodyLabel):
    def __init__(self, text="", angle=0, parent=None):
        super().__init__(text)
        if parent is not None:
            self.setParent(parent)
        self._angle = angle
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def setAngle(self, angle):
        if self._angle == angle:
            return
        self._angle = angle
        if angle in (90, -90):
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.updateGeometry()
        self.update()

    def paintEvent(self, event):
        if self._angle == 0:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = float(self.width())
        h = float(self.height())
        painter.translate(w / 2.0, h / 2.0)
        painter.rotate(self._angle)
        painter.setPen(self.palette().color(QPalette.ColorRole.WindowText))
        painter.setFont(self.font())

        painter.drawText(QRectF(-h / 2.0, -w / 2.0, h, w), Qt.AlignmentFlag.AlignCenter, self.text())

    def sizeHint(self):
        hint = super().sizeHint()
        if self._angle in (90, -90):
            return QSize(hint.height(), hint.width())
        return hint

    def minimumSizeHint(self):
        hint = super().minimumSizeHint()
        if self._angle in (90, -90):
            return QSize(hint.height(), hint.width())
        return hint


# ═══════════════════════════════════════════════
# 拖动手柄
# ═══════════════════════════════════════════════

class DrawerSplitterHandle(QFrame):
    GRIP_SPACING = 5
    HANDLE_THICKNESS = 8

    dragStarted = Signal()
    dragMoved = Signal(QPoint)
    dragFinished = Signal()

    def __init__(self, orientation, parent=None):
        super().__init__(parent)
        self._orientation = orientation
        self._hovered = False
        self._dragging = False

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        if orientation == Qt.Orientation.Vertical:
            self.setCursor(Qt.CursorShape.SplitHCursor)
        else:
            self.setCursor(Qt.CursorShape.SplitVCursor)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("DrawerSplitterHandle { background: transparent; border: none; }")

        if orientation == Qt.Orientation.Horizontal:
            self.setFixedHeight(self.HANDLE_THICKNESS)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            self.setFixedWidth(self.HANDLE_THICKNESS)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2

        if self._hovered or self._dragging:
            bg = QColor(255, 255, 255, 40) if isDarkTheme() else QColor(0, 0, 0, 20)
            painter.setBrush(QBrush(bg))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(1, 1, w - 2, h - 2, 3, 3)

        grip = QColor(255, 255, 255, 160) if isDarkTheme() else QColor(0, 0, 0, 110)
        painter.setBrush(QBrush(grip))
        painter.setPen(Qt.PenStyle.NoPen)

        s = self.GRIP_SPACING
        radius = 2
        if self._orientation == Qt.Orientation.Vertical:
            start_y = cy - s
            for i in range(3):
                painter.drawEllipse(QPoint(int(cx), int(start_y + i * s)), radius, radius)
        else:
            start_x = cx - s
            for i in range(3):
                painter.drawEllipse(QPoint(int(start_x + i * s), int(cy)), radius, radius)

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self.dragStarted.emit()
            self.update()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging:
            self.dragMoved.emit(event.globalPosition().toPoint())
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            self.dragFinished.emit()
            self.update()
            event.accept()


# ═══════════════════════════════════════════════
# 视觉面板
# ═══════════════════════════════════════════════

class DrawerPanel(QFrame):
    def __init__(self, drawer:FluentDrawer, parent):
        super().__init__(parent)
        self._drawer = drawer
        self._shadow_on = False

        self.setObjectName("drawerPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(False)
        self.setFrameShape(QFrame.Shape.NoFrame)

        # ── header ──
        self._headerFrame = QFrame(self)
        self._headerFrame.setObjectName("drawerHeader")
        self._headerFrame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._headerFrame.setAutoFillBackground(False)
        self._headerLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight, self._headerFrame)
        self._headerLayout.setContentsMargins(14, 14, 14, 14)
        self._headerLayout.setSpacing(8)

        self._checkbox = None
        if drawer._checkbox_visible:
            self._checkbox = CheckBox(self._headerFrame)
            self._checkbox.setChecked(False)
            self._headerLayout.addWidget(self._checkbox, 0, Qt.AlignmentFlag.AlignCenter)

        self._titleLabel = RotatedLabel(drawer._title, 0, self._headerFrame)
        self._titleLabel.setObjectName("drawerTitle")
        self._headerLayout.addWidget(self._titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self._headerLayout.addStretch(1)
        self._headerFrame.setVisible(bool(drawer._title) or drawer._checkbox_visible)

        # ── content ──
        self._contentFrame = QFrame(self)
        self._contentFrame.setObjectName("drawerContent")
        self._contentFrame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._contentFrame.setAutoFillBackground(False)
        self._contentLayout = QVBoxLayout(self._contentFrame)
        self._contentLayout.setContentsMargins(*drawer._content_margins)
        self._contentLayout.setSpacing(drawer._content_spacing)

        # ── 拖动手柄 ──
        self._splitterHandle = None
        if drawer._resizable:
            orientation = Qt.Orientation.Vertical if drawer._is_horizontal else Qt.Orientation.Horizontal
            self._splitterHandle = DrawerSplitterHandle(orientation, self)
            self._splitterHandle.dragStarted.connect(drawer._onSplitterDragStart)
            self._splitterHandle.dragMoved.connect(drawer._onSplitterDrag)
            self._splitterHandle.dragFinished.connect(drawer._onSplitterDragFinish)

        self.setStyleSheet(
            "#drawerPanel, #drawerHeader, #drawerContent, #drawerTitle {"
            " background: transparent; border: none; }"
            "#drawerPanel CheckBox { background: transparent; }"
        )
        self.hide()

    # ── 公共访问 ──

    def contentLayout(self):
        return self._contentLayout

    def headerWidget(self):
        return self._headerFrame

    def checkbox(self):
        return self._checkbox

    def contentFrame(self):
        return self._contentFrame

    def syncGeometry(self, rect: QRect):
        if self.geometry() != rect:
            self.setGeometry(rect)
        self.raise_()

    def setHandleVisible(self, visible: bool):
        if self._splitterHandle is not None:
            self._splitterHandle.setVisible(visible)

    # ── header 布局切换 ──

    def applyHeaderLayout(self, expanded):
        side = self._drawer._side
        is_h = self._drawer._is_horizontal
        has_cb = self._checkbox is not None
        title = self._drawer._title

        def configure_checkbox(text, fixed_w=None):
            self._checkbox.setText(text)
            if fixed_w is not None:
                self._checkbox.setFixedWidth(fixed_w)
            else:
                self._checkbox.setMinimumWidth(0)
                self._checkbox.setMaximumWidth(16777215)
            self._checkbox.updateGeometry()
            self._headerLayout.setAlignment(self._checkbox, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        def configure_title(angle=0, fixed_w=None):
            self._titleLabel.setVisible(True)
            self._titleLabel.setAngle(angle)
            if fixed_w is not None:
                self._titleLabel.setFixedWidth(fixed_w)
            else:
                self._titleLabel.setMinimumWidth(0)
                self._titleLabel.setMaximumWidth(16777215)
            self._titleLabel.updateGeometry()

        if expanded:
            self._headerLayout.setDirection(QBoxLayout.Direction.LeftToRight)
            self._headerLayout.setContentsMargins(14, 14, 14, 14)
            self._headerLayout.setSpacing(8)
            if has_cb:
                configure_checkbox(title)
                self._titleLabel.setVisible(False)
            else:
                configure_title()
        else:
            if is_h:
                self._headerLayout.setDirection(QBoxLayout.Direction.TopToBottom)
                self._headerLayout.setContentsMargins(14, 14, 14, 14)
                self._headerLayout.setSpacing(6)
                if has_cb:
                    configure_checkbox("", fixed_w=22)
                configure_title(angle=90 if side == DrawerSide.LEFT else -90, fixed_w=22)
                self._headerLayout.setAlignment(self._titleLabel, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            else:
                self._headerLayout.setDirection(QBoxLayout.Direction.LeftToRight)
                self._headerLayout.setContentsMargins(14, 14, 14, 14)
                self._headerLayout.setSpacing(8)
                if has_cb:
                    configure_checkbox(title)
                    self._titleLabel.setVisible(False)
                else:
                    configure_title()

        self._headerLayout.invalidate()
        self._headerLayout.activate()
        self._repositionHeader()
        self._repositionContent()

    # ── 布局定位 ──

    def _repositionHeader(self):
        if self._headerFrame.isHidden():
            return
        hint = self._headerFrame.sizeHint()
        h_h = hint.height() if hint.height() > 0 else 40
        self._headerFrame.setGeometry(0, 0, max(self.width(), 1), h_h)

    def _repositionContent(self):
        side = self._drawer._side
        exp = self._drawer._expanded_size
        col = self._drawer._collapsed_size
        pw = self.width()
        ph = self.height()
        header_h = self._headerFrame.height() if not self._headerFrame.isHidden() else 0

        def progress(cur, lo, hi):
            if hi <= lo:
                return 1.0
            return max(0.0, min(1.0, (cur - lo) / (hi - lo)))

        if self._drawer._is_horizontal:
            c_w = exp
            c_h = max(ph - header_h, 0)
            c_y = header_h
            t = progress(pw, col, exp)
            c_x = int(-exp * (1.0 - t)) if side == DrawerSide.LEFT else int(exp * (1.0 - t))
        else:
            c_w = pw
            c_h = max(exp - header_h, 0)
            c_x = 0
            t = progress(ph, col, exp)
            offset = int(exp * (1.0 - t))
            c_y = header_h + (-offset if side == DrawerSide.TOP else offset)

        self._contentFrame.setGeometry(c_x, c_y, c_w, c_h)

    def _repositionHandle(self):
        if self._splitterHandle is None:
            return
        th = DrawerSplitterHandle.HANDLE_THICKNESS
        pw = self.width()
        ph = self.height()
        side = self._drawer._side
        if side == DrawerSide.LEFT:
            self._splitterHandle.setGeometry(pw - th, 0, th, ph)
        elif side == DrawerSide.RIGHT:
            self._splitterHandle.setGeometry(0, 0, th, ph)
        elif side == DrawerSide.TOP:
            self._splitterHandle.setGeometry(0, ph - th, pw, th)
        else:
            self._splitterHandle.setGeometry(0, 0, pw, th)

    def showEvent(self, event):
        super().showEvent(event)
        self._repositionHeader()
        self._repositionContent()
        self._repositionHandle()

    def resizeEvent(self, event):
        self._repositionHeader()
        self._repositionContent()
        self._repositionHandle()
        super().resizeEvent(event)

    # ── 阴影（仅悬浮态） ──

    def enableShadow(self):
        if self._shadow_on:
            return
        self._shadow_on = True
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(40)
        effect.setColor(QColor(0, 0, 0, 80) if isDarkTheme() else QColor(0, 0, 0, 40))
        side = self._drawer._side
        offset = {
            DrawerSide.LEFT: (8, 0),
            DrawerSide.RIGHT: (-8, 0),
            DrawerSide.TOP: (0, 8),
            DrawerSide.BOTTOM: (0, -8),
        }[side]
        effect.setOffset(*offset)
        self.setGraphicsEffect(effect)
        self.raise_()

    def disableShadow(self):
        if not self._shadow_on:
            return
        self._shadow_on = False
        self.setGraphicsEffect(None)

    # ── 绘制 ──

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        rect = QRectF(self.rect())
        r = 8.0
        is_dark = isDarkTheme()
        tint = QColor(40, 40, 40, 235) if is_dark else QColor(245, 245, 245, 235)
        noise_alpha = 10 if is_dark else 8

        path = QPainterPath()
        path.addRoundedRect(rect, r, r)
        painter.fillPath(path, tint)
        self._draw_noise(painter, rect, r, noise_alpha)

        pen_w = 1.0
        inset = pen_w / 2.0
        border_rect = rect.adjusted(inset, inset, -inset, -inset)
        border_r = r - inset
        border_color = QColor(255, 255, 255, 22) if is_dark else QColor(0, 0, 0, 18)

        pen = QPen(border_color)
        pen.setWidthF(pen_w)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self._build_edge_path(border_rect, border_r))

    def _draw_noise(self, painter, rect, r, alpha):
        pm = QPixmap(64, 64)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        rng = QRandomGenerator(0xA57C0FF)
        fg = QColor(255, 255, 255) if isDarkTheme() else QColor(0, 0, 0)
        for _ in range(280):
            x = rng.bounded(64)
            y = rng.bounded(64)
            c = QColor(fg)
            c.setAlpha(rng.bounded(alpha) + 1)
            p.setPen(c)
            p.drawPoint(x, y)
        p.end()

        path = QPainterPath()
        path.addRoundedRect(rect, r, r)
        painter.save()
        painter.setClipPath(path)
        painter.setOpacity(0.5)
        painter.fillRect(rect, QBrush(pm))
        painter.restore()

    def _build_edge_path(self, rect: QRectF, r: float) -> QPainterPath:
        """非贴靠侧边 + 相邻两端圆角的描边路径"""
        p = QPainterPath()
        side = self._drawer._side
        d = 2.0 * r
        L, T, R, B = rect.left(), rect.top(), rect.right(), rect.bottom()

        if side == DrawerSide.LEFT:
            p.arcMoveTo(QRectF(R - d, T, d, d), 90)
            p.arcTo(QRectF(R - d, T, d, d), 90, -90)
            p.arcTo(QRectF(R - d, B - d, d, d), 0, -90)
        elif side == DrawerSide.RIGHT:
            p.arcMoveTo(QRectF(L, T, d, d), 90)
            p.arcTo(QRectF(L, T, d, d), 90, 90)
            p.arcTo(QRectF(L, B - d, d, d), 180, 90)
        elif side == DrawerSide.TOP:
            p.arcMoveTo(QRectF(L, B - d, d, d), 180)
            p.arcTo(QRectF(L, B - d, d, d), 180, 90)
            p.arcTo(QRectF(R - d, B - d, d, d), 270, 90)
        else:
            p.arcMoveTo(QRectF(L, T, d, d), 180)
            p.arcTo(QRectF(L, T, d, d), 180, -90)
            p.arcTo(QRectF(R - d, T, d, d), 90, -90)
        return p


# ═══════════════════════════════════════════════
# 主组件（占位符 + 管理器）
# ═══════════════════════════════════════════════

class FluentDrawer(QFrame):
    """
    Fluent 风格抽屉容器（本体是布局占位符）。

    注意:
        side 只是"标识"—— 决定圆角方向、拖动手柄所在边、收起形态，
        不会自动改变抽屉在父布局中的位置。请自行用布局摆放。
    """

    expanded = Signal()
    collapsed = Signal()
    checkboxStateChanged = Signal(bool)

    MIN_EXPANDED_SIZE = 120
    DEFAULT_EXPANDED_SIZE = 280
    MIN_COLLAPSED_SIZE = 40

    def __init__(
        self,
        title: str,
        side: DrawerSide ,
        parent:QWidget,
        content:QWidget|QLayout=None,
        *,
        checkbox_visible: bool = False,
        autohide: AutoHideMode = AutoHideMode.NONE,
        animated: bool = True,
        resizable: bool = False,
        expanded: bool = True,
        content_enabled:bool=True,
        content_margins: tuple = (16, 14, 16, 14),
        content_spacing: int = 10,
    ):
        '在启用了AutoHideMode.HOVER时expanded设置会失效'
        super().__init__(parent)
        self._title = title
        self._side = side
        self._checkbox_visible = checkbox_visible
        self._autohide = autohide
        self._animated = animated
        self._resizable = resizable

        # 状态变量
        self._is_animating = False
        self._expanded_size = self.DEFAULT_EXPANDED_SIZE
        self._collapsed_size = self.MIN_COLLAPSED_SIZE
        self._content_margins = content_margins
        self._content_spacing = content_spacing
        self._drag_last_pos = None
        self._anim = None
        self._panel = None
        self._floating_active = False
        self._hover_timer = None
        self._dragging = False
        self._hover_block_until_leave = False
        self._is_horizontal = side in (DrawerSide.LEFT, DrawerSide.RIGHT)

        self.setObjectName("fluentDrawerPlaceholder")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setAutoFillBackground(False)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("#fluentDrawerPlaceholder { background: transparent; border: none; }")

        if self._is_horizontal:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._setPlaceholderSize(self._expanded_size if expanded else self.MIN_COLLAPSED_SIZE)
        self._expanded = False # 初始状态，在init最后设置
        self._ensurePanel()
        if content is not None:
            if isinstance(content, QWidget):
                self.contentLayout().addWidget(content)
            elif isinstance(content, QLayout):
                self.contentLayout().addLayout(content)

        self.setContentEnabled(content_enabled)
        if expanded and not (autohide&AutoHideMode.HOVER):
            QTimer.singleShot(100,lambda:self.expand(floating=False,sync_checkbox=False))

    # ─────────────────────────────────────────
    # Panel 生命周期
    # ─────────────────────────────────────────

    def _ensurePanel(self):
        if self._panel is not None:
            return
        parent = self.parentWidget()

        self._panel = DrawerPanel(self, parent)
        if self._panel.checkbox() is not None:
            self._panel.checkbox().stateChanged.connect(self._onCheckboxChanged)

        init = self._expanded_size if self._expanded else self._collapsed_size
        self._panel.applyHeaderLayout(self._expanded)
        self._panel.syncGeometry(self._computePanelRect(init))
        self._panel.show()
        self._panel.raise_()

        qconfig.themeChanged.connect(self._onThemeChanged)
        self._initAutohide()

        if not self._expanded:
            self._applyExpandedState(animated=False)

    def event(self, e:QEvent):
        if e.type() == QEvent.Type.ParentChange:
            QTimer.singleShot(0, self._ensurePanel)
        elif e.type() in (QEvent.Type.Move, QEvent.Type.Resize):
            if self._panel is not None:
                self._syncPanelFollowPlaceholder()
        elif e.type()== QEvent.Type.EnabledChange:
            try:
                self._panel.checkbox().setEnabled(self.isEnabled())
            except:pass
        return super().event(e)

    def _syncPanelFollowPlaceholder(self):
        if self._panel is None or self._is_animating:
            return
        if self._floating_active:
            target = self._expanded_size if self._expanded else self._collapsed_size
            self._panel.syncGeometry(self._computePanelRect(target))
        else:
            cur = self.width() if self._is_horizontal else self.height()
            if cur <= 0:
                return
            self._panel.syncGeometry(self._computePanelRect(cur))

    def _computePanelRect(self, size: int) -> QRect:
        side = self._side
        pos = self.pos()
        pw = max(self.width(), 1)
        ph = max(self.height(), 1)

        if self._is_horizontal:
            if side == DrawerSide.LEFT:
                return QRect(pos.x(), pos.y(), size, ph)
            return QRect(pos.x() + pw - size, pos.y(), size, ph)
        if side == DrawerSide.TOP:
            return QRect(pos.x(), pos.y(), pw, size)
        return QRect(pos.x(), pos.y() + ph - size, pw, size)

    # ─────────────────────────────────────────
    # 主题 / CheckBox
    # ─────────────────────────────────────────

    def _onThemeChanged(self, *_):
        def refresh():
            if self._panel is not None:
                self._panel.update()
        QTimer.singleShot(0, refresh)

    def _onCheckboxChanged(self, _state):
        if not self.isEnabled():
            return
        checked = self._panel.checkbox().isChecked()
        self.setContentEnabled(checked)
        self.checkboxStateChanged.emit(checked)
        if not (self._autohide & AutoHideMode.CHECKBOX):
            return
        if checked:
            self._hover_block_until_leave = False
            if not self._expanded:
                self.expand(floating=False)
            elif self._floating_active:
                self._switch_floating(False)
        else:
            if self._expanded:
                if self._autohide & AutoHideMode.HOVER:
                    self._hover_block_until_leave = True
                self.collapse(floating=False)

    def _setCheckboxSilently(self, checked: bool):
        cb = self._panel.checkbox() if self._panel is not None else None
        if cb is None or cb.isChecked() == checked:
            return
        cb.blockSignals(True)
        cb.setChecked(checked)
        cb.blockSignals(False)
        self.setContentEnabled(checked)

    # ─────────────────────────────────────────
    # Autohide
    # ─────────────────────────────────────────

    def _initAutohide(self):
        app = QApplication.instance()
        for target in (app, self):
            try:
                target.removeEventFilter(self)
            except (TypeError, RuntimeError):
                pass

        if self._autohide & AutoHideMode.FOCUS:
            app.installEventFilter(self)

        if self._autohide & AutoHideMode.HOVER:
            if self._hover_timer is None:
                self._hover_timer = QTimer(self)
                self._hover_timer.setInterval(100)
                self._hover_timer.timeout.connect(self._checkHover)
            self._hover_timer.start()
        elif self._hover_timer is not None:
            self._hover_timer.stop()

    def _checkHover(self):
        if not self.isEnabled():
            return
        if self._dragging:
            return
        if self._panel is None or not self._panel.isVisible():
            return
        if not (self._autohide & AutoHideMode.HOVER):
            return

        gp = QCursor.pos()
        top = QApplication.widgetAt(gp)
        on_our_window = top is not None and top.window() is self.window()

        # 收起态只认折叠矩形，展开态才用展开矩形，避免缩回途中被误触重开
        detect_size = self._expanded_size if self._expanded else self._collapsed_size
        inside = False
        if on_our_window:
            parent = self.parentWidget()
            if parent is not None:
                local = parent.mapFromGlobal(gp)
                inside = self._computePanelRect(detect_size).contains(local)

        if self._autohide & AutoHideMode.CHECKBOX:
            cb = self._panel.checkbox()
            if cb is not None and cb.isChecked():
                return

        if self._hover_block_until_leave:
            if not inside:
                self._hover_block_until_leave = False
            return

        if self._expanded:
            if not inside:
                self.collapse(floating=True, sync_checkbox=False)
        else:
            if inside:
                self.expand(floating=True, sync_checkbox=False)

    def eventFilter(self, obj, event:QEvent):
        if not self.isEnabled():
            return super().eventFilter(obj, event)
        if not (self._autohide & AutoHideMode.FOCUS):
            return super().eventFilter(obj, event)
        if event.type() != QEvent.Type.MouseButtonPress:
            return super().eventFilter(obj, event)
        if event.button() != Qt.MouseButton.LeftButton:
            return super().eventFilter(obj, event)
        if self._panel is None or not self._panel.isVisible():
            return super().eventFilter(obj, event)

        parent = self.parentWidget()
        if parent is None:
            return super().eventFilter(obj, event)

        gp = event.globalPosition().toPoint()

        # 点击落在 ckb 上 → 交给 ckb 自己处理，stateChanged 会驱动展开/收起
        cb = self._panel.checkbox()
        if cb is not None and cb.isVisible():
            if QRect(cb.mapToGlobal(QPoint(0, 0)), cb.size()).contains(gp):
                return super().eventFilter(obj, event)

        detect_size = self._expanded_size if self._expanded else self._collapsed_size
        detect_rect = self._computePanelRect(detect_size)
        top_left_global = parent.mapToGlobal(detect_rect.topLeft())
        inside = QRect(top_left_global, detect_rect.size()).contains(gp)

        if inside:
            self.expand(floating=False)
        elif self._expanded:
            self.collapse(floating=False)

        return super().eventFilter(obj, event)

    # ─────────────────────────────────────────
    # 展开 / 收起
    # ─────────────────────────────────────────

    def expand(self, *, floating=False, sync_checkbox=True):
        if not self.isEnabled():
            return
        if self._expanded:
            if floating != self._floating_active:
                self._switch_floating(floating)
            if sync_checkbox and (self._autohide & AutoHideMode.CHECKBOX):
                self._setCheckboxSilently(True)
            return

        self._stopAnimation()
        self._expanded = True
        self._floating_active = floating

        # 纯 HOVER（无 CHECKBOX）触发展开时，首次给 enable；之后 hover 不再管 enable
        if floating and not (self._autohide & AutoHideMode.CHECKBOX) and not self._content_enabled:
            self.setContentEnabled(True)

        if sync_checkbox and (self._autohide & AutoHideMode.CHECKBOX):
            self._setCheckboxSilently(True)

        self._applyExpandedState(animated=self._animated)
        self.expanded.emit()

    def collapse(self, *, floating=None, sync_checkbox=True):
        if not self.isEnabled():
            return
        if not self._expanded and not self._is_animating:
            return
        self._stopAnimation()
        self._expanded = False
        if floating is None:
            floating = self._floating_active
        self._floating_active = floating

        if sync_checkbox and (self._autohide & AutoHideMode.CHECKBOX):
            self._setCheckboxSilently(False)

        self._applyExpandedState(animated=self._animated)
        self.collapsed.emit()

    def toggle(self, *, floating=False):
        if self._expanded:
            self.collapse(floating=floating)
        else:
            self.expand(floating=floating)

    def _stopAnimation(self):
        if self._anim is not None:
            try:
                self._anim.stop()
            except RuntimeError:
                pass
            self._anim = None
        self._is_animating = False

    def _setPlaceholderSize(self, size: int):
        if self._is_horizontal:
            self.setMinimumWidth(size)
            self.setMaximumWidth(size)
        else:
            self.setMinimumHeight(size)
            self.setMaximumHeight(size)

    def _setPanelRect(self, size: int):
        if self._panel is not None:
            self._panel.syncGeometry(self._computePanelRect(size))

    def _run_size_animation(self, start, end, duration, on_value, on_finish):
        """尺寸动画骨架：调用方提供 on_value / on_finish。"""
        self._stopAnimation()
        self._is_animating = True
        anim = QVariantAnimation(self)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(int(start))
        anim.setEndValue(int(end))
        anim.valueChanged.connect(on_value)
        anim.finished.connect(on_finish)
        anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        self._anim = anim

    def _applyExpandedState(self, animated: bool):
        if self._panel is None:
            return

        if not self._expanded:
            # 临时切到收起布局量取 collapsed_size，动画期间保持展开布局，旋转留到动画结束后
            self._panel.setUpdatesEnabled(False)
            self._panel.applyHeaderLayout(False)
            hdr = self._panel.headerWidget()
            # isVisible在show之前为False，会导致第一次尺寸计算被跳过，改为isHidden只会在hide之后为True
            if hdr is not None and not hdr.isHidden():
                if self._is_horizontal:
                    self._collapsed_size = max(hdr.sizeHint().width(), self.MIN_COLLAPSED_SIZE)
                else:
                    self._collapsed_size = max(hdr.sizeHint().height(), self.MIN_COLLAPSED_SIZE)
            self._panel.applyHeaderLayout(True)
            self._panel.setUpdatesEnabled(True)
        else:
            self._panel.applyHeaderLayout(True)

        target = self._expanded_size if self._expanded else self._collapsed_size
        floating_anim = self._floating_active
        floating_display = self._floating_active and self._expanded

        if self._expanded:
            self._panel.contentFrame().setVisible(True)

        if floating_display:
            self._panel.enableShadow()
        else:
            self._panel.disableShadow()

        if not animated:
            self._is_animating = False
            if floating_anim:
                self._setPlaceholderSize(self._collapsed_size)
            else:
                self._setPlaceholderSize(target)
            self._setPanelRect(target)
            if not self._expanded:
                self._panel.contentFrame().setVisible(False)
                self._panel.applyHeaderLayout(False)
            self._panel.setHandleVisible(self._expanded)
            return

        self._panel.setHandleVisible(False)
        self._animateTo(target, floating_anim, rotate_header_at_end=not self._expanded)

    def _animateTo(self, target: int, floating: bool, rotate_header_at_end: bool = False):
        if floating:
            self._setPlaceholderSize(self._collapsed_size)
            current = (self._panel.width() if self._is_horizontal else self._panel.height()) if self._panel else self._collapsed_size
        else:
            current = self.width() if self._is_horizontal else self.height()

        def on_value(v):
            v = int(v)
            if floating:
                self._setPanelRect(v)
            else:
                self._setPlaceholderSize(v)
                self._setPanelRect(v)

        def on_finished():
            self._is_animating = False
            if floating:
                self._setPanelRect(target)
            else:
                self._setPlaceholderSize(target)
                self._setPanelRect(target)
            if not self._expanded:
                self._panel.contentFrame().setVisible(False)
                if rotate_header_at_end:
                    self._panel.applyHeaderLayout(False)
            self._panel.setHandleVisible(self._expanded)
            self._anim = None

        self._run_size_animation(current, target, 250, on_value, on_finished)

    def _switch_floating(self, to_floating: bool):
        """悬浮 <-> 挤压 切换：占位符动画，Panel 锁定展开尺寸。"""
        if self._floating_active == to_floating:
            return
        self._floating_active = to_floating
        if to_floating:
            self._panel.enableShadow()
        else:
            self._panel.disableShadow()

        target = self._collapsed_size if to_floating else self._expanded_size

        def apply_final():
            self._setPlaceholderSize(target)
            self._setPanelRect(self._expanded_size)

        if not self._animated:
            apply_final()
            return

        current = self.width() if self._is_horizontal else self.height()

        def on_value(v):
            self._setPlaceholderSize(int(v))
            self._setPanelRect(self._expanded_size)

        def on_finished():
            apply_final()
            self._anim = None
            self._is_animating = False

        self._run_size_animation(current, target, 250, on_value, on_finished)

    # ─────────────────────────────────────────
    # 拖拽
    # ─────────────────────────────────────────

    def _onSplitterDragStart(self):
        if not self.isEnabled():
            return
        if not self._expanded:
            return
        self._drag_last_pos = None
        self._dragging = True
        self._stopAnimation()

    def _onSplitterDrag(self, global_pos):
        if not self._expanded or not self._dragging:
            return
        if self._drag_last_pos is None:
            self._drag_last_pos = global_pos
            return
        delta = global_pos - self._drag_last_pos
        self._drag_last_pos = global_pos

        cur = (self._panel.width() if self._is_horizontal else self._panel.height()) if self._panel else self._expanded_size

        parent = self.parentWidget()
        ref_w, ref_h = (parent.width(), parent.height()) if parent is not None else (0, 0)
        window = self.window()
        if window is not None and window is not self:
            if window.width() > 0:
                ref_w = window.width() if ref_w <= 0 else min(ref_w, window.width())
            if window.height() > 0:
                ref_h = window.height() if ref_h <= 0 else min(ref_h, window.height())

        base = (ref_w if ref_w > 0 else 800) if self._is_horizontal else (ref_h if ref_h > 0 else 600)
        max_size = max(self.MIN_EXPANDED_SIZE, int(base * 0.8))

        side = self._side
        if side == DrawerSide.LEFT:
            new_total = cur + delta.x()
        elif side == DrawerSide.RIGHT:
            new_total = cur - delta.x()
        elif side == DrawerSide.TOP:
            new_total = cur + delta.y()
        else:
            new_total = cur - delta.y()

        new_total = max(self.MIN_EXPANDED_SIZE, min(new_total, max_size))
        self._expanded_size = new_total

        if self._floating_active:
            self._setPanelRect(new_total)
        else:
            self._setPlaceholderSize(new_total)
            self._setPanelRect(new_total)

    def _onSplitterDragFinish(self):
        self._drag_last_pos = None
        self._dragging = False

    # ─────────────────────────────────────────
    # 公共 API
    # ─────────────────────────────────────────

    def contentLayout(self):
        if self._panel is None:
            self._ensurePanel()
        return self._panel.contentLayout()

    def setContentEnabled(self, enabled: bool):
        self._content_enabled = enabled
        if self._panel is not None:
            self._panel.contentFrame().setEnabled(enabled)
            self._panel.headerWidget().setEnabled(True)
            if self.checkbox().isChecked()!= enabled:
                if self._autohide&AutoHideMode.CHECKBOX:
                    self.checkbox().setChecked(enabled)
                else:
                    self._setCheckboxSilently(enabled)

    def isContentEnabled(self):
        return self._content_enabled

    def setTitle(self, title):
        self._title = title
        if self._panel is not None:
            self._panel._titleLabel.setText(title)
            cb = self._panel.checkbox()
            if cb is not None:
                cb.setText(title)
            self._panel.headerWidget().setVisible(bool(title) or self._checkbox_visible)

    def title(self):
        return self._title

    def setAnimated(self, animated: bool):
        self._animated = animated

    def isAnimated(self):
        return self._animated

    def setAutohide(self, mode: AutoHideMode):
        self._autohide = mode
        self._initAutohide()

    def autohide(self):
        return self._autohide

    def isExpanded(self):
        return self._expanded

    def setExpandedSize(self, size: int):
        size = max(self.MIN_EXPANDED_SIZE, size)
        if size == self._expanded_size:
            return
        self._expanded_size = size
        if not self._expanded or self._panel is None:
            return

        floating = self._floating_active

        def apply_final():
            if floating:
                self._setPanelRect(size)
            else:
                self._setPlaceholderSize(size)
                self._setPanelRect(size)

        if not self._animated:
            apply_final()
            return

        if floating:
            current = self._panel.width() if self._is_horizontal else self._panel.height()
        else:
            current = self.width() if self._is_horizontal else self.height()

        def on_value(v):
            v = int(v)
            if floating:
                self._setPanelRect(v)
            else:
                self._setPlaceholderSize(v)
                self._setPanelRect(v)

        def on_finished():
            apply_final()
            self._anim = None
            self._is_animating = False

        self._run_size_animation(current, size, 200, on_value, on_finished)

    def expandedSize(self):
        return self._expanded_size

    def checkbox(self):
        return self._panel.checkbox() if self._panel is not None else None

    def headerWidget(self):
        return self._panel.headerWidget() if self._panel is not None else None

    def panel(self):
        return self._panel

    def side(self):
        return self._side
