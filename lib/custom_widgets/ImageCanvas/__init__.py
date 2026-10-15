from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class ImageCanvas(QLabel):
    image_dropped = Signal(str)
    crop_changed = Signal(int, int, int, int)

    HIT_RADIUS = 16
    CORNER_LEN = 14
    MIN_CROP_SIZE = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(400, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self.setStyleSheet("ImageCanvas { background: transparent; border: none; }")

        self._pixmap = None
        self._drag_over = False
        self.crop_x1 = self.crop_y1 = 0
        self.crop_x2 = self.crop_y2 = 0
        self.has_image = False
        self.h_candidates = []
        self.v_candidates = []
        self._drag_handle = None
        self._drag_start_pos = None
        self._drag_original_crop = None

    def set_candidates(self, h_candidates, v_candidates):
        self.h_candidates = h_candidates
        self.v_candidates = v_candidates

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(
                        ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')):
                    event.acceptProposedAction()
                    self._drag_over = True
                    self.update()
                    return
        event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        self._drag_over = False
        self.update()

    def dropEvent(self, event: QDropEvent):
        self._drag_over = False
        self.update()
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')):
                self.image_dropped.emit(path)
                event.acceptProposedAction()
                return
        event.ignore()

    def set_image(self, pixmap: QPixmap, crop_rect=None):
        self._pixmap = pixmap
        self.has_image = True
        if crop_rect:
            self.crop_x1, self.crop_y1, self.crop_x2, self.crop_y2 = crop_rect
        self.update()

    def _get_display_rect(self):
        if self._pixmap is None:
            return QRect(), 1.0
        pw, ph = self._pixmap.width(), self._pixmap.height()
        cw, ch = self.width(), self.height()
        if pw == 0 or ph == 0:
            return QRect(), 1.0
        scale = min(cw / pw, ch / ph, 1.0)
        dw, dh = int(pw * scale), int(ph * scale)
        return QRect(0, 0, dw, dh), scale

    def _crop_screen_rect(self):
        rect, scale = self._get_display_rect()
        cx1 = rect.x() + int(self.crop_x1 * scale)
        cy1 = rect.y() + int(self.crop_y1 * scale)
        cx2 = rect.x() + int(self.crop_x2 * scale)
        cy2 = rect.y() + int(self.crop_y2 * scale)
        return QRect(QPoint(cx1, cy1), QPoint(cx2, cy2))

    def _hit_test(self, pos):
        if not self.has_image:
            return None
        r = self._crop_screen_rect()
        x, y = pos.x(), pos.y()
        hr = self.HIT_RADIUS
        if abs(x - r.left()) < hr and abs(y - r.top()) < hr:
            return 'tl'
        if abs(x - r.right()) < hr and abs(y - r.top()) < hr:
            return 'tr'
        if abs(x - r.left()) < hr and abs(y - r.bottom()) < hr:
            return 'bl'
        if abs(x - r.right()) < hr and abs(y - r.bottom()) < hr:
            return 'br'
        return None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() != Qt.MouseButton.LeftButton or self._pixmap is None:
            return super().mousePressEvent(event)
        handle = self._hit_test(event.position().toPoint())
        if handle:
            self._drag_handle = handle
            self._drag_start_pos = event.position().toPoint()
            self._drag_original_crop = (self.crop_x1, self.crop_y1,
                                        self.crop_x2, self.crop_y2)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()
        if self._drag_handle and self._drag_original_crop:
            delta = pos - self._drag_start_pos
            _, scale = self._get_display_rect()
            if scale <= 0:
                return
            dx, dy = delta.x() / scale, delta.y() / scale
            x1, y1, x2, y2 = self._drag_original_crop
            pw, ph = self._pixmap.width(), self._pixmap.height()
            MIN = self.MIN_CROP_SIZE

            if self._drag_handle == 'tl':
                x1 = max(0, min(x1 + dx, x2 - MIN))
                y1 = max(0, min(y1 + dy, y2 - MIN))
            elif self._drag_handle == 'tr':
                x2 = min(pw, max(x2 + dx, x1 + MIN))
                y1 = max(0, min(y1 + dy, y2 - MIN))
            elif self._drag_handle == 'bl':
                x1 = max(0, min(x1 + dx, x2 - MIN))
                y2 = min(ph, max(y2 + dy, y1 + MIN))
            elif self._drag_handle == 'br':
                x2 = min(pw, max(x2 + dx, x1 + MIN))
                y2 = min(ph, max(y2 + dy, y1 + MIN))

            if self._drag_handle in ('tl', 'bl'):
                snapped = self._snap(x1, self.v_candidates)
                if snapped < x2 - MIN:
                    x1 = snapped
            else:
                snapped = self._snap(x2, self.v_candidates)
                if snapped > x1 + MIN:
                    x2 = snapped

            if self._drag_handle in ('tl', 'tr'):
                snapped = self._snap(y1, self.h_candidates)
                if snapped < y2 - MIN:
                    y1 = snapped
            else:
                snapped = self._snap(y2, self.h_candidates)
                if snapped > y1 + MIN:
                    y2 = snapped

            self.crop_x1, self.crop_y1, self.crop_x2, self.crop_y2 = \
                int(x1), int(y1), int(x2), int(y2)
            self.crop_changed.emit(self.crop_x1, self.crop_y1,
                                   self.crop_x2, self.crop_y2)
            self.update()
            event.accept()
        else:
            handle = self._hit_test(pos)
            if handle in ('tl', 'br'):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif handle in ('tr', 'bl'):
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_handle = None
        self._drag_start_pos = None
        self._drag_original_crop = None
        super().mouseReleaseEvent(event)

    def _snap(self, value, candidates):
        if not candidates:
            return value
        return min(candidates, key=lambda c: abs(c - value))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._drag_over:
            painter.setPen(QPen(QColor(74, 158, 255), 2, Qt.PenStyle.DashLine))
            painter.setBrush(QColor(74, 158, 255, 30))
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)
        elif self._pixmap is None:
            painter.setPen(QPen(QColor(160, 160, 170, 120), 2, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)

        if self._pixmap is None:
            painter.setPen(QColor(200, 200, 210, 180))
            font = QFont()
            font.setPointSize(14)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "拖拽图片到此处\n或点击上方按钮选择图片")
            painter.end()
            return

        rect, scale = self._get_display_rect()
        painter.drawPixmap(rect, self._pixmap)

        if self.has_image:
            cx1 = rect.x() + int(self.crop_x1 * scale)
            cy1 = rect.y() + int(self.crop_y1 * scale)
            cx2 = rect.x() + int(self.crop_x2 * scale)
            cy2 = rect.y() + int(self.crop_y2 * scale)

            overlay = QColor(0, 0, 0, 130)
            painter.fillRect(rect.x(), rect.y(), rect.width(), cy1 - rect.y(), overlay)
            painter.fillRect(rect.x(), cy2, rect.width(), rect.bottom() - cy2, overlay)
            painter.fillRect(rect.x(), cy1, cx1 - rect.x(), cy2 - cy1, overlay)
            painter.fillRect(cx2, cy1, rect.right() - cx2, cy2 - cy1, overlay)

            painter.setPen(QPen(QColor(74, 158, 255), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRect(QPoint(cx1, cy1), QPoint(cx2, cy2)))

            painter.setPen(QPen(QColor(74, 158, 255), 3,
                                Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            cl = self.CORNER_LEN
            for px, py, dx, dy in [
                (cx1, cy1, 1, 1), (cx2, cy1, -1, 1),
                (cx1, cy2, 1, -1), (cx2, cy2, -1, -1)
            ]:
                painter.drawLine(px, py, px + dx * cl, py)
                painter.drawLine(px, py, px, py + dy * cl)

        painter.end()
