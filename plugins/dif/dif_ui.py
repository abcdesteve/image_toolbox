# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dif.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QSizePolicy, QSpacerItem,
    QStackedWidget, QVBoxLayout, QWidget)

from qfluentwidgets import (BodyLabel, Pivot, PrimaryPushButton, PushButton,
    SegmentedWidget, ToolButton)

class Ui_DifInterface(object):
    def setupUi(self, DifInterface):
        if not DifInterface.objectName():
            DifInterface.setObjectName(u"DifInterface")
        DifInterface.resize(729, 431)
        self.verticalLayout_2 = QVBoxLayout(DifInterface)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(16, 16, 16, 16)
        self.file_row = QHBoxLayout()
        self.file_row.setSpacing(8)
        self.file_row.setObjectName(u"file_row")
        self.btn_pick_A = PushButton(DifInterface)
        self.btn_pick_A.setObjectName(u"btn_pick_A")

        self.file_row.addWidget(self.btn_pick_A)

        self.btn_rot_A = ToolButton(DifInterface)
        self.btn_rot_A.setObjectName(u"btn_rot_A")

        self.file_row.addWidget(self.btn_rot_A)

        self.lbl_path_A = BodyLabel(DifInterface)
        self.lbl_path_A.setObjectName(u"lbl_path_A")
        self.lbl_path_A.setMinimumSize(QSize(180, 0))

        self.file_row.addWidget(self.lbl_path_A)

        self.spacer_file_mid = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.file_row.addItem(self.spacer_file_mid)

        self.lbl_path_B = BodyLabel(DifInterface)
        self.lbl_path_B.setObjectName(u"lbl_path_B")
        self.lbl_path_B.setMinimumSize(QSize(180, 0))
        self.lbl_path_B.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.file_row.addWidget(self.lbl_path_B)

        self.btn_rot_B = ToolButton(DifInterface)
        self.btn_rot_B.setObjectName(u"btn_rot_B")

        self.file_row.addWidget(self.btn_rot_B)

        self.btn_pick_B = PushButton(DifInterface)
        self.btn_pick_B.setObjectName(u"btn_pick_B")

        self.file_row.addWidget(self.btn_pick_B)


        self.verticalLayout.addLayout(self.file_row)

        self.action_row = QHBoxLayout()
        self.action_row.setSpacing(8)
        self.action_row.setObjectName(u"action_row")
        self.btn_step1 = PrimaryPushButton(DifInterface)
        self.btn_step1.setObjectName(u"btn_step1")

        self.action_row.addWidget(self.btn_step1)

        self.btn_step2 = PushButton(DifInterface)
        self.btn_step2.setObjectName(u"btn_step2")
        self.btn_step2.setEnabled(False)

        self.action_row.addWidget(self.btn_step2)

        self.spacer_action_mid = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.action_row.addItem(self.spacer_action_mid)

        self.btn_export = PushButton(DifInterface)
        self.btn_export.setObjectName(u"btn_export")
        self.btn_export.setEnabled(False)

        self.action_row.addWidget(self.btn_export)


        self.verticalLayout.addLayout(self.action_row)

        self.view_row = QHBoxLayout()
        self.view_row.setObjectName(u"view_row")
        self.view_seg = SegmentedWidget(DifInterface)
        self.view_seg.setObjectName(u"view_seg")
        self.view_seg.setMaximumSize(QSize(250, 33))

        self.view_row.addWidget(self.view_seg)

        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.view_row.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.view_row)

        self.view_stack = QStackedWidget(DifInterface)
        self.view_stack.setObjectName(u"view_stack")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.view_stack.sizePolicy().hasHeightForWidth())
        self.view_stack.setSizePolicy(sizePolicy)
        self.page_side = QWidget()
        self.page_side.setObjectName(u"page_side")
        self.side_layout = QHBoxLayout(self.page_side)
        self.side_layout.setSpacing(8)
        self.side_layout.setObjectName(u"side_layout")
        self.side_layout.setContentsMargins(0, 0, 0, 0)
        self.view_stack.addWidget(self.page_side)
        self.page_merged = QWidget()
        self.page_merged.setObjectName(u"page_merged")
        self.merged_layout = QVBoxLayout(self.page_merged)
        self.merged_layout.setSpacing(0)
        self.merged_layout.setObjectName(u"merged_layout")
        self.merged_layout.setContentsMargins(0, 0, 0, 0)
        self.view_stack.addWidget(self.page_merged)

        self.verticalLayout.addWidget(self.view_stack)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(DifInterface)

        self.view_stack.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(DifInterface)
    # setupUi

    def retranslateUi(self, DifInterface):
        DifInterface.setWindowTitle(QCoreApplication.translate("DifInterface", u"\u56fe\u7247\u5bf9\u6bd4", None))
