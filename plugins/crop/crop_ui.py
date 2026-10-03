# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'crop.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

from qfluentwidgets import (BodyLabel, CaptionLabel, CheckBox, ComboBox,
    PrimaryPushButton, PushButton, SplitPushButton)

class Ui_cropInterface(object):
    def setupUi(self, cropInterface):
        if not cropInterface.objectName():
            cropInterface.setObjectName(u"cropInterface")
        cropInterface.resize(1500, 700)
        cropInterface.setAutoFillBackground(False)
        self.mainLayout = QVBoxLayout(cropInterface)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.content = QWidget(cropInterface)
        self.content.setObjectName(u"content")
        self.content.setAutoFillBackground(False)
        self.contentLayout = QVBoxLayout(self.content)
        self.contentLayout.setSpacing(12)
        self.contentLayout.setObjectName(u"contentLayout")
        self.contentLayout.setContentsMargins(20, 20, 20, 12)
        self.toolbarLayout = QHBoxLayout()
        self.toolbarLayout.setSpacing(10)
        self.toolbarLayout.setObjectName(u"toolbarLayout")
        self.btn_load = PrimaryPushButton(self.content)
        self.btn_load.setObjectName(u"btn_load")

        self.toolbarLayout.addWidget(self.btn_load)

        self.btn_reset = PushButton(self.content)
        self.btn_reset.setObjectName(u"btn_reset")
        self.btn_reset.setEnabled(False)

        self.toolbarLayout.addWidget(self.btn_reset)

        self.lbl_info = CaptionLabel(self.content)
        self.lbl_info.setObjectName(u"lbl_info")

        self.toolbarLayout.addWidget(self.lbl_info)

        self.toolbarSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.toolbarLayout.addItem(self.toolbarSpacer)

        self.chk_exif = CheckBox(self.content)
        self.chk_exif.setObjectName(u"chk_exif")
        self.chk_exif.setEnabled(False)
        self.chk_exif.setChecked(True)

        self.toolbarLayout.addWidget(self.chk_exif)

        self.btn_save = SplitPushButton(self.content)
        self.btn_save.setObjectName(u"btn_save")
        self.btn_save.setEnabled(False)

        self.toolbarLayout.addWidget(self.btn_save)


        self.contentLayout.addLayout(self.toolbarLayout)

        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setObjectName(u"grid")
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.corner = QWidget(self.content)
        self.corner.setObjectName(u"corner")
        self.corner.setMinimumSize(QSize(22, 22))
        self.corner.setMaximumSize(QSize(22, 22))
        self.corner.setAutoFillBackground(False)

        self.grid.addWidget(self.corner, 0, 0, 1, 1)


        self.contentLayout.addLayout(self.grid)

        self.contentLayout.setStretch(1, 100)

        self.mainLayout.addWidget(self.content)

        self.snap_panel = QFrame(cropInterface)
        self.snap_panel.setObjectName(u"snap_panel")
        self.snap_panel.setStyleSheet(u"QFrame#snap_panel {\n"
"    background-color: rgba(0, 0, 0, 0.22);\n"
"    border: none;\n"
"    border-top: 1px solid rgba(255, 255, 255, 0.08);\n"
"    border-top-left-radius: 10px;\n"
"}\n"
"QFrame#snap_panel QLabel {\n"
"    background: transparent;\n"
"}")
        self.snapLayout = QHBoxLayout(self.snap_panel)
        self.snapLayout.setSpacing(24)
        self.snapLayout.setObjectName(u"snapLayout")
        self.snapLayout.setContentsMargins(28, 20, 28, 20)
        self.vGroup = QVBoxLayout()
        self.vGroup.setSpacing(6)
        self.vGroup.setObjectName(u"vGroup")
        self.v_title = BodyLabel(self.snap_panel)
        self.v_title.setObjectName(u"v_title")
        self.v_title.setStyleSheet(u"font-weight: bold; color: #4a9eff; background: transparent;")

        self.vGroup.addWidget(self.v_title)

        self.v_start_title = CaptionLabel(self.snap_panel)
        self.v_start_title.setObjectName(u"v_start_title")

        self.vGroup.addWidget(self.v_start_title)

        self.v_start_combo = ComboBox(self.snap_panel)
        self.v_start_combo.setObjectName(u"v_start_combo")
        self.v_start_combo.setMinimumSize(QSize(180, 0))

        self.vGroup.addWidget(self.v_start_combo)

        self.v_end_title = CaptionLabel(self.snap_panel)
        self.v_end_title.setObjectName(u"v_end_title")

        self.vGroup.addWidget(self.v_end_title)

        self.v_end_combo = ComboBox(self.snap_panel)
        self.v_end_combo.setObjectName(u"v_end_combo")
        self.v_end_combo.setMinimumSize(QSize(180, 0))

        self.vGroup.addWidget(self.v_end_combo)

        self.vGroup.setStretch(0, 1)

        self.snapLayout.addLayout(self.vGroup)

        self.hGroup = QVBoxLayout()
        self.hGroup.setSpacing(6)
        self.hGroup.setObjectName(u"hGroup")
        self.h_title = BodyLabel(self.snap_panel)
        self.h_title.setObjectName(u"h_title")
        self.h_title.setStyleSheet(u"font-weight: bold; color: #4a9eff; background: transparent;")

        self.hGroup.addWidget(self.h_title)

        self.h_start_title = CaptionLabel(self.snap_panel)
        self.h_start_title.setObjectName(u"h_start_title")

        self.hGroup.addWidget(self.h_start_title)

        self.h_start_combo = ComboBox(self.snap_panel)
        self.h_start_combo.setObjectName(u"h_start_combo")
        self.h_start_combo.setMinimumSize(QSize(180, 0))

        self.hGroup.addWidget(self.h_start_combo)

        self.h_end_title = CaptionLabel(self.snap_panel)
        self.h_end_title.setObjectName(u"h_end_title")

        self.hGroup.addWidget(self.h_end_title)

        self.h_end_combo = ComboBox(self.snap_panel)
        self.h_end_combo.setObjectName(u"h_end_combo")
        self.h_end_combo.setMinimumSize(QSize(180, 0))

        self.hGroup.addWidget(self.h_end_combo)

        self.hGroup.setStretch(0, 1)

        self.snapLayout.addLayout(self.hGroup)


        self.mainLayout.addWidget(self.snap_panel)

        self.mainLayout.setStretch(0, 100)

        self.retranslateUi(cropInterface)

        QMetaObject.connectSlotsByName(cropInterface)
    # setupUi

    def retranslateUi(self, cropInterface):
        cropInterface.setWindowTitle(QCoreApplication.translate("cropInterface", u"\u7eaf\u8272\u533a\u57df\u667a\u80fd\u88c1\u526a\u5de5\u5177", None))
        self.btn_load.setText(QCoreApplication.translate("cropInterface", u"\u9009\u62e9\u56fe\u7247", None))
        self.btn_reset.setText(QCoreApplication.translate("cropInterface", u"\u91cd\u8bbe\u88c1\u526a\u8303\u56f4", None))
        self.lbl_info.setText(QCoreApplication.translate("cropInterface", u"\u5c1a\u672a\u52a0\u8f7d\u56fe\u7247", None))
        self.chk_exif.setText(QCoreApplication.translate("cropInterface", u"\u4fdd\u7559\u539f\u56fe EXIF", None))
        self.btn_save.setProperty(u"text_", QCoreApplication.translate("cropInterface", u"\u5feb\u901f\u4fdd\u5b58", None))
        self.btn_save.setProperty(u"text", "")
        self.v_title.setText(QCoreApplication.translate("cropInterface", u"\u7ad6\u76f4\u65b9\u5411  \u2195", None))
        self.v_start_title.setText(QCoreApplication.translate("cropInterface", u"\u5934\uff08\u4e0a\u8fb9\u754c\u00b7\u8d77\u59cb\u884c\uff09", None))
        self.v_end_title.setText(QCoreApplication.translate("cropInterface", u"\u5c3e\uff08\u4e0b\u8fb9\u754c\u00b7\u7ed3\u675f\u884c\uff09", None))
        self.h_title.setText(QCoreApplication.translate("cropInterface", u"\u6c34\u5e73\u65b9\u5411  \u2194", None))
        self.h_start_title.setText(QCoreApplication.translate("cropInterface", u"\u5de6\uff08\u5de6\u8fb9\u754c\u00b7\u8d77\u59cb\u5217\uff09", None))
        self.h_end_title.setText(QCoreApplication.translate("cropInterface", u"\u53f3\uff08\u53f3\u8fb9\u754c\u00b7\u7ed3\u675f\u5217\uff09", None))
    # retranslateUi

