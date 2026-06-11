# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analysis_gain_interface.ui'
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

class Ui_AnalysisGainInterface(object):
    def setupUi(self, AnalysisGainInterface):
        if not AnalysisGainInterface.objectName():
            AnalysisGainInterface.setObjectName(u"AnalysisGainInterface")
        AnalysisGainInterface.resize(900, 700)
        AnalysisGainInterface.setStyleSheet(u"#HomeInterface {\n"
"    background-color: transparent;\n"
"}\n"
"#titleLabel {\n"
"    margin-top: 10px;\n"
"	margin-bottom: 10px;\n"
"}")
        self.verticalLayout = QVBoxLayout(AnalysisGainInterface)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.titleLabel = SubtitleLabel(AnalysisGainInterface)
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

        self.controlCard = CardWidget(AnalysisGainInterface)
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
        self.checkBoxMax = CheckBox(self.controlCard)
        self.checkBoxMax.setObjectName(u"checkBoxMax")

        self.horizontalLayout_2.addWidget(self.checkBoxMax)

        self.phiLable = BodyLabel(self.controlCard)
        self.phiLable.setObjectName(u"phiLable")
        self.phiLable.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout_2.addWidget(self.phiLable)

        self.phiComboBox = ComboBox(self.controlCard)
        self.phiComboBox.setObjectName(u"phiComboBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.phiComboBox.sizePolicy().hasHeightForWidth())
        self.phiComboBox.setSizePolicy(sizePolicy1)
        self.phiComboBox.setMaximumSize(QSize(200, 16777215))

        self.horizontalLayout_2.addWidget(self.phiComboBox)

        self.horizontalSpacer = QSpacerItem(151, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.thetaLable = BodyLabel(self.controlCard)
        self.thetaLable.setObjectName(u"thetaLable")
        self.thetaLable.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout_2.addWidget(self.thetaLable)

        self.thetaComboBox = ComboBox(self.controlCard)
        self.thetaComboBox.setObjectName(u"thetaComboBox")
        sizePolicy1.setHeightForWidth(self.thetaComboBox.sizePolicy().hasHeightForWidth())
        self.thetaComboBox.setSizePolicy(sizePolicy1)
        self.thetaComboBox.setMaximumSize(QSize(200, 16777215))

        self.horizontalLayout_2.addWidget(self.thetaComboBox)

        self.horizontalSpacer_2 = QSpacerItem(151, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.plotButton = PrimaryPushButton(self.controlCard)
        self.plotButton.setObjectName(u"plotButton")
        sizePolicy1.setHeightForWidth(self.plotButton.sizePolicy().hasHeightForWidth())
        self.plotButton.setSizePolicy(sizePolicy1)
        self.plotButton.setMaximumSize(QSize(200, 16777215))

        self.horizontalLayout_2.addWidget(self.plotButton)

        self.csvButton = PrimaryPushButton(self.controlCard)
        self.csvButton.setObjectName(u"csvButton")
        sizePolicy1.setHeightForWidth(self.csvButton.sizePolicy().hasHeightForWidth())
        self.csvButton.setSizePolicy(sizePolicy1)
        self.csvButton.setMaximumSize(QSize(200, 16777215))

        self.horizontalLayout_2.addWidget(self.csvButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

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


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addWidget(self.controlCard)

        self.chartContainer = QWidget(AnalysisGainInterface)
        self.chartContainer.setObjectName(u"chartContainer")

        self.verticalLayout.addWidget(self.chartContainer)

        self.verticalSpacer_2 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)

        self.verticalLayout.addItem(self.verticalSpacer_2)


        self.retranslateUi(AnalysisGainInterface)

        QMetaObject.connectSlotsByName(AnalysisGainInterface)
    # setupUi

    def retranslateUi(self, AnalysisGainInterface):
        AnalysisGainInterface.setWindowTitle(QCoreApplication.translate("AnalysisGainInterface", u"Form", None))
        self.titleLabel.setText(QCoreApplication.translate("AnalysisGainInterface", u"\u589e\u76ca - \u9891\u7387\u56fe", None))
        self.checkBoxMax.setText(QCoreApplication.translate("AnalysisGainInterface", u"Max", None))
        self.phiLable.setText(QCoreApplication.translate("AnalysisGainInterface", u"Phi:", None))
        self.thetaLable.setText(QCoreApplication.translate("AnalysisGainInterface", u"Theta:", None))
        self.plotButton.setText(QCoreApplication.translate("AnalysisGainInterface", u"\u7ed8\u5236\u56fe\u8868", None))
        self.csvButton.setText(QCoreApplication.translate("AnalysisGainInterface", u"\u5bfc\u51faCSV", None))
        self.checkBoxHori.setText(QCoreApplication.translate("AnalysisGainInterface", u"RealizedGainHorizontal", None))
        self.checkBoxVert.setText(QCoreApplication.translate("AnalysisGainInterface", u"RealizedGainVertical", None))
        self.checkBoxTotal.setText(QCoreApplication.translate("AnalysisGainInterface", u"RealizedGainTotal", None))
    # retranslateUi

