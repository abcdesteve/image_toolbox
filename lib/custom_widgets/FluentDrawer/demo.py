# coding: utf-8
"""
FluentDrawer 演示 —— 左右两个抽屉 + 中间参数控制面板 + 长文本自动换行测试。
"""

from qfluentwidgets import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from __init__ import FluentDrawer, DrawerSide, AutoHideMode
import sys


LONG_TEXT = (
    "FluentDrawer 是一个基于 QFluentWidgets 与 PySide6 的自定义抽屉容器组件，"
    "支持上、下、左、右四个贴靠方向。它的视觉本体是一个悬浮或挤压的面板，"
    "而实际参与布局的只是一个透明的占位符 —— 这让它可以在悬浮模式下展开而"
    "不挤压主内容区，同时在挤压模式下与占位符同步动画。"
    "抽屉支持可选标题、可选 CheckBox（未勾选时内容自动 disable，"
    "行为类似 QGroupBox），并可通过 AutoHideMode 的 Flag 组合叠加多种触发方式："
    "CHECKBOX 与勾选状态双向联动，HOVER 让鼠标进入时以悬浮形式展开，"
    "FOCUS 响应全局鼠标按下 —— 点内部展开、点外部收起。"
    "此外还可以手动拖动手柄调整尺寸，面板会实时跟手。"
    "本段文本用于测试自动换行：当窗口宽度变化，或者左右两侧的抽屉展开收起时，"
    "这段文字应当随着可用宽度自动重新排列，方便观察布局的实时变化。"
    "继续补充一些内容，确保文字足够长，以便清晰地看到折行与行距的表现，"
    "也让左右两个抽屉在开合时中间区域的伸缩更加直观。"
)


