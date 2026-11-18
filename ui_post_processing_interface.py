# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'post_processing_interface.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

from qfluentwidgets import (CardWidget, CheckBox, LineEdit, PrimaryPushButton,
    SubtitleLabel)

class Ui_PostProcessingInterface(object):
    def setupUi(self, PostProcessingInterface):
        if not PostProcessingInterface.objectName():
            PostProcessingInterface.setObjectName(u"PostProcessingInterface")
        PostProcessingInterface.resize(900, 700)
        PostProcessingInterface.setStyleSheet(u"#HomeInterface {\n"
"    background-color: transparent;\n"
"}\n"
"#titleLabel {\n"
"    margin-top: 10px;\n"
"	margin-bottom: 10px;\n"
"}")
        self.verticalLayout = QVBoxLayout(PostProcessingInterface)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.titleLabel = SubtitleLabel(PostProcessingInterface)
        self.titleLabel.setObjectName(u"titleLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titleLabel.sizePolicy().hasHeightForWidth())
        self.titleLabel.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(20)
        self.titleLabel.setFont(font)

        self.verticalLayout.addWidget(self.titleLabel)

        self.controlCard = CardWidget(PostProcessingInterface)
        self.controlCard.setObjectName(u"controlCard")
        sizePolicy.setHeightForWidth(self.controlCard.sizePolicy().hasHeightForWidth())
        self.controlCard.setSizePolicy(sizePolicy)
        self.controlCard.setMinimumSize(QSize(0, 0))
        self.controlCard.setFrameShape(QFrame.Shape.StyledPanel)
        self.controlCard.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.controlCard)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.checkBoxNoS1P = CheckBox(self.controlCard)
        self.checkBoxNoS1P.setObjectName(u"checkBoxNoS1P")

        self.horizontalLayout_2.addWidget(self.checkBoxNoS1P)

        self.S1PPathLineEdit = LineEdit(self.controlCard)
        self.S1PPathLineEdit.setObjectName(u"S1PPathLineEdit")
        self.S1PPathLineEdit.setReadOnly(False)

        self.horizontalLayout_2.addWidget(self.S1PPathLineEdit)

        self.openS1PButton = PrimaryPushButton(self.controlCard)
        self.openS1PButton.setObjectName(u"openS1PButton")

        self.horizontalLayout_2.addWidget(self.openS1PButton)

        self.plotButton = PrimaryPushButton(self.controlCard)
        self.plotButton.setObjectName(u"plotButton")
        self.plotButton.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_2.addWidget(self.plotButton)

        self.csvButton = PrimaryPushButton(self.controlCard)
        self.csvButton.setObjectName(u"csvButton")
        self.csvButton.setMaximumSize(QSize(200, 16777215))

        self.horizontalLayout_2.addWidget(self.csvButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.checkBoxGain = CheckBox(self.controlCard)
        self.checkBoxGain.setObjectName(u"checkBoxGain")

        self.horizontalLayout_3.addWidget(self.checkBoxGain)

        self.checkBoxDirectivity = CheckBox(self.controlCard)
        self.checkBoxDirectivity.setObjectName(u"checkBoxDirectivity")

        self.horizontalLayout_3.addWidget(self.checkBoxDirectivity)

        self.checkBoxEffeciency = CheckBox(self.controlCard)
        self.checkBoxEffeciency.setObjectName(u"checkBoxEffeciency")

        self.horizontalLayout_3.addWidget(self.checkBoxEffeciency)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addWidget(self.controlCard)

        self.chartContainer = QWidget(PostProcessingInterface)
        self.chartContainer.setObjectName(u"chartContainer")

        self.verticalLayout.addWidget(self.chartContainer)

        self.verticalSpacer_2 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)

        self.verticalLayout.addItem(self.verticalSpacer_2)


        self.retranslateUi(PostProcessingInterface)

        QMetaObject.connectSlotsByName(PostProcessingInterface)
    # setupUi

    def retranslateUi(self, PostProcessingInterface):
        PostProcessingInterface.setWindowTitle(QCoreApplication.translate("PostProcessingInterface", u"Form", None))
        self.titleLabel.setText(QCoreApplication.translate("PostProcessingInterface", u"\u540e\u5904\u7406", None))
        self.checkBoxNoS1P.setText(QCoreApplication.translate("PostProcessingInterface", u"\u89c6RealizedGain\u4e3aGain", None))
        self.S1PPathLineEdit.setPlaceholderText(QCoreApplication.translate("PostProcessingInterface", u"S1P\u6587\u4ef6\u8def\u5f84", None))
        self.openS1PButton.setText(QCoreApplication.translate("PostProcessingInterface", u"\u6d4f\u89c8\u6587\u4ef6", None))
        self.plotButton.setText(QCoreApplication.translate("PostProcessingInterface", u"\u7ed8\u5236\u56fe\u8868", None))
        self.csvButton.setText(QCoreApplication.translate("PostProcessingInterface", u"\u5bfc\u51faCSV", None))
        self.checkBoxGain.setText(QCoreApplication.translate("PostProcessingInterface", u"MaxGain", None))
        self.checkBoxDirectivity.setText(QCoreApplication.translate("PostProcessingInterface", u"MaxDirectivity", None))
        self.checkBoxEffeciency.setText(QCoreApplication.translate("PostProcessingInterface", u"Efficiency", None))
    # retranslateUi


