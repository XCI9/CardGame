# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ServerClientDialog.ui'
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
        Dialog.resize(333, 105)
        self.submit = QPushButton(Dialog)
        self.submit.setObjectName(u"submit")
        self.submit.setGeometry(QRect(240, 70, 75, 24))
        self.server = QRadioButton(Dialog)
        self.server.setObjectName(u"server")
        self.server.setGeometry(QRect(20, 10, 61, 20))
        self.server.setChecked(True)
        self.port = QLineEdit(Dialog)
        self.port.setObjectName(u"port")
        self.port.setGeometry(QRect(250, 40, 61, 20))
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(210, 40, 31, 21))
        self.client = QRadioButton(Dialog)
        self.client.setObjectName(u"client")
        self.client.setGeometry(QRect(110, 10, 61, 20))
        self.ip = QLineEdit(Dialog)
        self.ip.setObjectName(u"ip")
        self.ip.setGeometry(QRect(210, 10, 101, 20))
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(180, 10, 16, 21))
        self.name = QLineEdit(Dialog)
        self.name.setObjectName(u"name")
        self.name.setGeometry(QRect(70, 40, 111, 20))
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 40, 41, 21))

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.submit.setText(QCoreApplication.translate("Dialog", u"OK", None))
        self.server.setText(QCoreApplication.translate("Dialog", u"server", None))
        self.port.setText(QCoreApplication.translate("Dialog", u"8888", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"port", None))
        self.client.setText(QCoreApplication.translate("Dialog", u"client", None))
        self.ip.setText(QCoreApplication.translate("Dialog", u"127.0.0.1", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"ip", None))
        self.name.setText(QCoreApplication.translate("Dialog", u"Player", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"name", None))
    # retranslateUi