class DrawerControlPanel(QFrame):
    """单侧抽屉的参数控制面板。"""

    def __init__(self, drawer: FluentDrawer, name: str, parent=None):
        super().__init__(parent)
        self._drawer = drawer
        self.setStyleSheet("DrawerControlPanel { background: transparent; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(StrongBodyLabel(f"{name}抽屉参数"))
        layout.addWidget(CaptionLabel("自动隐藏模式（Flag 可叠加）"))

        # ── autohide flags ──
        mode = drawer.autohide()
        self.flag_ckb = CheckBox("CHECKBOX · 与勾选双向联动")
        self.flag_hover = CheckBox("HOVER · 鼠标悬浮展开")
        self.flag_focus = CheckBox("FOCUS · 点内部展开 / 点外部收起")
        self.flag_ckb.setChecked(bool(mode & AutoHideMode.CHECKBOX))
        self.flag_hover.setChecked(bool(mode & AutoHideMode.HOVER))
        self.flag_focus.setChecked(bool(mode & AutoHideMode.FOCUS))
        for cb in (self.flag_ckb, self.flag_hover, self.flag_focus):
            cb.stateChanged.connect(self._apply_autohide)
            layout.addWidget(cb)

        # ── 动画 ──
        layout.addLayout(self._switch_row("启用动画", drawer.isAnimated(), drawer.setAnimated))

        # ── 内容 enable ──
        layout.addLayout(self._switch_row("内容启用", drawer.isContentEnabled(), drawer.setContentEnabled))

        # ── 展开尺寸 ──
        row_size = QHBoxLayout()
        row_size.addWidget(BodyLabel("展开尺寸"))
        row_size.addStretch(1)
        self.size_spin = SpinBox()
        self.size_spin.setRange(FluentDrawer.MIN_EXPANDED_SIZE, 800)
        self.size_spin.setSingleStep(20)
        self.size_spin.setValue(drawer.expandedSize())
        self.size_spin.valueChanged.connect(drawer.setExpandedSize)
        row_size.addWidget(self.size_spin)
        layout.addLayout(row_size)

        # ── 手动控制按钮 ──
        row_btn = QHBoxLayout()
        btn_expand = PushButton("展开")
        btn_collapse = PushButton("收起")
        btn_toggle = PushButton("切换")
        btn_expand.clicked.connect(lambda: drawer.expand())
        btn_collapse.clicked.connect(lambda: drawer.collapse())
        btn_toggle.clicked.connect(lambda: drawer.toggle())
        row_btn.addWidget(btn_expand)
        row_btn.addWidget(btn_collapse)
        row_btn.addWidget(btn_toggle)
        layout.addLayout(row_btn)

        layout.addStretch(1)

    def _switch_row(self, label, checked, slot):
        row = QHBoxLayout()
        row.addWidget(BodyLabel(label))
        row.addStretch(1)
        sw = SwitchButton()
        sw.setChecked(checked)
        sw.checkedChanged.connect(slot)
        row.addWidget(sw)
        return row

    def _apply_autohide(self):
        mode = AutoHideMode.NONE
        if self.flag_ckb.isChecked():
            mode |= AutoHideMode.CHECKBOX
        if self.flag_hover.isChecked():
            mode |= AutoHideMode.HOVER
        if self.flag_focus.isChecked():
            mode |= AutoHideMode.FOCUS
        self._drawer.setAutohide(mode)


class DemoWindow(FluentWindow):

    def __init__(self):
        super().__init__()

        self.container = QWidget(self)
        self.container.setObjectName("container")

        self.hLayout = QHBoxLayout(self.container)
        self.hLayout.setContentsMargins(0, 0, 0, 0)
        self.hLayout.setSpacing(0)

        # ── 左侧抽屉 ──
        self.leftDrawer = FluentDrawer(
            title="左侧抽屉",
            side=DrawerSide.LEFT,
            parent=self.container,
            checkbox_enabled=True,
            autohide=AutoHideMode.CHECKBOX | AutoHideMode.HOVER,
            animated=True,
            resizable=True,
            expanded=True,
        )
        self._fill_drawer(self.leftDrawer, "左")

        # ── 右侧抽屉 ──
        self.rightDrawer = FluentDrawer(
            title="右侧抽屉",
            side=DrawerSide.RIGHT,
            parent=self.container,
            checkbox_enabled=True,
            autohide=AutoHideMode.CHECKBOX | AutoHideMode.FOCUS,
            animated=True,
            resizable=True,
            expanded=True,
        )
        self._fill_drawer(self.rightDrawer, "右")

        # ── 中间主内容 ──
        self.mainWidget = QWidget(self.container)
        self.mainWidget.setObjectName("mainWidget")

        mainLayout = QVBoxLayout(self.mainWidget)
        mainLayout.setContentsMargins(40, 32, 40, 32)
        mainLayout.setSpacing(20)

        mainLayout.addWidget(TitleLabel("FluentDrawer 演示"))

        self.textLabel = BodyLabel(LONG_TEXT)
        self.textLabel.setWordWrap(True)
        self.textLabel.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        mainLayout.addWidget(self.textLabel)

        # ── 左右参数面板 ──
        self.leftCtrl = DrawerControlPanel(self.leftDrawer, "左侧")
        self.rightCtrl = DrawerControlPanel(self.rightDrawer, "右侧")

        ctrlRow = QHBoxLayout()
        ctrlRow.setSpacing(40)
        ctrlRow.setContentsMargins(0, 0, 0, 0)
        ctrlRow.addWidget(self.leftCtrl, 1)
        ctrlRow.addWidget(self.rightCtrl, 1)

        ctrlWrap = QFrame()
        ctrlWrap.setStyleSheet("QFrame { background: transparent; }")
        ctrlWrap.setLayout(ctrlRow)
        mainLayout.addWidget(ctrlWrap)

        mainLayout.addStretch(1)

        # ── 组装 ──
        self.hLayout.addWidget(self.leftDrawer)
        self.hLayout.addWidget(self.mainWidget, 1)
        self.hLayout.addWidget(self.rightDrawer)

        self.addSubInterface(self.container, FluentIcon.HOME, "演示")

    def _fill_drawer(self, drawer: FluentDrawer, prefix: str):
        layout = drawer.contentLayout()
        layout.addWidget(StrongBodyLabel(f"{prefix}抽屉内容"))

        btn = PushButton(f"{prefix}侧按钮")
        btn.clicked.connect(lambda: print(f"{prefix}侧按钮被点击"))
        layout.addWidget(btn)

        combo = ComboBox()
        combo.addItems([f"{prefix}选项 A", f"{prefix}选项 B", f"{prefix}选项 C"])
        layout.addWidget(combo)

        line = LineEdit()
        line.setPlaceholderText("输入一些内容…")
        layout.addWidget(line)

        toggle = SwitchButton()
        toggle.setOnText("开")
        toggle.setOffText("关")
        row = QHBoxLayout()
        row.addWidget(BodyLabel(f"{prefix}开关"))
        row.addStretch(1)
        row.addWidget(toggle)
        layout.addLayout(row)

        layout.addStretch(1)


if __name__ == "__main__":
    setTheme(Theme.DARK)
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.resize(1280, 760)
    window.setWindowTitle("FluentDrawer 演示")
    window.show()
    sys.exit(app.exec())