#if QT_CONFIG(tooltip)
        self.btn_pick_A.setToolTip(QCoreApplication.translate("DifInterface", u"\u65e7\u56fe\uff08\u57fa\u51c6\uff09\u3002\u4e5f\u53ef\u4ee5\u76f4\u63a5\u628a\u6587\u4ef6\u62d6\u5230\u7a97\u53e3\u4e0a\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.btn_pick_A.setText(QCoreApplication.translate("DifInterface", u"\u9009\u62e9\u56fe\u7247 A", None))
        self.lbl_path_A.setText(QCoreApplication.translate("DifInterface", u"\u672a\u9009\u62e9", None))
        self.lbl_path_B.setText(QCoreApplication.translate("DifInterface", u"\u672a\u9009\u62e9", None))
#if QT_CONFIG(tooltip)
        self.btn_pick_B.setToolTip(QCoreApplication.translate("DifInterface", u"\u65b0\u56fe\u3002\u4e5f\u53ef\u76f4\u63a5\u62d6\u62fd\u6587\u4ef6\u5230\u7a97\u53e3\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.btn_pick_B.setText(QCoreApplication.translate("DifInterface", u"\u9009\u62e9\u56fe\u7247 B", None))
#if QT_CONFIG(tooltip)
        self.btn_step1.setToolTip(QCoreApplication.translate("DifInterface", u"\u81ea\u52a8\u914d\u51c6 A \u4e0e B\uff0c\u751f\u6210\u5f02\u5f62\u5408\u5e76\u56fe\u4e0e\u8272\u5c42\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.btn_step1.setText(QCoreApplication.translate("DifInterface", u"Step 1 \u00b7 \u5bf9\u9f50\u5e76\u5408\u5e76", None))
#if QT_CONFIG(tooltip)
        self.btn_step2.setToolTip(QCoreApplication.translate("DifInterface", u"\u5728\u914d\u51c6\u6210\u529f\u540e\u624d\u80fd\u6267\u884c\u3002\u68c0\u6d4b\u65b0\u589e/\u5220\u9664/\u7eb9\u7406\u4fee\u6539\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.btn_step2.setText(QCoreApplication.translate("DifInterface", u"Step 2 \u00b7 \u5206\u6790\u53d8\u5316", None))
#if QT_CONFIG(tooltip)
        self.btn_export.setToolTip(QCoreApplication.translate("DifInterface", u"\u300c\u53d8\u5316\u68c0\u6d4b\u300d\u5173\u95ed\u65f6\u5bfc\u51fa\u5408\u5e76\u56fe\uff1b\u5f00\u542f\u65f6\u5bfc\u51fa\u53d8\u5316\u68c0\u6d4b\u7ed3\u679c\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.btn_export.setText(QCoreApplication.translate("DifInterface", u"\u5bfc\u51fa", None))
#if QT_CONFIG(tooltip)
        self.view_seg.setToolTip(QCoreApplication.translate("DifInterface", u"\u5207\u6362\u89c6\u56fe\uff1a\u5e76\u6392\u5bf9\u6bd4 \u6216 \u5f02\u5f62\u5408\u5e76\u7ed3\u679c\u3002", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

