# coding: utf-8
"""
FluentDrawer — 基于 QFluentWidgets (PySide6) 的自定义抽屉容器组件

功能特性:
- 支持上/下/左/右四个贴靠方向
- 可选标题、可选 CheckBox（未勾选时内容自动 disable）
- 三种 autohide 模式：关联 CheckBox / 鼠标进入离开 / 失去焦点
- 展开/收起动画开关
- 非贴靠侧圆角 + Fluent 风格主题适配（亮/暗）
- 面板背景色参照 Fluent 对话框 buttonGroup 层
- 可选拖拽调整宽度/长度（类似 QSplitter，带 Fluent 风格拖动条）
- 适配 Mica 主窗口的半透明背景
"""

from enum import Enum
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from qfluentwidgets import *


# ═══════════════════════════════════════════════
# 枚举
# ═══════════════════════════════════════════════

class DrawerSide(Enum):
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"


class AutoHideMode(Enum):
    NONE = "none"
    CHECKBOX = "checkbox"
    HOVER = "hover"
    FOCUS = "focus"

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

    def angle(self):
        return self._angle

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

        draw_rect = QRectF(-h / 2.0, -w / 2.0, h, w)
        painter.drawText(draw_rect, Qt.AlignmentFlag.AlignCenter, self.text())

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
# 拖动条
# ═══════════════════════════════════════════════

class DrawerSplitterHandle(QFrame):
    GRIP_SIZE = 3
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
        # 垂直 handle（左右贴靠）→ 调宽度 → SplitH（左右箭头）
        # 水平 handle（上下贴靠）→ 调高度 → SplitV（上下箭头）
        if orientation == Qt.Orientation.Vertical:
            self.setCursor(Qt.CursorShape.SplitHCursor)
        else:
            self.setCursor(Qt.CursorShape.SplitVCursor)

        # 关键：不让 QFrame 绘制默认背景，否则会盖住父控件圆角
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
                y = start_y + i * s
                painter.drawEllipse(QPoint(int(cx), int(y)), radius, radius)
        else:
            start_x = cx - s
            for i in range(3):
                x = start_x + i * s
                painter.drawEllipse(QPoint(int(x), int(cy)), radius, radius)

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
# 主组件
# ═══════════════════════════════════════════════


