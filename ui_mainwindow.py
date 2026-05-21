# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QMainWindow, QSizePolicy,
    QWidget)

from qfluentwidgets import (NavigationBar, PopUpAniStackedWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(210, 498)
        MainWindow.setStyleSheet(u"font-family: 12pt \"\u5fae\u8f6f\u96c5\u9ed1\";")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(0, 0, 211, 481))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.navigationbar = NavigationBar(self.horizontalLayoutWidget)
        self.navigationbar.setObjectName(u"navigationbar")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.navigationbar.sizePolicy().hasHeightForWidth())
        self.navigationbar.setSizePolicy(sizePolicy)
        self.navigationbar.setMinimumSize(QSize(100, 0))

        self.horizontalLayout.addWidget(self.navigationbar)

        self.popupanistackedwidget = PopUpAniStackedWidget(self.horizontalLayoutWidget)
        self.popupanistackedwidget.setObjectName(u"popupanistackedwidget")
        self.popupanistackedwidget.setMinimumSize(QSize(0, 0))
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.popupanistackedwidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.popupanistackedwidget.addWidget(self.page_2)

        self.horizontalLayout.addWidget(self.popupanistackedwidget)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
    # retranslateUi

