# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LauncherDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QLineEdit,
    QPushButton, QRadioButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(333, 131)
        self.submit = QPushButton(Dialog)
        self.submit.setObjectName(u"submit")
        self.submit.setGeometry(QRect(240, 100, 75, 24))
        self.server = QRadioButton(Dialog)
        self.server.setObjectName(u"server")
        self.server.setGeometry(QRect(20, 10, 61, 20))
        self.server.setChecked(True)
        self.port = QLineEdit(Dialog)
        self.port.setObjectName(u"port")
        self.port.setGeometry(QRect(250, 70, 61, 20))
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(210, 70, 31, 21))
        self.client = QRadioButton(Dialog)
        self.client.setObjectName(u"client")
        self.client.setGeometry(QRect(20, 40, 61, 20))
        self.ip = QLineEdit(Dialog)
        self.ip.setObjectName(u"ip")
        self.ip.setEnabled(False)
        self.ip.setGeometry(QRect(130, 40, 181, 20))
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(100, 40, 16, 21))
        self.name = QLineEdit(Dialog)
        self.name.setObjectName(u"name")
        self.name.setGeometry(QRect(70, 70, 111, 20))
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 70, 41, 21))
        self.information = QLabel(Dialog)
        self.information.setObjectName(u"information")
        self.information.setGeometry(QRect(20, 100, 211, 21))
        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(100, 10, 141, 21))
        self.player_count = QLineEdit(Dialog)
        self.player_count.setObjectName(u"player_count")
        self.player_count.setGeometry(QRect(150, 10, 71, 20))

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"\u7c64\u7b52\u555f\u52d5\u5668", None))
        self.submit.setText(QCoreApplication.translate("Dialog", u"OK", None))
        self.server.setText(QCoreApplication.translate("Dialog", u"server", None))
        self.port.setText(QCoreApplication.translate("Dialog", u"8888", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"port", None))
        self.client.setText(QCoreApplication.translate("Dialog", u"client", None))
        self.ip.setText(QCoreApplication.translate("Dialog", u"127.0.0.1", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"ip", None))
        self.name.setText(QCoreApplication.translate("Dialog", u"Player", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"name", None))
        self.information.setText(QCoreApplication.translate("Dialog", u"\u73a9\u5bb6:", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"\u904a\u73a9\u4eba\u6578                          \u4eba", None))
        self.player_count.setText(QCoreApplication.translate("Dialog", u"3", None))
    # retranslateUi