class FluentDrawer(QFrame):
    """
    Fluent 风格抽屉容器。

    注意:
        side 只是"标识"—— 决定圆角方向、拖动条所在边、收起形态,
        不会自动改变抽屉在父布局中的位置。请自行用布局摆放。
    """

    expanded = Signal()
    collapsed = Signal()
    checkboxStateChanged = Signal(bool)

    MIN_EXPANDED_SIZE = 120
    DEFAULT_EXPANDED_SIZE = 280
    MIN_COLLAPSED_SIZE = 40

    # ─────────────────────────────────────────
    # 构造 / 初始化
    # ─────────────────────────────────────────

    def __init__(
        self,
        title: str = "",
        side: DrawerSide = DrawerSide.LEFT,
        parent=None,
        *,
        checkbox_enabled: bool = False,
        autohide: AutoHideMode = AutoHideMode.NONE,
        animated: bool = True,
        resizable: bool = False,
        expanded: bool = True,
        content_margins: tuple = (16, 14, 16, 14),
        content_spacing: int = 10,
    ):
        super().__init__(parent)
        self._side = side
        self._title = title
        self._checkbox_enabled = checkbox_enabled
        self._autohide = autohide
        self._animated = animated
        self._resizable = resizable
        self._expanded = expanded
        self._is_animating = False
        self._expanded_size = self.DEFAULT_EXPANDED_SIZE
        self._collapsed_size = self.MIN_COLLAPSED_SIZE
        self._content_enabled = True
        self._applying_style = False
        self._drag_last_pos = None
        self._anim = None

        # 左右贴靠的抽屉展开方向是水平的（宽度变化）
        self._is_horizontal = side in (DrawerSide.LEFT, DrawerSide.RIGHT)

        self._initUI(content_margins, content_spacing)

        # 样式
        self.setObjectName("fluentDrawer")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self._applyDrawerStyle()

        # 信号
        qconfig.themeChanged.connect(self._onThemeChanged)
        if self._checkbox:
            self._checkbox.stateChanged.connect(self._onCheckboxChanged)
        # 构造期 isVisible() 恒为 False，不能加判断
        self._headerFrame.mousePressEvent = self._onHeaderClicked

        self._initAutoHide()

        # 尺寸策略
        if self._is_horizontal:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._applyExpandedState(animated=False)

    # ─────────────────────────────────────────
    # UI 构建
    # ─────────────────────────────────────────

    def _initUI(self, content_margins, content_spacing):
        if self._is_horizontal:
            self._rootLayout = QHBoxLayout(self)
        else:
            self._rootLayout = QVBoxLayout(self)
        self._rootLayout.setContentsMargins(0, 0, 0, 0)
        self._rootLayout.setSpacing(0)
        self._rootLayout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)

        self._body = QFrame(self)
        self._body.setObjectName("drawerBody")
        self._body.setFrameShape(QFrame.Shape.NoFrame)
        self._body.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._body.setMinimumSize(0, 0)
        self._body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._body.setAutoFillBackground(False)

        self._bodyLayout = QVBoxLayout(self._body)
        self._bodyLayout.setContentsMargins(0, 0, 0, 0)
        self._bodyLayout.setSpacing(0)

        self._headerFrame = QFrame(self._body)
        self._headerFrame.setObjectName("drawerHeader")
        self._headerFrame.setFrameShape(QFrame.Shape.NoFrame)
        self._headerFrame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._headerLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight, self._headerFrame)
        self._headerLayout.setContentsMargins(16, 10, 16, 10)
        self._headerLayout.setSpacing(8)
        self._headerFrame.setAutoFillBackground(False)

        self._checkbox = None
        if self._checkbox_enabled:
            self._checkbox = CheckBox(self._headerFrame)
            self._checkbox.setChecked(True)
            self._headerLayout.addWidget(self._checkbox, 0, Qt.AlignmentFlag.AlignCenter)

        self._titleLabel = RotatedLabel(self._title, 0, self._headerFrame)
        self._titleLabel.setObjectName("drawerTitle")
        self._headerLayout.addWidget(self._titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        self._headerLayout.addStretch(1)

        self._headerFrame.setVisible(bool(self._title) or self._checkbox_enabled)

        self._contentFrame = QFrame(self._body)
        self._contentFrame.setObjectName("drawerContent")
        self._contentFrame.setFrameShape(QFrame.Shape.NoFrame)
        self._contentFrame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._contentFrame.setAutoFillBackground(False)
        self._contentLayout = QVBoxLayout(self._contentFrame)
        self._contentLayout.setContentsMargins(*content_margins)
        self._contentLayout.setSpacing(content_spacing)

        self._bodyLayout.addWidget(self._headerFrame, 0)
        self._bodyLayout.addWidget(self._contentFrame, 1)

        if self._resizable:
            orientation = Qt.Orientation.Vertical if self._is_horizontal else Qt.Orientation.Horizontal
            self._splitterHandle = DrawerSplitterHandle(orientation, self)
            self._splitterHandle.dragStarted.connect(self._onSplitterDragStart)
            self._splitterHandle.dragMoved.connect(self._onSplitterDrag)
            self._splitterHandle.dragFinished.connect(self._onSplitterDragFinish)
        else:
            self._splitterHandle = None

        # ── 组装根布局（内部函数，只此一处使用） ──
        def assemble_root():
            side = self._side
            body = self._body
            handle = self._splitterHandle

            if side == DrawerSide.LEFT:
                self._rootLayout.addWidget(body, 1)
                if handle:
                    self._rootLayout.addWidget(handle, 0)
            elif side == DrawerSide.RIGHT:
                if handle:
                    self._rootLayout.addWidget(handle, 0)
                self._rootLayout.addWidget(body, 1)
            elif side == DrawerSide.TOP:
                self._rootLayout.addWidget(body, 1)
                if handle:
                    self._rootLayout.addWidget(handle, 0)
            elif side == DrawerSide.BOTTOM:
                if handle:
                    self._rootLayout.addWidget(handle, 0)
                self._rootLayout.addWidget(body, 1)

        assemble_root()

    # ─────────────────────────────────────────
    # 样式
    # ─────────────────────────────────────────

    def _applyDrawerStyle(self):
        if self._applying_style:
            return
        self._applying_style = True
        try:
            def build_qss():
                return (
                    "#fluentDrawer, #drawerBody, #drawerHeader, #drawerContent, #drawerTitle { background: transparent; border: none; }"
                    "#fluentDrawer CheckBox { background: transparent; }"
                )

            self.setStyleSheet(build_qss())
        finally:
            self._applying_style = False

    def _onThemeChanged(self, *_):
        def refresh():
            self._applyDrawerStyle()
            self.update()

        QTimer.singleShot(0, refresh)

    def changeEvent(self, event):
        # 不在这里刷样式，避免递归；改用 qconfig.themeChanged
        super().changeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        is_dark = isDarkTheme()
        if is_dark:
            bg = QColor(0, 0, 0, 56)
            border_color = QColor(255, 255, 255, 22)
        else:
            bg = QColor(255, 255, 255, 130)
            border_color = QColor(0, 0, 0, 18)

        r = 8.0
        rect = QRectF(self.rect())

        path = QPainterPath()
        path.setFillRule(Qt.FillRule.WindingFill)
        path.addRoundedRect(rect, r, r)

        if self._side == DrawerSide.LEFT:
            path.addRect(QRectF(rect.left(), rect.top(), r, rect.height()))
        elif self._side == DrawerSide.RIGHT:
            path.addRect(QRectF(rect.right() - r, rect.top(), r, rect.height()))
        elif self._side == DrawerSide.TOP:
            path.addRect(QRectF(rect.left(), rect.top(), rect.width(), r))
        else:
            path.addRect(QRectF(rect.left(), rect.bottom() - r, rect.width(), r))

        painter.fillPath(path, bg)

        side = self._side
        if side == DrawerSide.LEFT:          # 高光在右
            clip = QRectF(rect.right() - r, rect.top(), r, rect.height())
        elif side == DrawerSide.RIGHT:       # 高光在左
            clip = QRectF(rect.left(), rect.top(), r, rect.height())
        elif side == DrawerSide.TOP:         # 高光在下
            clip = QRectF(rect.left(), rect.bottom() - r, rect.width(), r)
        else:                                # BOTTOM，高光在上
            clip = QRectF(rect.left(), rect.top(), rect.width(), r)

        # 高光描边
        pen = QPen(border_color)
        pen.setWidthF(2)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        def _build_edge_path(rect: QRectF, r: float) -> QPainterPath:
            """只构造非贴靠边 + 两端相邻圆角的描边路径（从上到下）"""
            p = QPainterPath()
            side = self._side
            d = 2.5 * r
            L, T, R, B = rect.left(), rect.top(), rect.right(), rect.bottom()

            if side == DrawerSide.LEFT:          # 高光在右边缘
                # 右上角弧：顶部边缘 → 右侧边缘
                p.arcMoveTo(QRectF(R - d, T, d, d), 90)
                p.arcTo(QRectF(R - d, T, d, d), 90, -90)
                # 右下角弧：右侧边缘 → 底部边缘（arcTo 自动画中间那条竖线）
                p.arcTo(QRectF(R - d, B - d, d, d), 0, -90)

            elif side == DrawerSide.RIGHT:       # 高光在左边缘
                # 左上角弧：顶部边缘 → 左侧边缘
                p.arcMoveTo(QRectF(L, T, d, d), 90)
                p.arcTo(QRectF(L, T, d, d), 90, 90)
                # 左下角弧：左侧边缘 → 底部边缘
                p.arcTo(QRectF(L, B - d, d, d), 180, 90)

            elif side == DrawerSide.TOP:         # 高光在下边缘
                # 左下角弧：左侧边缘 → 底部边缘
                p.arcMoveTo(QRectF(L, B - d, d, d), 180)
                p.arcTo(QRectF(L, B - d, d, d), 180, 90)
                # 右下角弧：底部边缘 → 右侧边缘
                p.arcTo(QRectF(R - d, B - d, d, d), 270, 90)

            else:                                # BOTTOM，高光在上边缘
                # 左上角弧：左侧边缘 → 顶部边缘
                p.arcMoveTo(QRectF(L, T, d, d), 180)
                p.arcTo(QRectF(L, T, d, d), 180, -90)
                # 右上角弧：顶部边缘 → 右侧边缘
                p.arcTo(QRectF(R - d, T, d, d), 90, -90)

            return p
        painter.drawPath(_build_edge_path(rect, r))

    # ─────────────────────────────────────────
    # 交互 / 信号处理
    # ─────────────────────────────────────────

    def _onHeaderClicked(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle()
        QFrame.mousePressEvent(self._headerFrame, event)

    def _onCheckboxChanged(self, state):
        checked = (state == Qt.CheckState.Checked.value or state == 2)
        self.setContentEnabled(checked)
        self.checkboxStateChanged.emit(checked)
        if self._autohide == AutoHideMode.CHECKBOX:
            if checked:
                self.expand()
            else:
                self.collapse()

    # ─────────────────────────────────────────
    # Autohide
    # ─────────────────────────────────────────

    def _initAutoHide(self):
        app = QApplication.instance()
        # 先清掉旧安装
        for target in (app, self):
            try:
                target.removeEventFilter(self)
            except (TypeError, RuntimeError):
                pass

        # hover 只要自身事件；focus_lost 需要全局事件（才能收到子控件/外部点击）
        if self._autohide == AutoHideMode.HOVER:
            self.installEventFilter(self)
        elif self._autohide == AutoHideMode.FOCUS:
            app.installEventFilter(self)

        self.setMouseTracking(self._autohide == AutoHideMode.HOVER)

    def eventFilter(self, obj, event):
        # ── MOUSE_HOVER：进入展开，离开收起 ──
        if self._autohide == AutoHideMode.HOVER and obj is self:
            if event.type() == QEvent.Type.Enter:
                self.expand()
            elif event.type() == QEvent.Type.Leave:
                def check_mouse_leave():
                    if not self.underMouse():
                        self.collapse()

                QTimer.singleShot(100, check_mouse_leave)

        # ── FOCUS_LOST：进入不展开，点内展开，点外收起 ──
        elif self._autohide == AutoHideMode.FOCUS:
            if event.type() == QEvent.Type.MouseButtonPress:
                if isinstance(event, QMouseEvent) and event.button() == Qt.MouseButton.LeftButton:
                    if self.isVisible():
                        gp = event.globalPosition().toPoint()
                        inside = self.rect().contains(self.mapFromGlobal(gp))
                        if inside:
                            if not self._expanded:
                                self.expand()
                        else:
                            if self._expanded:
                                self.collapse()

        return super().eventFilter(obj, event)

    # ─────────────────────────────────────────
    # 展开 / 收起
    # ─────────────────────────────────────────

    def expand(self):
        if self._expanded and not self._is_animating:
            return
        self._stopAnimation()
        self._expanded = True
        self._applyExpandedState(animated=self._animated)
        self.expanded.emit()

    def collapse(self):
        if not self._expanded and not self._is_animating:
            return
        self._stopAnimation()
        self._expanded = False
        self._applyExpandedState(animated=self._animated)
        self.collapsed.emit()

    def toggle(self):
        if self._expanded:
            self.collapse()
        else:
            self.expand()

    def _stopAnimation(self):
        if self._anim is not None:
            try:
                self._anim.stop()
            except RuntimeError:
                pass
            self._anim = None
        self._is_animating = False

    def _setFixedDrawerSize(self, size: int):
        if self._is_horizontal:
            self.setMinimumWidth(size)
            self.setMaximumWidth(size)
        else:
            self.setMinimumHeight(size)
            self.setMaximumHeight(size)

    def _applyExpandedState(self, animated):
        has_cb = self._checkbox is not None

        if self._expanded:
            self._headerLayout.setDirection(QBoxLayout.Direction.LeftToRight)
            self._headerLayout.setSpacing(4)
            self._headerLayout.setContentsMargins(16, 10, 16, 10)

            if has_cb:
                self._checkbox.setMinimumWidth(0)
                self._checkbox.setMaximumWidth(16777215)
                self._checkbox.setText(self._title)
                self._checkbox.updateGeometry()
                self._titleLabel.setVisible(False)
            else:
                self._titleLabel.setVisible(True)
                self._titleLabel.setAngle(0)
                self._titleLabel.setMinimumWidth(0)
                self._titleLabel.setMaximumWidth(16777215)
                self._titleLabel.updateGeometry()

            self._contentFrame.setVisible(True)
            if self._splitterHandle:
                self._splitterHandle.setVisible(True)
            target = self._expanded_size

        else:
            if self._is_horizontal:
                self._headerLayout.setDirection(QBoxLayout.Direction.TopToBottom)
                self._headerLayout.setSpacing(6)
                self._headerLayout.setContentsMargins(4, 8, 4, 8)

                if has_cb:
                    self._checkbox.setText("")
                    self._checkbox.setFixedWidth(22)

                self._titleLabel.setVisible(True)
                self._titleLabel.setFixedWidth(22)
                if self._side == DrawerSide.LEFT:
                    self._titleLabel.setAngle(90)
                else:
                    self._titleLabel.setAngle(-90)
            else:
                self._headerLayout.setDirection(QBoxLayout.Direction.LeftToRight)
                self._headerLayout.setSpacing(4)
                self._headerLayout.setContentsMargins(16, 8, 16, 8)

                if has_cb:
                    self._checkbox.setMinimumWidth(0)
                    self._checkbox.setMaximumWidth(16777215)
                    self._checkbox.setText(self._title)
                    self._checkbox.updateGeometry()
                    self._titleLabel.setVisible(False)
                else:
                    self._titleLabel.setVisible(True)
                    self._titleLabel.setAngle(0)
                    self._titleLabel.setMinimumWidth(0)
                    self._titleLabel.setMaximumWidth(16777215)
                    self._titleLabel.updateGeometry()

            self._contentFrame.setVisible(False)
            if self._splitterHandle:
                self._splitterHandle.setVisible(False)

            self._headerLayout.invalidate()
            self._headerLayout.activate()
            hint = self._headerLayout.sizeHint()

            if self._is_horizontal:
                target = max(hint.width(), self.MIN_COLLAPSED_SIZE)
            else:
                target = max(hint.height(), self.MIN_COLLAPSED_SIZE)
            self._collapsed_size = target

        if not animated:
            self._setFixedDrawerSize(target)
            self._is_animating = False
            return

        # ── 动画执行（内部函数，仅此处使用） ──
        def animate_to_size():
            self._stopAnimation()
            self._is_animating = True

            if self._is_horizontal:
                prop_min = b"minimumWidth"
                prop_max = b"maximumWidth"
                current = self.width()
            else:
                prop_min = b"minimumHeight"
                prop_max = b"maximumHeight"
                current = self.height()

            def on_finished():
                self._is_animating = False
                if self._is_horizontal:
                    self.setMinimumWidth(target)
                    self.setMaximumWidth(target)
                else:
                    self.setMinimumHeight(target)
                    self.setMaximumHeight(target)
                self._anim = None

            anim_min = QPropertyAnimation(self, prop_min, self)
            anim_max = QPropertyAnimation(self, prop_max, self)
            for a in (anim_min, anim_max):
                a.setDuration(250)
                a.setEasingCurve(QEasingCurve.Type.OutCubic)
                a.setStartValue(current)
                a.setEndValue(target)

            group = QParallelAnimationGroup(self)
            group.addAnimation(anim_min)
            group.addAnimation(anim_max)
            group.finished.connect(on_finished)
            group.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            self._anim = group

        animate_to_size()

    # ─────────────────────────────────────────
    # 拖动
    # ─────────────────────────────────────────

    def _onSplitterDragStart(self):
        self._drag_last_pos = None
        if self._anim is not None:
            try:
                self._anim.stop()
            except RuntimeError:
                pass
            self._anim = None
            self._is_animating = False

    def _onSplitterDrag(self, global_pos):
        if self._drag_last_pos is None:
            self._drag_last_pos = global_pos
            return
        delta = global_pos - self._drag_last_pos
        self._drag_last_pos = global_pos

        # ── 最大展开尺寸计算（内部函数，仅此处使用） ──
        def get_max_expanded_size():
            ref_w = 0
            ref_h = 0

            parent = self.parentWidget()
            if parent is not None:
                ref_w = parent.width()
                ref_h = parent.height()

            window = self.window()
            if window is not None and window is not self:
                w = window.width()
                h = window.height()
                if w > 0:
                    ref_w = w if ref_w <= 0 else min(ref_w, w)
                if h > 0:
                    ref_h = h if ref_h <= 0 else min(ref_h, h)

            if self._is_horizontal:
                base = ref_w if ref_w > 0 else 800
                return max(self.MIN_EXPANDED_SIZE, int(base * 0.8))
            else:
                base = ref_h if ref_h > 0 else 600
                return max(self.MIN_EXPANDED_SIZE, int(base * 0.8))

        side = self._side
        if side == DrawerSide.LEFT:
            new_total = self.width() + delta.x()
        elif side == DrawerSide.RIGHT:
            new_total = self.width() - delta.x()
        elif side == DrawerSide.TOP:
            new_total = self.height() + delta.y()
        else:
            new_total = self.height() - delta.y()

        max_size = get_max_expanded_size()
        new_total = max(self.MIN_EXPANDED_SIZE, min(new_total, max_size))

        self._expanded_size = new_total
        self._setFixedDrawerSize(new_total)

    def _onSplitterDragFinish(self):
        self._drag_last_pos = None

    # ─────────────────────────────────────────
    # 公共 API
    # ─────────────────────────────────────────

    def contentLayout(self):
        return self._contentLayout

    def setContentEnabled(self, enabled: bool):
        self._content_enabled = enabled
        self._contentFrame.setEnabled(enabled)
        self._headerFrame.setEnabled(True)

    def isContentEnabled(self):
        return self._content_enabled

    def setTitle(self, title):
        self._title = title
        self._titleLabel.setText(title)
        if self._checkbox is not None:
            if self._expanded or not self._is_horizontal:
                self._checkbox.setText(title)
        self._headerFrame.setVisible(bool(title) or self._checkbox_enabled)

    def title(self):
        return self._title

    def setAnimated(self, animated: bool):
        self._animated = animated

    def isAnimated(self):
        return self._animated

    def setAutohide(self, mode: AutoHideMode):
        self._autohide = mode
        self._initAutoHide()

    def autohide(self):
        return self._autohide

    def isExpanded(self):
        return self._expanded

    def setExpandedSize(self, size):
        self._expanded_size = max(self.MIN_EXPANDED_SIZE, size)
        if self._expanded:
            self._setFixedDrawerSize(self._expanded_size)

    def expandedSize(self):
        return self._expanded_size

    def checkbox(self):
        return self._checkbox

    def headerWidget(self):
        return self._headerFrame

    def side(self):
        return self._side
