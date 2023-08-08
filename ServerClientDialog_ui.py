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
        Dialog.resize(331, 105)
        self.submit = QPushButton(Dialog)
        self.submit.setObjectName(u"submit")
        self.submit.setGeometry(QRect(240, 70, 75, 24))
        self.server = QRadioButton(Dialog)
        self.server.setObjectName(u"server")
        self.server.setGeometry(QRect(20, 10, 61, 20))
        self.port = QLineEdit(Dialog)
        self.port.setObjectName(u"port")
        self.port.setGeometry(QRect(70, 70, 61, 20))
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(30, 70, 31, 21))
        self.client = QRadioButton(Dialog)
        self.client.setObjectName(u"client")
        self.client.setGeometry(QRect(20, 40, 61, 20))
        self.ip = QLineEdit(Dialog)
        self.ip.setObjectName(u"ip")
        self.ip.setGeometry(QRect(110, 40, 201, 20))
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(90, 40, 16, 21))

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
    # retranslateUi

