# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'advance_panel.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QHBoxLayout,
    QSizePolicy, QWidget)

from qfluentwidgets import (BodyLabel, CheckBox, ComboBox, CompactDoubleSpinBox,
    CompactSpinBox, StrongBodyLabel)

class Ui_AdvancePanel(object):
    def setupUi(self, AdvancePanel):
        if not AdvancePanel.objectName():
            AdvancePanel.setObjectName(u"AdvancePanel")
        AdvancePanel.resize(757, 300)
        self.horizontalLayout = QHBoxLayout(AdvancePanel)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.form_reg = QFormLayout()
        self.form_reg.setObjectName(u"form_reg")
        self.form_reg.setLabelAlignment(Qt.AlignVCenter)
        self.form_reg.setHorizontalSpacing(2)
        self.form_reg.setVerticalSpacing(4)
        self.lbl_grp_reg = StrongBodyLabel(AdvancePanel)
        self.lbl_grp_reg.setObjectName(u"lbl_grp_reg")

        self.form_reg.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.lbl_grp_reg)

        self.lbl_feature = BodyLabel(AdvancePanel)
        self.lbl_feature.setObjectName(u"lbl_feature")

        self.form_reg.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lbl_feature)

        self.combo_feature = ComboBox(AdvancePanel)
        self.combo_feature.setObjectName(u"combo_feature")

        self.form_reg.setWidget(1, QFormLayout.ItemRole.FieldRole, self.combo_feature)

        self.lbl_ratio = BodyLabel(AdvancePanel)
        self.lbl_ratio.setObjectName(u"lbl_ratio")

        self.form_reg.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lbl_ratio)

        self.spin_ratio = CompactDoubleSpinBox(AdvancePanel)
        self.spin_ratio.setObjectName(u"spin_ratio")
        self.spin_ratio.setDecimals(2)
        self.spin_ratio.setMinimum(0.400000000000000)
        self.spin_ratio.setMaximum(1.000000000000000)
        self.spin_ratio.setSingleStep(0.010000000000000)
        self.spin_ratio.setValue(0.720000000000000)

        self.form_reg.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spin_ratio)

        self.lbl_ransac = BodyLabel(AdvancePanel)
        self.lbl_ransac.setObjectName(u"lbl_ransac")

        self.form_reg.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lbl_ransac)

        self.spin_ransac = CompactDoubleSpinBox(AdvancePanel)
        self.spin_ransac.setObjectName(u"spin_ransac")
        self.spin_ransac.setDecimals(1)
        self.spin_ransac.setMinimum(0.500000000000000)
        self.spin_ransac.setMaximum(20.000000000000000)
        self.spin_ransac.setSingleStep(0.500000000000000)
        self.spin_ransac.setValue(3.000000000000000)

        self.form_reg.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spin_ransac)

        self.lbl_min_match = BodyLabel(AdvancePanel)
        self.lbl_min_match.setObjectName(u"lbl_min_match")

        self.form_reg.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lbl_min_match)

        self.spin_min_match = CompactSpinBox(AdvancePanel)
        self.spin_min_match.setObjectName(u"spin_min_match")
        self.spin_min_match.setMinimum(4)
        self.spin_min_match.setMaximum(200)
        self.spin_min_match.setValue(12)

        self.form_reg.setWidget(4, QFormLayout.ItemRole.FieldRole, self.spin_min_match)

        self.lbl_min_inlier = BodyLabel(AdvancePanel)
        self.lbl_min_inlier.setObjectName(u"lbl_min_inlier")

        self.form_reg.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lbl_min_inlier)

        self.spin_min_inlier = CompactDoubleSpinBox(AdvancePanel)
        self.spin_min_inlier.setObjectName(u"spin_min_inlier")
        self.spin_min_inlier.setDecimals(2)
        self.spin_min_inlier.setMinimum(0.000000000000000)
        self.spin_min_inlier.setMaximum(1.000000000000000)
        self.spin_min_inlier.setSingleStep(0.050000000000000)
        self.spin_min_inlier.setValue(0.250000000000000)

        self.form_reg.setWidget(5, QFormLayout.ItemRole.FieldRole, self.spin_min_inlier)


        self.horizontalLayout.addLayout(self.form_reg)

        self.form_tps = QFormLayout()
        self.form_tps.setObjectName(u"form_tps")
        self.form_tps.setLabelAlignment(Qt.AlignVCenter)
        self.form_tps.setHorizontalSpacing(2)
        self.form_tps.setVerticalSpacing(4)
        self.chk_tps = CheckBox(AdvancePanel)
        self.chk_tps.setObjectName(u"chk_tps")
        self.chk_tps.setChecked(True)

        self.form_tps.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.chk_tps)

        self.lbl_tps_ctrl = BodyLabel(AdvancePanel)
        self.lbl_tps_ctrl.setObjectName(u"lbl_tps_ctrl")

        self.form_tps.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lbl_tps_ctrl)

        self.spin_tps_ctrl = CompactSpinBox(AdvancePanel)
        self.spin_tps_ctrl.setObjectName(u"spin_tps_ctrl")
        self.spin_tps_ctrl.setMinimum(8)
        self.spin_tps_ctrl.setMaximum(1000)
        self.spin_tps_ctrl.setValue(150)

        self.form_tps.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spin_tps_ctrl)

        self.lbl_tps_smooth = BodyLabel(AdvancePanel)
        self.lbl_tps_smooth.setObjectName(u"lbl_tps_smooth")

        self.form_tps.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lbl_tps_smooth)

        self.spin_tps_smooth = CompactDoubleSpinBox(AdvancePanel)
        self.spin_tps_smooth.setObjectName(u"spin_tps_smooth")
        self.spin_tps_smooth.setDecimals(2)
        self.spin_tps_smooth.setMinimum(0.000000000000000)
        self.spin_tps_smooth.setMaximum(20.000000000000000)
        self.spin_tps_smooth.setSingleStep(0.050000000000000)
        self.spin_tps_smooth.setValue(0.100000000000000)

        self.form_tps.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spin_tps_smooth)

        self.lbl_tps_step = BodyLabel(AdvancePanel)
        self.lbl_tps_step.setObjectName(u"lbl_tps_step")

        self.form_tps.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lbl_tps_step)

        self.spin_tps_step = CompactSpinBox(AdvancePanel)
        self.spin_tps_step.setObjectName(u"spin_tps_step")
        self.spin_tps_step.setMinimum(4)
        self.spin_tps_step.setMaximum(128)
        self.spin_tps_step.setSingleStep(4)
        self.spin_tps_step.setValue(16)

        self.form_tps.setWidget(4, QFormLayout.ItemRole.FieldRole, self.spin_tps_step)

        self.lbl_grp_tps = StrongBodyLabel(AdvancePanel)
        self.lbl_grp_tps.setObjectName(u"lbl_grp_tps")

        self.form_tps.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.lbl_grp_tps)


        self.horizontalLayout.addLayout(self.form_tps)

        self.form_photo = QFormLayout()
        self.form_photo.setObjectName(u"form_photo")
        self.form_photo.setLabelAlignment(Qt.AlignVCenter)
        self.form_photo.setHorizontalSpacing(2)
        self.form_photo.setVerticalSpacing(4)
        self.lbl_grp_photo = StrongBodyLabel(AdvancePanel)
        self.lbl_grp_photo.setObjectName(u"lbl_grp_photo")

        self.form_photo.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.lbl_grp_photo)

        self.lbl_photo_method = BodyLabel(AdvancePanel)
        self.lbl_photo_method.setObjectName(u"lbl_photo_method")

        self.form_photo.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lbl_photo_method)

        self.combo_photo_method = ComboBox(AdvancePanel)
        self.combo_photo_method.setObjectName(u"combo_photo_method")

        self.form_photo.setWidget(1, QFormLayout.ItemRole.FieldRole, self.combo_photo_method)


        self.horizontalLayout.addLayout(self.form_photo)

        self.line = QFrame(AdvancePanel)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line)

        self.form_diff = QFormLayout()
        self.form_diff.setObjectName(u"form_diff")
        self.form_diff.setLabelAlignment(Qt.AlignVCenter)
        self.form_diff.setHorizontalSpacing(2)
        self.form_diff.setVerticalSpacing(4)
        self.lbl_grp_diff = StrongBodyLabel(AdvancePanel)
        self.lbl_grp_diff.setObjectName(u"lbl_grp_diff")

        self.form_diff.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.lbl_grp_diff)

        self.lbl_lab_thresh = BodyLabel(AdvancePanel)
        self.lbl_lab_thresh.setObjectName(u"lbl_lab_thresh")

        self.form_diff.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lbl_lab_thresh)

        self.spin_lab_thresh = CompactDoubleSpinBox(AdvancePanel)
        self.spin_lab_thresh.setObjectName(u"spin_lab_thresh")
        self.spin_lab_thresh.setDecimals(1)
        self.spin_lab_thresh.setMinimum(1.000000000000000)
        self.spin_lab_thresh.setMaximum(120.000000000000000)
        self.spin_lab_thresh.setSingleStep(1.000000000000000)
        self.spin_lab_thresh.setValue(25.000000000000000)

        self.form_diff.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spin_lab_thresh)

        self.lbl_ssim_thresh = BodyLabel(AdvancePanel)
        self.lbl_ssim_thresh.setObjectName(u"lbl_ssim_thresh")

        self.form_diff.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lbl_ssim_thresh)

        self.spin_ssim_thresh = CompactDoubleSpinBox(AdvancePanel)
        self.spin_ssim_thresh.setObjectName(u"spin_ssim_thresh")
        self.spin_ssim_thresh.setDecimals(2)
        self.spin_ssim_thresh.setMinimum(0.000000000000000)
        self.spin_ssim_thresh.setMaximum(1.000000000000000)
        self.spin_ssim_thresh.setSingleStep(0.050000000000000)
        self.spin_ssim_thresh.setValue(0.600000000000000)

        self.form_diff.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spin_ssim_thresh)

        self.lbl_min_area = BodyLabel(AdvancePanel)
        self.lbl_min_area.setObjectName(u"lbl_min_area")

        self.form_diff.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lbl_min_area)

        self.spin_min_area = CompactSpinBox(AdvancePanel)
        self.spin_min_area.setObjectName(u"spin_min_area")
        self.spin_min_area.setMinimum(1)
        self.spin_min_area.setMaximum(10000)
        self.spin_min_area.setSingleStep(10)
        self.spin_min_area.setValue(80)

        self.form_diff.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spin_min_area)

        self.lbl_morph = BodyLabel(AdvancePanel)
        self.lbl_morph.setObjectName(u"lbl_morph")

        self.form_diff.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lbl_morph)

        self.spin_morph = CompactSpinBox(AdvancePanel)
        self.spin_morph.setObjectName(u"spin_morph")
        self.spin_morph.setMinimum(1)
        self.spin_morph.setMaximum(31)
        self.spin_morph.setSingleStep(2)
        self.spin_morph.setValue(3)

        self.form_diff.setWidget(4, QFormLayout.ItemRole.FieldRole, self.spin_morph)


        self.horizontalLayout.addLayout(self.form_diff)


        self.retranslateUi(AdvancePanel)

        QMetaObject.connectSlotsByName(AdvancePanel)
    # setupUi

    def retranslateUi(self, AdvancePanel):
        AdvancePanel.setWindowTitle(QCoreApplication.translate("AdvancePanel", u"Form", None))
        self.lbl_grp_reg.setText(QCoreApplication.translate("AdvancePanel", u"\u7279\u5f81\u5339\u914d\uff08\u7c97\u914d\u51c6\uff09", None))
        self.lbl_feature.setText(QCoreApplication.translate("AdvancePanel", u"\u7279\u5f81\u7b97\u6cd5", None))
