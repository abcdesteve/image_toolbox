from qfluentwidgets import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from __init__ import *
import sys


class DemoWindow(FluentWindow):
    """主窗口 —— 带 Mica 效果的 Fluent 窗口"""

    def __init__(self):
        super().__init__()

        # ── 用一个容器承载「抽屉 + 主内容区」，交给布局自动管理 ──
        self.container = QWidget(self)
        self.container.setObjectName("container")

        self.hLayout = QHBoxLayout(self.container)
        self.hLayout.setContentsMargins(0, 0, 0, 0)
        self.hLayout.setSpacing(0)

        # ── 主内容区（长文本自动换行）──
        self.mainWidget = QWidget(self.container)
        self.mainWidget.setObjectName("mainWidget")

        vLayout = QVBoxLayout(self.mainWidget)
        vLayout.setContentsMargins(40, 40, 40, 40)
        vLayout.setSpacing(20)

        long_text = (
            "这是一段用于测试自动换行的长文本。FluentDrawer 是一个基于 "
            "QFluentWidgets 的自定义抽屉容器组件，支持上、下、左、右四个贴靠方向，"
            "可选标题与 CheckBox，未勾选 CheckBox 时内部内容会自动禁用，"
            "行为类似 QGroupBox。它还支持三种自动隐藏模式（关联 CheckBox、"
            "鼠标进入离开、失去焦点），可以手动控制展开与收起，"
            "并且可以通过拖动条调整尺寸。整体风格遵循 Fluent Design，"
            "非贴靠侧带有圆角，面板背景色参照 Fluent 对话框按钮栏层，"
            "在 Mica 主窗口上呈现半透明的毛玻璃效果。"
            "这段文字会随着窗口宽度变化自动换行，方便观察抽屉展开和收起时"
            "主内容区的布局变化。"
        )

        self.textLabel = BodyLabel(long_text, self.mainWidget)
        self.textLabel.setWordWrap(True)
        self.textLabel.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        vLayout.addWidget(self.textLabel, 1)

        # ── 创建抽屉 ──
        self.drawer = FluentDrawer(
            title='None',
            side=DrawerSide.LEFT,
            parent=self.container,
            checkbox_enabled=True,
            autohide=AutoHideMode.FOCUS,
            animated=True,
            resizable=True,
            expanded=True,
        )

        # 抽屉内放一个按钮
        self.drawerButton = PushButton("抽屉里的按钮", self.drawer)
        self.drawerButton.clicked.connect(self._onDrawerButtonClicked)
        self.drawer.contentLayout().addWidget(self.drawerButton)
        self.drawer.contentLayout().addStretch(1)

        # ── 组装布局：抽屉在右，主内容区在左 ──
        self.hLayout.addWidget(self.mainWidget, 1)
        self.hLayout.insertWidget(0, self.drawer)

        self.addSubInterface(self.container, FluentIcon.ZOOM_OUT, 'test')

        # 监听展开/收起
        self.drawer.expanded.connect(self._onDrawerToggled)
        self.drawer.collapsed.connect(self._onDrawerToggled)

    def _onDrawerToggled(self):
        # 布局会自动重排，这里只做日志
        state = "展开" if self.drawer.isExpanded() else "收起"
        print(f"抽屉状态: {state}")

    def _onDrawerButtonClicked(self):
        print("抽屉里的按钮被点击了")


if __name__ == "__main__":
    setTheme(Theme.DARK)

    app = QApplication(sys.argv)
    window = DemoWindow()
    window.resize(960, 640)
    window.setWindowTitle("FluentDrawer 测试")
    window.show()
    sys.exit(app.exec())
