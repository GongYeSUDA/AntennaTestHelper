# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analysis_pattern_interface.ui'
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
    ImageLabel, PrimaryPushButton, SubtitleLabel)

class Ui_AnalysisPatternInterface(object):
    def setupUi(self, AnalysisPatternInterface):
        if not AnalysisPatternInterface.objectName():
            AnalysisPatternInterface.setObjectName(u"AnalysisPatternInterface")
        AnalysisPatternInterface.resize(900, 700)
        AnalysisPatternInterface.setStyleSheet(u"#HomeInterface {\n"
"    background-color: transparent;\n"
"}\n"
"#titleLabel {\n"
"    margin-top: 10px;\n"
"	margin-bottom: 10px;\n"
"}")
        self.verticalLayout = QVBoxLayout(AnalysisPatternInterface)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.titleLabel = SubtitleLabel(AnalysisPatternInterface)
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

        self.controlCard = CardWidget(AnalysisPatternInterface)
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

        self.horizontalSpacer = QSpacerItem(151, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.planeLable = BodyLabel(self.controlCard)
        self.planeLable.setObjectName(u"planeLable")
        self.planeLable.setMaximumSize(QSize(200, 16777215))

        self.horizontalLayout_2.addWidget(self.planeLable)

        self.planeComboBox = ComboBox(self.controlCard)
        self.planeComboBox.setObjectName(u"planeComboBox")
        sizePolicy1.setHeightForWidth(self.planeComboBox.sizePolicy().hasHeightForWidth())
        self.planeComboBox.setSizePolicy(sizePolicy1)
        self.planeComboBox.setMaximumSize(QSize(200, 16777215))

        self.horizontalLayout_2.addWidget(self.planeComboBox)

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

        self.schematicLabel = ImageLabel(self.controlCard)
        self.schematicLabel.setObjectName(u"schematicLabel")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.schematicLabel.sizePolicy().hasHeightForWidth())
        self.schematicLabel.setSizePolicy(sizePolicy2)
        self.schematicLabel.setMinimumSize(QSize(150, 150))
        self.schematicLabel.setMaximumSize(QSize(300, 300))
        self.schematicLabel.setFrameShape(QFrame.Shape.StyledPanel)
        self.schematicLabel.setScaledContents(True)
        self.schematicLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.schematicLabel)


        self.verticalLayout.addWidget(self.controlCard)

        self.chartContainer = QWidget(AnalysisPatternInterface)
        self.chartContainer.setObjectName(u"chartContainer")
        self.chartContainer.setMinimumSize(QSize(0, 200))

        self.verticalLayout.addWidget(self.chartContainer)

        self.verticalSpacer_2 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)

        self.verticalLayout.addItem(self.verticalSpacer_2)


        self.retranslateUi(AnalysisPatternInterface)

        QMetaObject.connectSlotsByName(AnalysisPatternInterface)
    # setupUi

    def retranslateUi(self, AnalysisPatternInterface):
        AnalysisPatternInterface.setWindowTitle(QCoreApplication.translate("AnalysisPatternInterface", u"Form", None))
        self.titleLabel.setText(QCoreApplication.translate("AnalysisPatternInterface", u"2D\u65b9\u5411\u56fe", None))
        self.freqLable.setText(QCoreApplication.translate("AnalysisPatternInterface", u"\u9891\u7387 (MHz):", None))
        self.planeLable.setText(QCoreApplication.translate("AnalysisPatternInterface", u"\u56fa\u5b9a\u5e73\u9762:", None))
        self.plotButton.setText(QCoreApplication.translate("AnalysisPatternInterface", u"\u7ed8\u5236\u56fe\u8868", None))
        self.csvButton.setText(QCoreApplication.translate("AnalysisPatternInterface", u"\u5bfc\u51faCSV", None))
        self.checkBoxHori.setText(QCoreApplication.translate("AnalysisPatternInterface", u"RealizedGainHorizontal", None))
        self.checkBoxVert.setText(QCoreApplication.translate("AnalysisPatternInterface", u"RealizedGainVertical", None))
        self.checkBoxTotal.setText(QCoreApplication.translate("AnalysisPatternInterface", u"RealizedGainTotal", None))
        self.schematicLabel.setText(QCoreApplication.translate("AnalysisPatternInterface", u"TextLabel", None))
    # retranslateUi

