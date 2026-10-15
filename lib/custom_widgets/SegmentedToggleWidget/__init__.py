from typing import Union

from qfluentwidgets import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class SegmentedToggleItem(TransparentToolButton):
    """ Segmented toggle item (text version, with disabled state) """

    itemClicked = Signal(bool)

    def _postInit(self):
        super()._postInit()
        self.isSelected = False
        self.setCheckable(True)
        self.setFixedHeight(32)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # 注意：不要在 clicked 里读 isChecked()，Qt 的切换顺序不保证
        # 我们只关心"被点了"这个事实，状态由 widget 层的 _currentKey 决定
        self.clicked.connect(lambda: self.itemClicked.emit(True))
        setFont(self, 14)

    # ── 尺寸 ────────────────────────────────────────────────
    def sizeHint(self) -> QSize:
        fm = self.fontMetrics()
        return QSize(max(fm.horizontalAdvance(self.text()) + 24, 40), 32)

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    # ── 状态 ────────────────────────────────────────────────
    def setSelected(self, isSelected: bool):
        if self.isSelected == isSelected:
            return
        self.isSelected = isSelected
        self.setChecked(isSelected)
        self.update()

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self.update()

    # ── 绘制 ────────────────────────────────────────────────
    def _textColor(self) -> QColor:
        if not self.isEnabled():
            return QColor(0, 0, 0, 92) if not isDarkTheme() else QColor(255, 255, 255, 92)
        if self.isSelected:
            return QColor(0, 0, 0) if isDarkTheme() else QColor(255, 255, 255)
        return QColor(255, 255, 255) if isDarkTheme() else QColor(0, 0, 0)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)

        canHover = self.isEnabled() and not self.isSelected
        if canHover and (self.underMouse() or self.isDown()):
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, 15) if isDarkTheme()
                             else QColor(0, 0, 0, 12))
            painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 4, 4)

        painter.setPen(self._textColor())
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())


class SegmentedToggleWidget(SegmentedToggleToolWidget):
    """ Segmented toggle widget (text items, toggle semantics) """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._currentKey = None
        qconfig.themeChanged.connect(self._onThemeChanged)

    def _onThemeChanged(self):
        for item in self.items.values():
            if isinstance(item, SegmentedToggleItem):
                item.update()
        self.update()

    # ── 接口 ────────────────────────────────────────────────
    def addItem(self, routeKey: str, text: str, onClick=None,
                icon: Union[str, QIcon, FluentIconBase] = None):
        return self.insertItem(-1, routeKey, text, onClick, icon)

    def insertItem(self, index: int, routeKey: str, text: str, onClick=None,
                   icon: Union[str, QIcon, FluentIconBase] = None):
        if routeKey in self.items:
            return

        item = SegmentedToggleItem(self)
        item.setText(text)
        item.setToolTip(text)
        if icon:
            item.setIcon(icon)

        self.insertWidget(index, routeKey, item, onClick)
        return item

    def insertWidget(self, index, routeKey, widget, onClick=None):
        """ 完全接管 Pivot.insertWidget

        差异于父类：
        - 不自动选中第一项（toggle 初始 = 什么都不选）
        - 不连接 Pivot._onItemClicked（那是"必选一项"的语义，会吞掉取消事件）
        """
        if routeKey in self.items:
            return

        self.items[routeKey] = widget
        widget.setProperty('routeKey', routeKey)

        widget.itemClicked.connect(
            lambda _=False, it=widget, k=routeKey: self._onItemToggled(it, k))
        if onClick:
            widget.itemClicked.connect(lambda _=False: onClick())

        self.hBoxLayout.insertWidget(index, widget)
        # 不做任何自动选中

        self._normalizeWidths()

    def _normalizeWidths(self):
        items = [it for it in self.items.values() if isinstance(it, SegmentedToggleItem)]
        if not items:
            return
        for i in items:
            i.setFixedWidth(self.width() // len(items))

    # ── toggle 状态机（唯一入口） ───────────────────────────
    def _onItemToggled(self, item, routeKey: str):
        if not item.isEnabled():
            return

        if self._currentKey == routeKey:
            # 点的是当前项 → 取消选中
            self.setCurrentItem(None)
        else:
            self.setCurrentItem(routeKey)

    # ── 状态查询 ────────────────────────────────────────────
    def currentItem(self):
        if self._currentKey is None:
            return None
        return self.items.get(self._currentKey)

    def currentRouteKey(self) -> str:
        return self._currentKey

    def setCurrentItem(self, routeKey, blockSignal=False):
        if routeKey == self._currentKey:
            return
        if routeKey is not None and routeKey not in self.items:
            return

        self._currentKey = routeKey

        for k, it in self.items.items():
            it.setSelected(k == routeKey)

        item = self.currentItem()
        self.slideAni.stop()
        if item is not None:
            self.slideAni.setEndValue(item.x())
            self.slideAni.start()
        else:
            self.slideAni.setValue(0)     # 滑块收回原点，paintEvent 会跳过绘制

        # 关键：显式发出 currentItemChanged，取消时发出空串
        if not blockSignal:
            self.currentItemChanged.emit(routeKey if routeKey is not None else '')

        self.update()

    def currentIndicatorGeometry(self):
        item = self.currentItem()
        return item.x() if item else 0

    # ── 绘制：滑块 ──────────────────────────────────────────
    def paintEvent(self, e):
        QWidget.paintEvent(self, e)

        item = self.currentItem()
        if item is None:                  # 没选中 → 不画滑块
            return

        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        if item.isEnabled():
            painter.setBrush(color.autoFallbackThemeColor(
                self.lightIndicatorColor, self.darkIndicatorColor))
        else:
            painter.setBrush(QColor(255, 255, 255, 30) if isDarkTheme()
                             else QColor(0, 0, 0, 20))

        painter.drawRoundedRect(
            QRectF(self.slideAni.value(), 0, item.width(), item.height()), 4, 4)
