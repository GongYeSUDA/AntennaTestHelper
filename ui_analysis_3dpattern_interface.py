# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analysis_3dpattern_interface.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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

from qfluentwidgets import (BodyLabel, CardWidget, CheckBox, ComboBox,
    PrimaryPushButton, SubtitleLabel)

class Ui_Analysis3DPatternInterface(object):
    def setupUi(self, Analysis3DPatternInterface):
        if not Analysis3DPatternInterface.objectName():
            Analysis3DPatternInterface.setObjectName(u"Analysis3DPatternInterface")
        Analysis3DPatternInterface.resize(900, 700)
        Analysis3DPatternInterface.setStyleSheet(u"#HomeInterface {\n"
"    background-color: transparent;\n"
"}\n"
"#titleLabel {\n"
"    margin-top: 10px;\n"
"	margin-bottom: 10px;\n"
"}")
        self.verticalLayout = QVBoxLayout(Analysis3DPatternInterface)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.titleLabel = SubtitleLabel(Analysis3DPatternInterface)
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

        self.controlCard = CardWidget(Analysis3DPatternInterface)
        self.controlCard.setObjectName(u"controlCard")
        sizePolicy.setHeightForWidth(self.controlCard.sizePolicy().hasHeightForWidth())
        self.controlCard.setSizePolicy(sizePolicy)
        self.controlCard.setMinimumSize(QSize(0, 0))
        self.controlCard.setFrameShape(QFrame.Shape.StyledPanel)
        self.controlCard.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.controlCard)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.freqLable = BodyLabel(self.controlCard)
        self.freqLable.setObjectName(u"freqLable")
        self.freqLable.setMaximumSize(QSize(200, 16777215))

        self.horizontalLayout_2.addWidget(self.freqLable)

        self.freqComboBox = ComboBox(self.controlCard)
        self.freqComboBox.setObjectName(u"freqComboBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.freqComboBox.sizePolicy().hasHeightForWidth())
        self.freqComboBox.setSizePolicy(sizePolicy1)
        self.freqComboBox.setMaximumSize(QSize(200, 16777215))

        self.horizontalLayout_2.addWidget(self.freqComboBox)

        self.horizontalSpacer_2 = QSpacerItem(1, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.plotButton = PrimaryPushButton(self.controlCard)
        self.plotButton.setObjectName(u"plotButton")
        sizePolicy1.setHeightForWidth(self.plotButton.sizePolicy().hasHeightForWidth())
        self.plotButton.setSizePolicy(sizePolicy1)
        self.plotButton.setMaximumSize(QSize(200, 16777215))

        self.horizontalLayout_2.addWidget(self.plotButton)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.checkBoxHori = CheckBox(self.controlCard)
        self.checkBoxHori.setObjectName(u"checkBoxHori")

        self.horizontalLayout_3.addWidget(self.checkBoxHori)

        self.checkBoxVert = CheckBox(self.controlCard)
        self.checkBoxVert.setObjectName(u"checkBoxVert")

        self.horizontalLayout_3.addWidget(self.checkBoxVert)

        self.checkBoxTotal = CheckBox(self.controlCard)
        self.checkBoxTotal.setObjectName(u"checkBoxTotal")

        self.horizontalLayout_3.addWidget(self.checkBoxTotal)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)


        self.horizontalLayout.addLayout(self.verticalLayout_3)


        self.verticalLayout.addWidget(self.controlCard)

        self.chartContainer = QWidget(Analysis3DPatternInterface)
        self.chartContainer.setObjectName(u"chartContainer")
        self.chartContainer.setMinimumSize(QSize(0, 200))

        self.verticalLayout.addWidget(self.chartContainer)

        self.verticalSpacer_2 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)

        self.verticalLayout.addItem(self.verticalSpacer_2)


        self.retranslateUi(Analysis3DPatternInterface)

        QMetaObject.connectSlotsByName(Analysis3DPatternInterface)
    # setupUi

    def retranslateUi(self, Analysis3DPatternInterface):
        Analysis3DPatternInterface.setWindowTitle(QCoreApplication.translate("Analysis3DPatternInterface", u"Form", None))
        self.titleLabel.setText(QCoreApplication.translate("Analysis3DPatternInterface", u"3D\u65b9\u5411\u56fe", None))
        self.freqLable.setText(QCoreApplication.translate("Analysis3DPatternInterface", u"\u9891\u7387 (MHz):", None))
        self.plotButton.setText(QCoreApplication.translate("Analysis3DPatternInterface", u"\u7ed8\u5236\u56fe\u8868", None))
        self.checkBoxHori.setText(QCoreApplication.translate("Analysis3DPatternInterface", u"RealizedGainHorizontal", None))
        self.checkBoxVert.setText(QCoreApplication.translate("Analysis3DPatternInterface", u"RealizedGainVertical", None))
        self.checkBoxTotal.setText(QCoreApplication.translate("Analysis3DPatternInterface", u"RealizedGainTotal", None))
    # retranslateUi

