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
        """设置文字旋转角度（0 / 90 / -90）。0 时退回普通 BodyLabel 绘制。"""
        if self._angle == angle:
            return
        self._angle = angle
        self.setAlignment(Qt.AlignmentFlag.AlignCenter if angle in (90, -90) else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.updateGeometry()
        self.update()

    def paintEvent(self, event: QPaintEvent):
        if self._angle == 0:
            return super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        w, h = float(self.width()), float(self.height())
        p.translate(w / 2.0, h / 2.0)
        p.rotate(self._angle)
        p.setPen(self.palette().color(QPalette.ColorRole.WindowText))
        p.setFont(self.font())
        p.drawText(QRectF(-h / 2.0, -w / 2.0, h, w), Qt.AlignmentFlag.AlignCenter, self.text())

    def _rotatedSize(self, hint):
        return QSize(hint.height(), hint.width()) if self._angle in (90, -90) else hint

    def sizeHint(self): return self._rotatedSize(super().sizeHint())
    def minimumSizeHint(self): return self._rotatedSize(super().minimumSizeHint())


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
        self.setCursor(Qt.CursorShape.SplitHCursor if orientation == Qt.Orientation.Vertical else Qt.CursorShape.SplitVCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("DrawerSplitterHandle { background: transparent; border: none; }")
        if orientation == Qt.Orientation.Horizontal:
            self.setFixedHeight(self.HANDLE_THICKNESS)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            self.setFixedWidth(self.HANDLE_THICKNESS)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

    def paintEvent(self, event: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        # 悬停 / 拖拽时先画背景高亮块
        if self._hovered or self._dragging:
            p.setBrush(QBrush(QColor(255, 255, 255, 40) if isDarkTheme() else QColor(0, 0, 0, 20)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(1, 1, w - 2, h - 2, 3, 3)
        # 三点抓手
        p.setBrush(QBrush(QColor(255, 255, 255, 160) if isDarkTheme() else QColor(0, 0, 0, 110)))
        p.setPen(Qt.PenStyle.NoPen)
        s, r = self.GRIP_SPACING, 2
        if self._orientation == Qt.Orientation.Vertical:
            for i in range(3):
                p.drawEllipse(QPoint(int(cx), int(cy - s + i * s)), r, r)
        else:
            for i in range(3):
                p.drawEllipse(QPoint(int(cx - s + i * s), int(cy)), r, r)

    def enterEvent(self, e): self._hovered = True; self.update(); super().enterEvent(e)
    def leaveEvent(self, e): self._hovered = False; self.update(); super().leaveEvent(e)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self.dragStarted.emit()
            self.update()
            e.accept()

    def mouseMoveEvent(self, e: QMouseEvent):
        if self._dragging:
            self.dragMoved.emit(e.globalPosition().toPoint())
            e.accept()

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            self.dragFinished.emit()
            self.update()
            e.accept()


# ═══════════════════════════════════════════════
# 视觉面板
# ═══════════════════════════════════════════════

class DrawerPanel(QFrame):
    """抽屉的视觉本体，与占位符同父容器、不在布局中。几何由 FluentDrawer 驱动。"""

    def __init__(self, drawer, parent):
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

        self._checkbox = CheckBox(self._headerFrame) if drawer._checkbox_visible else None
        if self._checkbox is not None:
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

        self.setStyleSheet("#drawerPanel, #drawerHeader, #drawerContent, #drawerTitle { background: transparent; border: none; } #drawerPanel CheckBox { background: transparent; }")
        self.hide()

    def contentLayout(self): return self._contentLayout
    def headerWidget(self): return self._headerFrame
    def checkbox(self): return self._checkbox
    def contentFrame(self): return self._contentFrame

    def syncGeometry(self, rect):
        """把 Panel 摆到 rect 上；始终 raise_ 保证位于兄弟控件之上。"""
        if self.geometry() != rect:
            self.setGeometry(rect)
        self.raise_()

    def setHandleVisible(self, visible):
        if self._splitterHandle is not None:
            self._splitterHandle.setVisible(visible)

    def applyHeaderLayout(self, expanded, relayout=True):
        """
        切换 header 布局。
        expanded=True  -> 水平排列（正常标题 / CheckBox+文字）
        expanded=False -> 水平方向抽屉旋转标题；垂直方向保持水平布局
        relayout=False 时仅设置布局，不立即重排子控件几何（用于测量场景）。
        """
        side, is_h, has_ckb, title = self._drawer._side, self._drawer._is_horizontal, self._checkbox is not None, self._drawer._title

        def setCkb(text, fixed_w=None):
            self._checkbox.setText(text)
            if fixed_w is not None:
                self._checkbox.setFixedWidth(fixed_w)
            else:
                self._checkbox.setMinimumWidth(0)
                self._checkbox.setMaximumWidth(16777215)
            self._checkbox.updateGeometry()
            self._headerLayout.setAlignment(self._checkbox, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        def setTitleLbl(angle=0, fixed_w=None):
            self._titleLabel.setVisible(True)
            self._titleLabel.setAngle(angle)
            if fixed_w is not None:
                self._titleLabel.setFixedWidth(fixed_w)
            else:
                self._titleLabel.setMinimumWidth(0)
                self._titleLabel.setMaximumWidth(16777215)
            self._titleLabel.updateGeometry()

        # 展开态 与 垂直方向抽屉的收起态，布局一致（水平排列）
        if expanded or not is_h:
            self._headerLayout.setDirection(QBoxLayout.Direction.LeftToRight)
            self._headerLayout.setContentsMargins(14, 14, 14, 14)
            self._headerLayout.setSpacing(8)
            if has_ckb:
                setCkb(title)
                self._titleLabel.setVisible(False)
            else:
                setTitleLbl()
        else:
            # 水平方向抽屉的收起态：纵向堆叠，标题旋转
            self._headerLayout.setDirection(QBoxLayout.Direction.TopToBottom)
            self._headerLayout.setContentsMargins(14, 14, 14, 14)
            self._headerLayout.setSpacing(6)
            if has_ckb:
                setCkb("", fixed_w=22)
            setTitleLbl(angle=90 if side == DrawerSide.LEFT else -90, fixed_w=22)
            self._headerLayout.setAlignment(self._titleLabel, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self._headerLayout.invalidate()
        self._headerLayout.activate()
        if relayout:
            self._relayout()

    def _relayout(self):
        """根据当前 Panel 尺寸，重新计算 header / content / 手柄的几何。"""
        if not self._headerFrame.isHidden():
            hh = self._headerFrame.sizeHint().height()
            self._headerFrame.setGeometry(0, 0, max(self.width(), 1), hh if hh > 0 else 40)

        side, exp, col = self._drawer._side, self._drawer._expanded_size, self._drawer._collapsed_size
        pw, ph = self.width(), self.height()
        hh = self._headerFrame.height() if not self._headerFrame.isHidden() else 0

        def progress(cur, lo, hi):
            return 1.0 if hi <= lo else max(0.0, min(1.0, (cur - lo) / (hi - lo)))

        # content 沿展开方向滑出：t=0 完全藏于 header 后，t=1 完全展开
        if self._drawer._is_horizontal:
            t = progress(pw, col, exp)
            c_x = int(-exp * (1.0 - t)) if side == DrawerSide.LEFT else int(exp * (1.0 - t))
            c_y, c_w, c_h = hh, exp, max(ph - hh, 0)
        else:
            t = progress(ph, col, exp)
            off = int(exp * (1.0 - t))
            c_x, c_y, c_w, c_h = 0, hh + (-off if side == DrawerSide.TOP else off), pw, max(exp - hh, 0)
        self._contentFrame.setGeometry(c_x, c_y, c_w, c_h)

        if self._splitterHandle is not None:
            th = DrawerSplitterHandle.HANDLE_THICKNESS
            self._splitterHandle.setGeometry(*{
                DrawerSide.LEFT: (pw - th, 0, th, ph), DrawerSide.RIGHT: (0, 0, th, ph),
                DrawerSide.TOP: (0, ph - th, pw, th), DrawerSide.BOTTOM: (0, 0, pw, th),
            }[side])

    def showEvent(self, e): super().showEvent(e); self._relayout()
    def resizeEvent(self, e): self._relayout(); super().resizeEvent(e)

    def setShadow(self, on):
        """开关悬浮阴影（仅悬浮展开时启用）。"""
        if on == self._shadow_on:
            return
        self._shadow_on = on
        if not on:
            self.setGraphicsEffect(None)
            return
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(40)
        effect.setColor(QColor(0, 0, 0, 80) if isDarkTheme() else QColor(0, 0, 0, 40))
        effect.setOffset(*{DrawerSide.LEFT: (8, 0), DrawerSide.RIGHT: (-8, 0), DrawerSide.TOP: (0, 8), DrawerSide.BOTTOM: (0, -8)}[self._drawer._side])
        self.setGraphicsEffect(effect)
        self.raise_()

    def paintEvent(self, event: QPaintEvent):
        def buildEdge(rect, r):
            # 非贴靠侧 + 相邻两端圆角的描边路径
            p = QPainterPath()
            d = 2.0 * r
            L, T, R, B = rect.left(), rect.top(), rect.right(), rect.bottom()
            side = self._drawer._side
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

        def drawNoise(painter, rect, r, alpha):
            # 64x64 噪点贴图，平铺出磨砂质感（固定种子，结果确定）
            pm = QPixmap(64, 64)
            pm.fill(Qt.GlobalColor.transparent)
            pp = QPainter(pm)
            pp.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            rng = QRandomGenerator(0xA57C0FF)
            fg = QColor(255, 255, 255) if isDarkTheme() else QColor(0, 0, 0)
            for _ in range(280):
                c = QColor(fg)
                c.setAlpha(rng.bounded(alpha) + 1)
                pp.setPen(c)
                pp.drawPoint(rng.bounded(64), rng.bounded(64))
            pp.end()
            path = QPainterPath()
            path.addRoundedRect(rect, r, r)
            painter.save()
            painter.setClipPath(path)
            painter.setOpacity(0.5)
            painter.fillRect(rect, QBrush(pm))
            painter.restore()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        rect = QRectF(self.rect())
        r = 8.0
        is_dark = isDarkTheme()

        # 半透明底色 + 噪点
        path = QPainterPath()
        path.addRoundedRect(rect, r, r)
        painter.fillPath(path, QColor(40, 40, 40, 235) if is_dark else QColor(245, 245, 245, 235))
        drawNoise(painter, rect, r, 10 if is_dark else 8)

        # 非贴靠侧描边
        pen_w = 1.0
        inset = pen_w / 2.0
        pen = QPen(QColor(255, 255, 255, 22) if is_dark else QColor(0, 0, 0, 18))
        pen.setWidthF(pen_w)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(buildEdge(rect.adjusted(inset, inset, -inset, -inset), r - inset))


# ═══════════════════════════════════════════════
# 主组件
# ═══════════════════════════════════════════════

class FluentDrawer(QFrame):
    """
    Fluent 风格抽屉容器（本体是布局占位符）。

    side 只是"标识"—— 决定圆角方向、拖动手柄所在边、收起形态，
    不会自动改变抽屉在父布局中的位置。请自行用布局摆放。
    """

    expanded = Signal()
    collapsed = Signal()
    checkboxStateChanged = Signal(bool)

    MIN_EXPANDED_SIZE = 120
    DEFAULT_EXPANDED_SIZE = 280
    MIN_COLLAPSED_SIZE = 40

    def __init__(self, title, side, parent, content=None, *, checkbox_visible=False, autohide=AutoHideMode.NONE, animated=True, resizable=False, expanded=True, content_enabled=True, content_margins=(16, 14, 16, 14), content_spacing=10):
        """
        title:            标题文字（展开态显示）
        side:             DrawerSide，决定圆角方向 / 手柄所在边 / 收起形态
        parent:           父控件
        content:          内容控件或布局（可选）
        checkbox_visible: header 是否显示 CheckBox（标题会作为其文字）
        autohide:         AutoHideMode，可叠加
        animated:         是否启用尺寸动画
        resizable:        是否显示拖动手柄
        expanded:         初始是否展开（启用 HOVER 时失效）
        content_enabled:  初始内容是否可交互
        content_margins:  content 内边距
        content_spacing:  content 布局间距
        """
        super().__init__(parent)
        self._title = title
        self._side = side
        self._checkbox_visible = checkbox_visible
        self._autohide = autohide
        self._animated = animated
        self._resizable = resizable
        self._is_animating = False
        self._expanded_size = self.DEFAULT_EXPANDED_SIZE
        self._collapsed_size = self.MIN_COLLAPSED_SIZE
        self._content_margins = content_margins
        self._content_spacing = content_spacing
        self._content_enabled = content_enabled
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

        self._expanded = False
        self._ensurePanel()
        if content is not None:
            if isinstance(content, QWidget):
                self.contentLayout().addWidget(content)
            elif isinstance(content, QLayout):
                self.contentLayout().addLayout(content)
        self.setContentEnabled(content_enabled)
        # HOVER 模式由定时器驱动，初始展开请求应忽略
        if expanded and not (autohide & AutoHideMode.HOVER):
            QTimer.singleShot(100, lambda: self.expand(floating=False, sync_checkbox=False))

    # ─────────────────────────────────────────
    # Panel 生命周期
    # ─────────────────────────────────────────

    def _ensurePanel(self):
        """惰性创建 Panel，并完成一次初始布局（含收起尺寸测量）。"""
        if self._panel:
            return
        self._panel = DrawerPanel(self, self.parentWidget())
        if self._panel.checkbox() is not None:
            self._panel.checkbox().stateChanged.connect(self._onCheckboxChanged)
        # 主题变化时只需重绘 Panel，不必重建结构
        qconfig.themeChanged.connect(lambda *_: QTimer.singleShot(0, lambda: self._panel and self._panel.update()))
        self._initAutohide()

        # 先测收起尺寸（保证初始 collapsed 与后续一致）
        self._measureCollapsedSize()
        target = self._expanded_size if self._expanded else self._collapsed_size
        self._setPlaceholderSize(target)
        self._panel.syncGeometry(self._computePanelRect(target))
        if self._expanded:
            self._panel.applyHeaderLayout(True, relayout=False)
        self._panel.contentFrame().setVisible(self._expanded)
        self._panel.setHandleVisible(self._expanded)
        self._panel.show()       # showEvent 里 _relayout 一次完成最终几何
        self._panel.raise_()

    def _measureCollapsedSize(self):
        """切到收起布局测量 header 尺寸（不触发 relayout）。测量后布局停在收起态。

        关键点：用 isHidden() 而非 isVisible()，保证窗口尚未 show 时也能测出真实尺寸。
        否则初始 collapsed 会停留在 MIN_COLLAPSED_SIZE（原 bug）。
        """
        self._panel.setUpdatesEnabled(False)
        try:
            self._panel.applyHeaderLayout(False, relayout=False)
            hdr = self._panel.headerWidget()
            if hdr is not None and not hdr.isHidden():
                self._collapsed_size = max(hdr.sizeHint().width() if self._is_horizontal else hdr.sizeHint().height(), self.MIN_COLLAPSED_SIZE)
        finally:
            self._panel.setUpdatesEnabled(True)

    def event(self, e: QEvent):
        # 换父后需重建 Panel
        if e.type() == QEvent.Type.ParentChange:
            QTimer.singleShot(0, self._ensurePanel)
        # 占位符移动/缩放时 Panel 跟随
        elif e.type() in (QEvent.Type.Move, QEvent.Type.Resize) and self._panel and not self._is_animating:
            if self._floating_active:
                self._panel.syncGeometry(self._computePanelRect(self._expanded_size if self._expanded else self._collapsed_size))
            else:
                cur = self.width() if self._is_horizontal else self.height()
                if cur > 0:
                    self._panel.syncGeometry(self._computePanelRect(cur))
        # 禁用时 CheckBox 也要禁用
        elif e.type() == QEvent.Type.EnabledChange and self._panel:
            ckb = self._panel.checkbox()
            if ckb is not None:
                ckb.setEnabled(self.isEnabled())
            # 避免调用setContentEnabled，防止联动
            if self._panel.contentFrame() is not None:
                self._panel.contentFrame().setEnabled(self.isEnabled() and ckb.isChecked())
        return super().event(e)

    def _computePanelRect(self, size):
        """按当前占位符几何和 size 计算 Panel 应占的矩形（父坐标系）。"""
        pos = self.pos()
        pw, ph = max(self.width(), 1), max(self.height(), 1)
        if self._is_horizontal:
            return QRect(pos.x(), pos.y(), size, ph) if self._side == DrawerSide.LEFT else QRect(pos.x() + pw - size, pos.y(), size, ph)
        return QRect(pos.x(), pos.y(), pw, size) if self._side == DrawerSide.TOP else QRect(pos.x(), pos.y() + ph - size, pw, size)

    def _isInsideRect(self, global_pos, size):
        """global_pos 是否落在按 size 计算出的 Panel 矩形内。"""
        parent = self.parentWidget()
        if parent is None:
            return False
        rect = self._computePanelRect(size)
        return QRect(parent.mapToGlobal(rect.topLeft()), rect.size()).contains(global_pos)

    # ─────────────────────────────────────────
    # CheckBox
    # ─────────────────────────────────────────

    def _onCheckboxChanged(self, _state):
        # 联动：CheckBox 状态变化 -> content 启停 + 展开/收起
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
        elif self._expanded:
            # HOVER 下由用户主动勾掉，需阻止 hover 立刻重新展开
            if self._autohide & AutoHideMode.HOVER:
                self._hover_block_until_leave = True
            self.collapse(floating=False)

    def _setCheckboxSilently(self, checked):
        """程序化设置 CheckBox 状态，屏蔽信号回环。"""
        ckb = self._panel.checkbox() if self._panel else None
        if ckb is None or ckb.isChecked() == checked:
            return
        ckb.blockSignals(True)
        ckb.setChecked(checked)
        ckb.blockSignals(False)
        self.setContentEnabled(checked)

    # ─────────────────────────────────────────
    # Autohide
    # ─────────────────────────────────────────

    def _initAutohide(self):
        """按当前 autohide 模式挂/摘事件过滤器、启/停 hover 定时器。"""
        app = QApplication.instance()
        # 先清掉历史注册，避免模式切换残留
        for target in (app, self):
            try:
                target.removeEventFilter(self)
            except Exception:
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
        # 定时轮询光标位置：进入/离开检测矩形时切换展开/收起
        if not self.isEnabled() or self._dragging or not self._panel or not self._panel.isVisible() or not (self._autohide & AutoHideMode.HOVER):
            return
        gp = QCursor.pos()
        top = QApplication.widgetAt(gp)
        # 收起态只认折叠矩形，展开态才用展开矩形，避免缩回途中被误触重开
        size = self._expanded_size if self._expanded else self._collapsed_size
        inside = top is not None and top.window() is self.window() and self._isInsideRect(gp, size)
        if self._autohide & AutoHideMode.CHECKBOX:
            ckb = self._panel.checkbox()
            if ckb is not None and ckb.isChecked():
                return
        if self._hover_block_until_leave:
            if not inside:
                self._hover_block_until_leave = False
            return
        if self._expanded:
            if not inside:
                self.collapse(floating=True, sync_checkbox=False)
        elif inside:
            self.expand(floating=True, sync_checkbox=False)

    def eventFilter(self, obj, event: QEvent):
        # FOCUS 模式：全局左键按下 -> 内展开 / 外收起
        if not self.isEnabled() or not (self._autohide & AutoHideMode.FOCUS):
            return super().eventFilter(obj, event)
        if event.type() != QEvent.Type.MouseButtonPress or event.button() != Qt.MouseButton.LeftButton:
            return super().eventFilter(obj, event)
        if not self._panel or not self._panel.isVisible() or self.parentWidget() is None:
            return super().eventFilter(obj, event)

        gp = event.globalPosition().toPoint()
        # 落在 CheckBox 上交给其自己处理（信号驱动展开/收起）
        ckb = self._panel.checkbox()
        if ckb is not None and ckb.isVisible() and QRect(ckb.mapToGlobal(QPoint(0, 0)), ckb.size()).contains(gp):
            return super().eventFilter(obj, event)

        size = self._expanded_size if self._expanded else self._collapsed_size
        if self._isInsideRect(gp, size):
            self.expand(floating=False)
        elif self._expanded:
            self.collapse(floating=False)
        return super().eventFilter(obj, event)

    # ─────────────────────────────────────────
    # 展开 / 收起
    # ─────────────────────────────────────────

    def expand(self, *, floating=False, sync_checkbox=True):
        """
        展开抽屉。
        floating:      True=悬浮展开（占位符不动，Panel 覆盖展开），False=挤压展开
        sync_checkbox: 是否同步 CheckBox 状态（避免信号回环）
        """
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
        # 纯 HOVER 触发展开时，首次给 content 打开 enable
        if floating and not (self._autohide & AutoHideMode.CHECKBOX) and not self._content_enabled:
            self.setContentEnabled(True)
        if sync_checkbox and (self._autohide & AutoHideMode.CHECKBOX):
            self._setCheckboxSilently(True)
        self._applyExpandedState(animated=self._animated)
        self.expanded.emit()

    def collapse(self, *, floating=None, sync_checkbox=True):
        """
        收起抽屉。
        floating:      True=悬浮收起（占位符不动），False=挤压收起，None=沿用当前模式
        sync_checkbox: 是否同步 CheckBox 状态
        """
        if not self.isEnabled():
            return
        if not self._expanded and not self._is_animating:
            return
        self._stopAnimation()
        self._expanded = False
        self._floating_active = self._floating_active if floating is None else floating
        if sync_checkbox and (self._autohide & AutoHideMode.CHECKBOX):
            self._setCheckboxSilently(False)
        self._applyExpandedState(animated=self._animated)
        self.collapsed.emit()

    def toggle(self, *, floating=False):
        """切换展开/收起。floating 同 expand 的参数。"""
        if self._expanded:
            self.collapse(floating=floating)
        else:
            self.expand(floating=floating)

    # ─────────────────────────────────────────
    # 尺寸工具
    # ─────────────────────────────────────────

    def _stopAnimation(self):
        if self._anim is not None:
            try:
                self._anim.stop()
            except Exception:
                pass
            self._anim = None
        self._is_animating = False

    def _setPlaceholderSize(self, size):
        if self._is_horizontal:
            self.setMinimumWidth(size)
            self.setMaximumWidth(size)
        else:
            self.setMinimumHeight(size)
            self.setMaximumHeight(size)

    def _setPanelRect(self, size):
        if self._panel:
            self._panel.syncGeometry(self._computePanelRect(size))

    def _applySize(self, size, floating=None):
        """floating=True 只动 Panel；False 占位符和 Panel 一起动；None 按当前模式。"""
        if floating is None:
            floating = self._floating_active
        if not floating:
            self._setPlaceholderSize(size)
        self._setPanelRect(size)

    def _currentSize(self):
        if self._floating_active:
            return self._panel.width() if self._is_horizontal else self._panel.height()
        return self.width() if self._is_horizontal else self.height()

    def _run_size_animation(self, start, end, duration, on_value, on_finish):
        """尺寸动画骨架：调用方提供 on_value / on_finish 回调。"""
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

    def _applyExpandedState(self, animated):
        if not self._panel:
            return

        # 目标布局：展开态水平排版；收起态旋转标题
        if self._expanded:
            self._panel.applyHeaderLayout(True)
        else:
            self._measureCollapsedSize()
            if animated:
                # 动画期间保持展开排版，旋转留到 on_finished
                self._panel.applyHeaderLayout(True)

        target = self._expanded_size if self._expanded else self._collapsed_size
        floating_anim = self._floating_active
        floating_display = floating_anim and self._expanded

        if self._expanded:
            self._panel.contentFrame().setVisible(True)
        self._panel.setShadow(floating_display)

        if not animated:
            self._is_animating = False
            # 悬浮模式占位符锁定 collapsed；挤压模式跟随 target
            self._setPlaceholderSize(self._collapsed_size if floating_anim else target)
            self._setPanelRect(target)
            if not self._expanded:
                self._panel.contentFrame().setVisible(False)
                self._panel.applyHeaderLayout(False)
            self._panel.setHandleVisible(self._expanded)
            return

        self._panel.setHandleVisible(False)
        if floating_anim:
            self._setPlaceholderSize(self._collapsed_size)
        current = self._currentSize()
        rotate_header_at_end = not self._expanded

        def on_value(v): self._applySize(int(v), floating_anim)

        def on_finished():
            self._is_animating = False
            self._applySize(target, floating_anim)
            if not self._expanded:
                self._panel.contentFrame().setVisible(False)
                if rotate_header_at_end:
                    self._panel.applyHeaderLayout(False)
            self._panel.setHandleVisible(self._expanded)
            self._anim = None

        self._run_size_animation(current, target, 250, on_value, on_finished)

    def _switch_floating(self, to_floating):
        """悬浮 <-> 挤压 模式切换：占位符动画，Panel 始终锁定展开尺寸。"""
        if self._floating_active == to_floating:
            return
        self._floating_active = to_floating
        self._panel.setShadow(to_floating)
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
        if not self.isEnabled() or not self._expanded:
            return
        self._drag_last_pos = None
        self._dragging = True
        self._stopAnimation()

    def _onSplitterDrag(self, global_pos):
        """按边方向把鼠标位移换算成展开尺寸，并限制到合理范围。"""
        if not self._expanded or not self._dragging:
            return
        if self._drag_last_pos is None:
            self._drag_last_pos = global_pos
            return
        delta = global_pos - self._drag_last_pos
        self._drag_last_pos = global_pos
        cur = self._currentSize()

        # 参照系：优先父容器，其次窗口，最后回落默认值
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

        # 贴靠侧不同，鼠标位移对尺寸的正负号不同
        side = self._side
        if side == DrawerSide.LEFT:
            new_total = cur + delta.x()
        elif side == DrawerSide.RIGHT:
            new_total = cur - delta.x()
        elif side == DrawerSide.TOP:
            new_total = cur + delta.y()
        else:
            new_total = cur - delta.y()

        self._expanded_size = max(self.MIN_EXPANDED_SIZE, min(new_total, max_size))
        self._applySize(self._expanded_size)

    def _onSplitterDragFinish(self):
        self._drag_last_pos = None
        self._dragging = False

    # ─────────────────────────────────────────
    # 公共 API
    # ─────────────────────────────────────────

    def contentLayout(self):
        """返回 content 布局，供外部添加内容。"""
        if not self._panel:
            self._ensurePanel()
        return self._panel.contentLayout()

    def setContentEnabled(self, enabled):
        """启用/禁用 content，并同步 CheckBox。"""
        self._content_enabled = enabled
        if not self._panel:
            return
        self._panel.contentFrame().setEnabled(enabled)
        self._panel.headerWidget().setEnabled(True)
        ckb = self._panel.checkbox()
        if ckb is None or ckb.isChecked() == enabled:
            return
        if self._autohide & AutoHideMode.CHECKBOX:
            ckb.setChecked(enabled)
        else:
            self._setCheckboxSilently(enabled)

    def isContentEnabled(self): return self._content_enabled

    def setTitle(self, title):
        """更新标题（同时刷新 CheckBox 文字，若启用）。"""
        self._title = title
        if self._panel:
            self._panel._titleLabel.setText(title)
            ckb = self._panel.checkbox()
            if ckb is not None:
                ckb.setText(title)
            self._panel.headerWidget().setVisible(bool(title) or self._checkbox_visible)

    def title(self): return self._title
    def setAnimated(self, animated): self._animated = animated
    def isAnimated(self): return self._animated
    def setAutohide(self, mode): self._autohide = mode; self._initAutohide()
    def autohide(self): return self._autohide
    def isExpanded(self): return self._expanded
    def expandedSize(self): return self._expanded_size

    def setExpandedSize(self, size):
        """设置展开尺寸。展开态时立即动画过渡；收起态只记录。"""
        size = max(self.MIN_EXPANDED_SIZE, size)
        if size == self._expanded_size:
            return
        self._expanded_size = size
        if not self._expanded or not self._panel:
            return
        floating = self._floating_active
        if not self._animated:
            self._applySize(size, floating)
            return
        current = self._currentSize()

        def on_value(v): self._applySize(int(v), floating)

        def on_finished():
            self._applySize(size, floating)
            self._anim = None
            self._is_animating = False

        self._run_size_animation(current, size, 200, on_value, on_finished)

    def checkbox(self): return self._panel.checkbox() if self._panel else None
    def headerWidget(self): return self._panel.headerWidget() if self._panel else None
    def panel(self): return self._panel
    def side(self): return self._side
