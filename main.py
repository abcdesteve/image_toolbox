from PySide6.QtWidgets import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF

from plugins.crop import *
from plugins.dif import *
from plugins.about import *

import sys


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("神龙图片工具箱 v2.0")
        self.setWindowIcon(FIF.icon(FIF.PHOTO))
        self.resize(900, 600)

        self.cropInterface = CropInterface(self)
        self.addSubInterface(self.cropInterface, FIF.CUT, "智能裁剪")

        self.difInterface = DifInterface(self)
        self.addSubInterface(self.difInterface, FIF.SEARCH, "图片对比")

        self.aboutInterface = AboutInterface(self)
        self.addSubInterface(self.aboutInterface, FIF.INFO, "关于", NavigationItemPosition.BOTTOM)

        self.navigationInterface.setExpandWidth(180)
        try:
            self.setMicaEffectEnabled(True)
        except Exception:
            pass
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    setTheme(Theme.DARK)
    window = MainWindow()
    app.setWindowIcon(FIF.icon(FIF.PHOTO))
    sys.exit(app.exec())
