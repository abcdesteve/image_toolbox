from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class RulerWidget(QWidget):
    start_picked = Signal(int)
    end_picked = Signal(int)
    pick_cancelled = Signal()

    THICKNESS = 22
    TICK_LEN = 6

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self.setMouseTracking(True)

        if orientation == Qt.Orientation.Horizontal:
            self.setFixedHeight(self.THICKNESS)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            self.setFixedWidth(self.THICKNESS)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self.image_size = 0
        self.offset = 0
        self.scale = 1.0
        self.candidates = []
        self.selected_start = 0
        self.selected_end = 0
        self.hover_point = None
        self._pending = False
        self._pending_value = None

    def set_params(self, image_size, offset, scale, candidates, sel_start, sel_end):
        self.image_size = image_size
        self.offset = offset
        self.scale = scale
        self.candidates = candidates
        self.selected_start = sel_start
        self.selected_end = sel_end
        self.update()

    def clear(self):
        self.image_size = 0
        self.candidates = []
        self.selected_start = 0
        self.selected_end = 0
        self.hover_point = None
        self._pending = False
        self._pending_value = None
        self.update()

    def _img_to_widget(self, v):
        return self.offset + v * self.scale

    def _widget_to_img(self, v):
        return (v - self.offset) / self.scale if self.scale > 0 else 0

    def _nearest(self, v):
        if not self.candidates:
            return None
        return min(self.candidates, key=lambda c: abs(c - v))

    def paintEvent(self, event):
        if self.image_size <= 0 or self.scale <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        if self.orientation == Qt.Orientation.Horizontal:
            x1 = self._img_to_widget(self.selected_start)
            x2 = self._img_to_widget(self.selected_end)
            if x2 > x1:
                painter.fillRect(int(x1), 0, int(x2 - x1), h,
                                 QColor(100, 160, 255, 35))
            painter.setPen(QPen(QColor(120, 120, 130, 160), 1))
            step = self._calc_step()
            for pos in range(0, self.image_size + 1, step):
                wp = int(self._img_to_widget(pos))
                if 0 <= wp <= w:
                    painter.drawLine(wp, h - self.TICK_LEN, wp, h)
            for c in self.candidates:
                wp = int(self._img_to_widget(c))
                if not (0 <= wp <= w):
                    continue
                if self._pending and self._pending_value is not None \
                        and c == self._pending_value:
                    painter.fillRect(wp - 5, 0, 10, h, QColor(74, 158, 255, 70))
                    painter.setPen(QPen(QColor(74, 158, 255), 3))
                elif self.hover_point is not None and abs(c - self.hover_point) < 2:
                    painter.setPen(QPen(QColor(255, 152, 0), 2))
                else:
                    painter.setPen(QPen(QColor(255, 183, 77, 200), 1))
                painter.drawLine(wp, 0, wp, h)
        else:
            y1 = self._img_to_widget(self.selected_start)
            y2 = self._img_to_widget(self.selected_end)
            if y2 > y1:
                painter.fillRect(0, int(y1), w, int(y2 - y1),
                                 QColor(100, 160, 255, 35))
            painter.setPen(QPen(QColor(120, 120, 130, 160), 1))
            step = self._calc_step()
            for pos in range(0, self.image_size + 1, step):
                wp = int(self._img_to_widget(pos))
                if 0 <= wp <= h:
                    painter.drawLine(w - self.TICK_LEN, wp, w, wp)
            for c in self.candidates:
                wp = int(self._img_to_widget(c))
                if not (0 <= wp <= h):
                    continue
                if self._pending and self._pending_value is not None \
                        and c == self._pending_value:
                    painter.fillRect(0, wp - 5, w, 10, QColor(74, 158, 255, 70))
                    painter.setPen(QPen(QColor(74, 158, 255), 3))
                elif self.hover_point is not None and abs(c - self.hover_point) < 2:
                    painter.setPen(QPen(QColor(255, 152, 0), 2))
                else:
                    painter.setPen(QPen(QColor(255, 183, 77, 200), 1))
                painter.drawLine(0, wp, w, wp)
        painter.end()

    def _calc_step(self):
        if self.scale <= 0:
            return 10
        raw = 60 / self.scale
        for s in [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]:
            if raw <= s:
                return s
        return 1000

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.image_size <= 0 or self.scale <= 0:
            return
        v = self._widget_to_img(
            event.position().x() if self.orientation == Qt.Orientation.Horizontal
            else event.position().y())
        best = None
        best_dist = 15 / self.scale if self.scale > 0 else 15
        for c in self.candidates:
            d = abs(c - v)
            if d < best_dist:
                best_dist = d
                best = c
        if best != self.hover_point:
            self.hover_point = best
            self.update()

    def leaveEvent(self, event):
        self.hover_point = None
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if self.image_size <= 0 or not self.candidates or self.scale <= 0:
            return
        if event.button() == Qt.MouseButton.RightButton:
            self._cancel_pending()
            return
        if event.button() != Qt.MouseButton.LeftButton:
            return
        v = self._widget_to_img(
            event.position().x() if self.orientation == Qt.Orientation.Horizontal
            else event.position().y())
        best = self._nearest(v)
        if best is None:
            return
        if not self._pending:
            self._pending = True
            self._pending_value = best
            self.start_picked.emit(best)
        else:
            self._pending = False
            self._pending_value = None
            self.end_picked.emit(best)
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape and self._pending:
            self._cancel_pending()
        else:
            super().keyPressEvent(event)

    def _cancel_pending(self):
        if self._pending:
            self._pending = False
            self._pending_value = None
            self.update()
            self.pick_cancelled.emit()
