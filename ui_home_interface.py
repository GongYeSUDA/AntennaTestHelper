# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'home_interface.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QFrame,
    QHBoxLayout, QHeaderView, QSizePolicy, QSpacerItem,
    QTableWidgetItem, QVBoxLayout, QWidget)

from qfluentwidgets import (CardWidget, LineEdit, PrimaryPushButton, SubtitleLabel,
    TableWidget)

class Ui_HomeInterface(object):
    def setupUi(self, HomeInterface):
        if not HomeInterface.objectName():
            HomeInterface.setObjectName(u"HomeInterface")
        HomeInterface.resize(900, 700)
        HomeInterface.setStyleSheet(u"#HomeInterface {\n"
"    background-color: transparent;\n"
"}\n"
"#titleLabel {\n"
"    margin-top: 10px;\n"
"	margin-bottom: 10px;\n"
"}")
        self.verticalLayout = QVBoxLayout(HomeInterface)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.titleLabel = SubtitleLabel(HomeInterface)
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

        self.fileCard = CardWidget(HomeInterface)
        self.fileCard.setObjectName(u"fileCard")
        self.fileCard.setMinimumSize(QSize(0, 0))
        self.fileCard.setFrameShape(QFrame.Shape.StyledPanel)
        self.fileCard.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.fileCard)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.filePathLineEdit = LineEdit(self.fileCard)
        self.filePathLineEdit.setObjectName(u"filePathLineEdit")
        self.filePathLineEdit.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.filePathLineEdit)

        self.openFileButton = PrimaryPushButton(self.fileCard)
        self.openFileButton.setObjectName(u"openFileButton")

        self.horizontalLayout_2.addWidget(self.openFileButton)


        self.verticalLayout.addWidget(self.fileCard)

        self.infoTable = TableWidget(HomeInterface)
        if (self.infoTable.columnCount() < 2):
            self.infoTable.setColumnCount(2)
        self.infoTable.setObjectName(u"infoTable")
        self.infoTable.setMinimumSize(QSize(200, 0))
        self.infoTable.setMidLineWidth(0)
        self.infoTable.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.infoTable.setAutoScroll(True)
        self.infoTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.infoTable.setAlternatingRowColors(True)
        self.infoTable.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.infoTable.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.infoTable.setColumnCount(2)
        self.infoTable.horizontalHeader().setMinimumSectionSize(10)
        self.infoTable.horizontalHeader().setDefaultSectionSize(200)
        self.infoTable.horizontalHeader().setStretchLastSection(True)
        self.infoTable.verticalHeader().setVisible(False)

        self.verticalLayout.addWidget(self.infoTable)

        self.verticalSpacer_2 = QSpacerItem(20, 100, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)

        self.verticalLayout.addItem(self.verticalSpacer_2)


        self.retranslateUi(HomeInterface)

        QMetaObject.connectSlotsByName(HomeInterface)
    # setupUi

    def retranslateUi(self, HomeInterface):
        HomeInterface.setWindowTitle(QCoreApplication.translate("HomeInterface", u"Form", None))
        self.titleLabel.setText(QCoreApplication.translate("HomeInterface", u"\u6570\u636e\u5bfc\u5165", None))
        self.filePathLineEdit.setPlaceholderText(QCoreApplication.translate("HomeInterface", u"\u6587\u4ef6\u8def\u5f84", None))
        self.openFileButton.setText(QCoreApplication.translate("HomeInterface", u"\u6d4f\u89c8\u6587\u4ef6", None))
    # retranslateUi

