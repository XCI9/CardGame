# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
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
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGroupBox, QHBoxLayout,
    QLabel, QListView, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1020, 509)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.canva = QGraphicsView(self.centralwidget)
        self.canva.setObjectName(u"canva")
        self.canva.setGeometry(QRect(10, 10, 791, 441))
        self.canva.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.canva.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cardChooser = QListView(self.centralwidget)
        self.cardChooser.setObjectName(u"cardChooser")
        self.cardChooser.setGeometry(QRect(810, 100, 201, 311))
        self.cardChooser.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.cardChooser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cardChooser.setBatchSize(100)
        self.cannot_play_msg = QLabel(self.centralwidget)
        self.cannot_play_msg.setObjectName(u"cannot_play_msg")
        self.cannot_play_msg.setGeometry(QRect(860, 420, 111, 16))
        self.cannot_play_msg.setStyleSheet(u"QLabel{color:#f00}")
        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(808, 440, 201, 41))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pass_ = QPushButton(self.horizontalLayoutWidget)
        self.pass_.setObjectName(u"pass_")
        self.pass_.setEnabled(False)
        self.pass_.setCheckable(False)

        self.horizontalLayout.addWidget(self.pass_)

        self.submit = QPushButton(self.horizontalLayoutWidget)
        self.submit.setObjectName(u"submit")
        self.submit.setEnabled(False)
        self.submit.setCheckable(False)

        self.horizontalLayout.addWidget(self.submit)

        self.eliminate = QPushButton(self.horizontalLayoutWidget)
        self.eliminate.setObjectName(u"eliminate")

        self.horizontalLayout.addWidget(self.eliminate)

        self.rule19 = QLabel(self.centralwidget)
        self.rule19.setObjectName(u"rule19")
        self.rule19.setGeometry(QRect(140, 460, 41, 16))
        self.rule19.setStyleSheet(u"QLabel{color:#f00}")
        self.rule29 = QLabel(self.centralwidget)
        self.rule29.setObjectName(u"rule29")
        self.rule29.setGeometry(QRect(80, 460, 41, 16))
        self.rule29.setStyleSheet(u"QLabel{color:#f00}")
        self.rule9 = QLabel(self.centralwidget)
        self.rule9.setObjectName(u"rule9")
        self.rule9.setGeometry(QRect(20, 460, 41, 16))
        self.rule9.setStyleSheet(u"QLabel{color:#f00}")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(810, 10, 201, 81))
        self.horizontalLayoutWidget_2 = QWidget(self.groupBox)
        self.horizontalLayoutWidget_2.setObjectName(u"horizontalLayoutWidget_2")
        self.horizontalLayoutWidget_2.setGeometry(QRect(0, 20, 201, 61))
        self.prev_hand = QHBoxLayout(self.horizontalLayoutWidget_2)
        self.prev_hand.setObjectName(u"prev_hand")
        self.prev_hand.setContentsMargins(0, 0, 0, 0)
        self.turn_player_name = QLabel(self.centralwidget)
        self.turn_player_name.setObjectName(u"turn_player_name")
        self.turn_player_name.setGeometry(QRect(660, 460, 141, 21))
        font = QFont()
        font.setPointSize(12)
        self.turn_player_name.setFont(font)
        self.turn_player_name.setStyleSheet(u"")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1020, 22))
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.cannot_play_msg.setText(QCoreApplication.translate("MainWindow", u"\u8acb\u5148\u9078\u8981\u6253\u51fa\u7684\u724c!", None))
        self.pass_.setText(QCoreApplication.translate("MainWindow", u"Pass", None))
        self.submit.setText(QCoreApplication.translate("MainWindow", u"\u6253\u51fa", None))
        self.eliminate.setText(QCoreApplication.translate("MainWindow", u"\u6d88\u9664", None))
        self.rule19.setText(QCoreApplication.translate("MainWindow", u"3\u58d31\u2718", None))
        self.rule29.setText(QCoreApplication.translate("MainWindow", u"3\u58d32\u2718", None))
        self.rule9.setText(QCoreApplication.translate("MainWindow", u"2\u58d31\u2718", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u4e0a\u5bb6", None))
        self.turn_player_name.setText(QCoreApplication.translate("MainWindow", u"\u76ee\u524d\u8f2a\u5230: Player A", None))
    # retranslateUi

