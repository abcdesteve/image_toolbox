from PySide6.QtWidgets import *
from PySide6.QtCore import *
from qfluentwidgets import *


class AboutInterface(QWidget):
    def __init__(self,parent):
        super().__init__(parent)
        self.setObjectName("aboutInterface")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)

        title = BodyLabel("纯色区域智能裁剪工具")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        desc = CaptionLabel(
            "• 自动检测图片中的纯色段，生成横/竖吸附点\n"
            "• 标尺单击依次选择起点、终点（右键取消）\n"
            "• 图片四角可直接拖拽，自动吸附到最近吸附点\n"
            "• 四角拖拽不会重合，始终保留最小裁剪尺寸\n"
            "• 「快速保存」保存为 crop_原名.原扩展名；\n"
            "  下拉箭头可「另存为」到其他路径/格式\n"
            "• 同格式输出时保持原画质，可选保留 EXIF"
        )
        desc.setStyleSheet("font-size: 13px; color: #aaa; line-height: 1.8;")
        layout.addWidget(desc)
        layout.addStretch()