#if QT_CONFIG(tooltip)
        self.combo_feature.setToolTip(QCoreApplication.translate("AdvancePanel", u"\u4f5c\u7528\uff1a\u51b3\u5b9a\u7528\u54ea\u79cd\u5c40\u90e8\u7279\u5f81\u505a\u5339\u914d\u3002\n"
"SIFT\uff1a\u6700\u7a33\uff0c\u901a\u7528\u9ed8\u8ba4\u3002\u9002\u5408\u7eb9\u7406\u4e30\u5bcc\u3001\u5149\u7167\u53d8\u5316\u7684\u573a\u666f\u3002\n"
"AKAZE\uff1a\u901f\u5ea6\u5feb\uff0c\u5bf9\u5f31\u7eb9\u7406/\u6a21\u7cca\u66f4\u53cb\u597d\uff0c\u9002\u5408\u684c\u9762\u7eaf\u8272\u7269\u4f53\u591a\u7684\u573a\u666f\u3002\n"
"ORB\uff1a\u6700\u5feb\u4f46\u6700\u5f31\uff0c\u53ea\u5728\u5176\u4ed6\u7b97\u6cd5\u592a\u6162\u65f6\u7528\u3002\n"
"\u9ed8\u8ba4 SIFT\uff1a\u7efc\u5408\u6700\u597d\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_ratio.setText(QCoreApplication.translate("AdvancePanel", u"Lowe \u6bd4\u503c", None))
#if QT_CONFIG(tooltip)
        self.spin_ratio.setToolTip(QCoreApplication.translate("AdvancePanel", u"\u4f5c\u7528\uff1a\u8fc7\u6ee4\u8bef\u5339\u914d\u3002\u4ec5\u4fdd\u7559\u300c\u6700\u8fd1\u90bb\u8ddd\u79bb < ratio \u00d7 \u6b21\u8fd1\u90bb\u8ddd\u79bb\u300d\u7684\u5339\u914d\u3002\n"
"\u8c03\u5927 (0.80~0.90)\uff1a\u5339\u914d\u66f4\u591a\u4f46\u8bef\u5339\u914d\u589e\u591a \u2192 \u9002\u5408\u7eb9\u7406\u5f31\u3001\u5339\u914d\u6570\u4e0d\u8db3\n"
"\u8c03\u5c0f (0.60~0.70)\uff1a\u5339\u914d\u66f4\u4e25\u4f46\u53ef\u80fd\u6f0f \u2192 \u9002\u5408\u7eb9\u7406\u4e30\u5bcc\u3001\u8bef\u5339\u914d\u591a\n"
"\u9ed8\u8ba4 0.72\uff1a\u901a\u7528\u5e73\u8861\u70b9\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_ransac.setText(QCoreApplication.translate("AdvancePanel", u"RANSAC \u9608\u503c", None))
#if QT_CONFIG(tooltip)
        self.spin_ransac.setToolTip(QCoreApplication.translate("AdvancePanel", u"\u4f5c\u7528\uff1aMAGSAC \u5224\u5b9a\u5185\u70b9\u7684\u50cf\u7d20\u8bef\u5dee\u4e0a\u9650\u3002\n"
"\u8c03\u5927 (5~10)\uff1a\u5bb9\u5fcd\u66f4\u5927\u51e0\u4f55\u8bef\u5dee\uff0c\u4f46\u53ef\u80fd\u628a\u9519\u8bef\u5339\u914d\u5f53\u5185\u70b9\u3002\n"
"\u8c03\u5c0f (1~2)\uff1a\u66f4\u4e25\u683c\uff0c\u53ea\u4fdd\u7559\u9ad8\u7cbe\u5ea6\u5339\u914d\uff0c\u53ef\u80fd\u5185\u70b9\u4e0d\u8db3\u3002\n"
"\u9ed8\u8ba4 3.0\uff1a\u50cf\u7d20\u7ea7\u901a\u7528\u7684\u7a33\u59a5\u503c\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.spin_ransac.setSuffix(QCoreApplication.translate("AdvancePanel", u" px", None))
        self.lbl_min_match.setText(QCoreApplication.translate("AdvancePanel", u"\u6700\u5c0f\u5339\u914d\u6570", None))
#if QT_CONFIG(tooltip)
        self.spin_min_match.setToolTip(QCoreApplication.translate("AdvancePanel", u"\u4f5c\u7528\uff1a\u5339\u914d\u6570\u4f4e\u4e8e\u6b64\u503c\u5224\u5b9a\u914d\u51c6\u5931\u8d25\u3002\n"
"\u8c03\u5927\uff1a\u66f4\u4fdd\u5b88\uff0c\u907f\u514d\u4e0d\u9760\u8c31\u7684\u914d\u51c6\uff0c\u4f46\u53ef\u80fd\u8bef\u62a5\u5931\u8d25\u3002\n"
"\u8c03\u5c0f\uff1a\u66f4\u5bbd\u677e\uff0c\u4f46\u4f4e\u8d28\u91cf\u914d\u51c6\u4e5f\u53ef\u80fd\u901a\u8fc7\u3002\n"
"\u9ed8\u8ba4 12\uff1a\u5e73\u9762\u573a\u666f\u4e0b\u7ecf\u9a8c\u503c\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_min_inlier.setText(QCoreApplication.translate("AdvancePanel", u"\u5185\u70b9\u7387\u4e0b\u9650", None))
#if QT_CONFIG(tooltip)
        self.spin_min_inlier.setToolTip(QCoreApplication.translate("AdvancePanel", u"\u4f5c\u7528\uff1aRANSAC \u5185\u70b9\u5360\u5168\u90e8\u5339\u914d\u7684\u6bd4\u4f8b\u4f4e\u4e8e\u6b64\u503c\uff0c\u5224\u5b9a\u5931\u8d25\u3002\n"
"\u8c03\u5927 (0.4~0.6)\uff1a\u975e\u5e38\u4e25\u683c\uff0c\u53ea\u63a5\u53d7\u9ad8\u8d28\u91cf\u914d\u51c6\u3002\n"
"\u8c03\u5c0f (0.1~0.2)\uff1a\u5bbd\u677e\uff0c\u9002\u5408\u6742\u4e71\u573a\u666f\u4f46\u53ef\u80fd\u8bef\u5224\u3002\n"
"\u9ed8\u8ba4 0.25\uff1a\u5e73\u8861\u70b9\u3002", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.chk_tps.setToolTip(QCoreApplication.translate("AdvancePanel", u"\u4f5c\u7528\uff1a\u5728\u5168\u5c40\u5355\u5e94\u57fa\u7840\u4e0a\u505a\u975e\u521a\u6027\u53d8\u5f62\uff0c\u5438\u6536\u5c40\u90e8\u89c6\u5dee\uff08\u5982\u684c\u9762\u4e0a\u7684\u7acb\u4f53\u7269\uff09\u3002\n"
"\u5f00\u542f\uff1a\u80fd\u5bf9\u9f50\u6709\u539a\u5ea6\u7684\u7269\u4f53\uff0c\u4f46\u8fb9\u7f18\u53ef\u80fd\u6709\u6b8b\u5f71\u3002\n"
"\u5173\u95ed\uff1a\u53ea\u7528\u5168\u5c40\u5355\u5e94\uff0c\u901f\u5ea6\u5feb\uff0c\u975e\u5e73\u9762\u533a\u57df\u4f1a\u6709\u91cd\u5f71\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.chk_tps.setText(QCoreApplication.translate("AdvancePanel", u"\u542f\u7528 TPS \u53d8\u5f62", None))
        self.lbl_tps_ctrl.setText(QCoreApplication.translate("AdvancePanel", u"\u63a7\u5236\u70b9\u4e0a\u9650", None))
#if QT_CONFIG(tooltip)
        self.spin_tps_ctrl.setToolTip(QCoreApplication.translate("AdvancePanel", u"\u4f5c\u7528\uff1a\u53c2\u4e0e\u62df\u5408 TPS \u7684\u63a7\u5236\u70b9\u6570\u91cf\u4e0a\u9650\u3002\n"
"\u8c03\u5927 (300~500)\uff1a\u53d8\u5f62\u66f4\u8d34\u5408\u5c40\u90e8\u7ec6\u8282\uff0c\u4f46\u66f4\u6162\u3001\u66f4\u6613\u8fc7\u62df\u5408\u566a\u58f0\u3002\n"
"\u8c03\u5c0f (50~100)\uff1a\u53d8\u5f62\u66f4\u5e73\u6ed1\uff0c\u4f46\u53ef\u80fd\u5438\u6536\u4e0d\u6389\u5c40\u90e8\u89c6\u5dee\u3002\n"
"\u9ed8\u8ba4 150\uff1a\u7ec6\u8282\u548c\u7a33\u5b9a\u6027\u5e73\u8861\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_tps_smooth.setText(QCoreApplication.translate("AdvancePanel", u"\u5e73\u6ed1\u7cfb\u6570", None))
#if QT_CONFIG(tooltip)
        self.spin_tps_smooth.setToolTip(QCoreApplication.translate("AdvancePanel", u"\u4f5c\u7528\uff1aTPS \u62df\u5408\u65f6\u5bf9\u63a7\u5236\u70b9\u7684\u653e\u677e\u7a0b\u5ea6\u3002\n"
"0\uff1a\u4e25\u683c\u7a7f\u8fc7\u6240\u6709\u63a7\u5236\u70b9\uff08\u6613\u53d7\u566a\u58f0\u5f71\u54cd\uff0c\u4ea7\u751f\u6ce2\u7eb9\uff09\u3002\n"
"0.1~1\uff1a\u5141\u8bb8\u5c0f\u5e45\u504f\u79bb\uff08\u63a8\u8350\uff09\u3002\n"
">5\uff1a\u53d8\u5f62\u975e\u5e38\u5e73\u6ed1\uff0c\u51e0\u4e4e\u9000\u5316\u4e3a\u5168\u5c40\u5f62\u53d8\u3002\n"
"\u9ed8\u8ba4 0.10\uff1a\u8f7b\u5fae\u6297\u566a\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_tps_step.setText(QCoreApplication.translate("AdvancePanel", u"\u6c42\u503c\u6b65\u957f", None))
#if QT_CONFIG(tooltip)
        self.spin_tps_step.setToolTip(QCoreApplication.translate("AdvancePanel", u"\u4f5c\u7528\uff1aTPS \u5728\u7c97\u7f51\u683c\u4e0a\u6c42\u503c\u518d\u4e0a\u91c7\u6837\uff0c\u63a7\u5236\u8ba1\u7b97\u7cbe\u5ea6/\u901f\u5ea6\u3002\n"
"\u8c03\u5c0f (4~8)\uff1a\u66f4\u7cbe\u786e\uff0c\u4f46\u66f4\u6162\u3002\n"
"\u8c03\u5927 (32~64)\uff1a\u66f4\u5feb\uff0c\u4f46\u53ef\u80fd\u635f\u5931\u7ec6\u8282\u3002\n"
"\u9ed8\u8ba4 16\uff1a\u901f\u5ea6\u4e0e\u7cbe\u5ea6\u5e73\u8861\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.spin_tps_step.setSuffix(QCoreApplication.translate("AdvancePanel", u" px", None))
        self.lbl_grp_tps.setText(QCoreApplication.translate("AdvancePanel", u"TPS \u975e\u521a\u6027\uff08\u7cbe\u914d\u51c6\uff09", None))
        self.lbl_grp_photo.setText(QCoreApplication.translate("AdvancePanel", u"\u5149\u5ea6\u5f52\u4e00\u5316", None))
        self.lbl_photo_method.setText(QCoreApplication.translate("AdvancePanel", u"\u65b9\u6cd5", None))
#if QT_CONFIG(tooltip)
        self.combo_photo_method.setToolTip(QCoreApplication.translate("AdvancePanel", u"\u4f5c\u7528\uff1a\u6d88\u9664\u4e24\u56fe\u66dd\u5149/\u8272\u5f69\u5dee\u5f02\u3002\n"
"linear\uff1a\u9010\u901a\u9053\u7ebf\u6027\u62df\u5408 B\u2248kA+t\u3002\u7b80\u5355\u5feb\u901f\uff0c\u9002\u5408\u6574\u4f53\u4eae\u5ea6\u548c\u589e\u76ca\u5dee\u5f02\u3002\n"
"reinhard\uff1aLab \u7a7a\u95f4\u5747\u503c/\u6807\u51c6\u5dee\u8fc1\u79fb\u3002\u9002\u5408\u8272\u5f69\u504f\u79fb\u660e\u663e\u65f6\uff0c\u6548\u679c\u66f4\u81ea\u7136\u3002\n"
"hist_match\uff1a\u76f4\u65b9\u56fe\u5339\u914d\u3002\u5bf9\u6574\u4f53\u8272\u8c03\u6700\u5f7b\u5e95\uff0c\u4f46\u53ef\u80fd\u6539\u53d8\u5c40\u90e8\u5bf9\u6bd4\u5ea6\u3002\n"
"\u9ed8\u8ba4 linear\uff1a\u5148\u8bd5\u6700\u7b80\u5355\uff0c\u4e0d\u591f\u518d\u5347\u7ea7\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_grp_diff.setText(QCoreApplication.translate("AdvancePanel", u"\u53d8\u5316\u68c0\u6d4b", None))
        self.lbl_lab_thresh.setText(QCoreApplication.translate("AdvancePanel", u"Lab \u8ddd\u79bb\u9608\u503c", None))
#if QT_CONFIG(tooltip)
        self.spin_lab_thresh.setToolTip(QCoreApplication.translate("AdvancePanel", u"\u4f5c\u7528\uff1a\u5224\u5b9a\u300c\u4eae\u5ea6/\u989c\u8272\u53d1\u751f\u663e\u8457\u53d8\u5316\u300d\u7684\u9608\u503c\u3002\n"
"\u8c03\u5927 (35~60)\uff1a\u53ea\u6807\u8bb0\u660e\u663e\u53d8\u5316\uff0c\u51cf\u5c11\u8bef\u62a5\u3002\n"
"\u8c03\u5c0f (10~20)\uff1a\u66f4\u654f\u611f\uff0c\u53ef\u80fd\u628a\u5149\u7167\u6ce2\u52a8\u8bef\u5224\u4e3a\u53d8\u5316\u3002\n"
"\u9ed8\u8ba4 25\uff1a\u4e2d\u7b49\u654f\u611f\u5ea6\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_ssim_thresh.setText(QCoreApplication.translate("AdvancePanel", u"SSIM \u9608\u503c", None))
#if QT_CONFIG(tooltip)
        self.spin_ssim_thresh.setToolTip(QCoreApplication.translate("AdvancePanel", u"\u4f5c\u7528\uff1aSSIM \u4f4e\u4e8e\u6b64\u503c\u5224\u5b9a\u300c\u5c40\u90e8\u7ed3\u6784\u53d1\u751f\u53d8\u5316\u300d\uff08\u7eb9\u7406\u4fee\u6539\uff09\u3002\n"
"\u8c03\u5927 (0.75~0.9)\uff1a\u975e\u5e38\u654f\u611f\uff0c\u8f7b\u5fae\u9519\u4f4d\u4e5f\u4f1a\u88ab\u6807\u4e3a\u7eb9\u7406\u53d8\u5316\u3002\n"
"\u8c03\u5c0f (0.4~0.5)\uff1a\u53ea\u6807\u8bb0\u7ed3\u6784\u5927\u5e45\u53d8\u5316\u3002\n"
"\u9ed8\u8ba4 0.60\uff1a\u5e73\u8861\u70b9\u3002\u914d\u51c6\u4e0d\u591f\u51c6\u65f6\u5efa\u8bae\u8c03\u5927\u4ee5\u6355\u6349\u66f4\u591a\u7eb9\u7406\u5dee\u5f02\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_min_area.setText(QCoreApplication.translate("AdvancePanel", u"\u6700\u5c0f\u53d8\u5316\u9762\u79ef", None))
#if QT_CONFIG(tooltip)
        self.spin_min_area.setToolTip(QCoreApplication.translate("AdvancePanel", u"\u4f5c\u7528\uff1a\u53d8\u5316\u533a\u57df\u50cf\u7d20\u9762\u79ef\u4f4e\u4e8e\u6b64\u503c\u4f1a\u88ab\u4e22\u5f03\uff08\u8fc7\u6ee4\u566a\u58f0\uff09\u3002\n"
"\u8c03\u5927 (200~1000)\uff1a\u53ea\u4fdd\u7559\u5927\u5757\u53d8\u5316\uff0c\u753b\u9762\u5e72\u51c0\u4f46\u53ef\u80fd\u6f0f\u5c0f\u7269\u4f53\u3002\n"
"\u8c03\u5c0f (10~50)\uff1a\u66f4\u654f\u611f\uff0c\u4f46\u4f1a\u6709\u5f88\u591a\u96f6\u788e\u8bef\u62a5\u3002\n"
"\u9ed8\u8ba4 80\uff1a\u684c\u9762\u573a\u666f\u5e73\u8861\u503c\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.spin_min_area.setSuffix(QCoreApplication.translate("AdvancePanel", u" px", None))
        self.lbl_morph.setText(QCoreApplication.translate("AdvancePanel", u"\u5f62\u6001\u5b66\u6838", None))
#if QT_CONFIG(tooltip)
        self.spin_morph.setToolTip(QCoreApplication.translate("AdvancePanel", u"\u4f5c\u7528\uff1a\u53d8\u5316 mask \u505a\u5f00/\u95ed\u8fd0\u7b97\u7684\u6838\u5927\u5c0f\uff0c\u7528\u4e8e\u53bb\u5c0f\u566a\u70b9\u3001\u8fde\u63a5\u788e\u7247\u3002\n"
"\u8c03\u5927 (7~15)\uff1a\u66f4\u5f3a\u53bb\u566a\uff0c\u4f46\u4f1a\u5403\u6389\u7ec6\u5c0f\u53d8\u5316\u3002\n"
"\u8c03\u5c0f (1~3)\uff1a\u4fdd\u7559\u7ec6\u8282\uff0c\u4f46\u53ef\u80fd\u6b8b\u7559\u566a\u70b9\u3002\n"
"\u9ed8\u8ba4 3\uff1a\u8f7b\u5ea6\u6e05\u7406\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.spin_morph.setSuffix(QCoreApplication.translate("AdvancePanel", u" px", None))
    # retranslateUi

