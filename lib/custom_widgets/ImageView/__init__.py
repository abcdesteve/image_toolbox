from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import numpy as np
import cv2

class ImageView(QGraphicsView):
    """显示 BGR ndarray，支持滚轮缩放、拖拽平移、拖拽文件、双击复位。"""

    file_dropped = Signal(str)   # 拖入文件后发出文件路径

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._item = QGraphicsPixmapItem()
        self._item.setTransformationMode(Qt.SmoothTransformation)
        self._scene.addItem(self._item)

        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setFrameShape(QFrame.NoFrame)
        self.setBackgroundBrush(QColor(28, 28, 28))

        self._has_image = False
        self._fit_mode = True
        self._drag_over = False          # 拖拽悬停标记

        self.setAcceptDrops(True)        # 关键：允许接收拖拽

    # ---------- 公共 API ----------

    def set_image_bgr(self, img_bgr: np.ndarray | None) -> None:
        if img_bgr is None:
            self.clear_image()
            return
        if img_bgr.ndim == 2:
            rgb = cv2.cvtColor(img_bgr, cv2.COLOR_GRAY2RGB)
        else:
            rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        rgb = np.ascontiguousarray(rgb)
        h, w = rgb.shape[:2]
        qimg = QImage(rgb.data, w, h, rgb.strides[0],
                      QImage.Format_RGB888).copy()
        self._item.setPixmap(QPixmap.fromImage(qimg))
        self._scene.setSceneRect(0, 0, w, h)
        self._has_image = True
        self._fit_mode = True
        self.fit_view()

    def clear_image(self) -> None:
        self._item.setPixmap(QPixmap())
        self._has_image = False
        self.viewport().update()

    def fit_view(self) -> None:
        if not self._has_image:
            return
        self.resetTransform()
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
        self._fit_mode = True

    # ---------- 拖拽事件 ----------

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._drag_over = True
            self.viewport().update()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._drag_over = False
        self.viewport().update()
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        self._drag_over = False
        self.viewport().update()
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.file_dropped.emit(path)
        event.acceptProposedAction()

    # ---------- 绘制虚线边框 ----------

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._drag_over:
            return
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(74, 158, 255), 2, Qt.PenStyle.DashLine))
        painter.setBrush(QColor(74, 158, 255, 30))
        painter.drawRoundedRect(
            self.viewport().rect().adjusted(1, 1, -1, -1), 12, 12)
        painter.end()

    # ---------- 缩放/复位事件 ----------

    def wheelEvent(self, event):
        if not self._has_image:
            return
        delta = event.angleDelta().y()
        if delta == 0:
            return
        factor = 1.15 if delta > 0 else 1.0 / 1.15
        cur = self.transform().m11()
        nxt = cur * factor
        if nxt < 0.02 or nxt > 40:
            return
        self.scale(factor, factor)
        self._fit_mode = False

    def mouseDoubleClickEvent(self, event):
        self.fit_view()

    def mousePressEvent(self, event):
        self._fit_mode = False
        super().mousePressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._has_image and self._fit_mode:
            self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
