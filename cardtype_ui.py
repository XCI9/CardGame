# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cardtype.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(201, 54)
        Form.setStyleSheet(u"")
        self.card = QLabel(Form)
        self.card.setObjectName(u"card")
        self.card.setGeometry(QRect(10, 10, 91, 31))
        font = QFont()
        font.setPointSize(16)
        self.card.setFont(font)
        self.eliminate = QLabel(Form)
        self.eliminate.setObjectName(u"eliminate")
        self.eliminate.setGeometry(QRect(160, 5, 41, 21))
        font1 = QFont()
        font1.setUnderline(False)
        self.eliminate.setFont(font1)
        self.eliminate.setStyleSheet(u"QLabel:hover{color:#00f}")
        self.type = QLabel(Form)
        self.type.setObjectName(u"type")
        self.type.setGeometry(QRect(100, 30, 61, 21))
        self.value = QLabel(Form)
        self.value.setObjectName(u"value")
        self.value.setGeometry(QRect(130, 30, 61, 21))
        self.value.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.widget = QWidget(Form)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(90, 180, 120, 80))
        self.cannot_play_reason = QLabel(Form)
        self.cannot_play_reason.setObjectName(u"cannot_play_reason")
        self.cannot_play_reason.setGeometry(QRect(100, 5, 101, 21))
        self.cannot_play_reason.setStyleSheet(u"QLabel{color:#f00}")
        self.cannot_play_reason.raise_()
        self.card.raise_()
        self.eliminate.raise_()
        self.type.raise_()
        self.value.raise_()
        self.widget.raise_()

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.card.setText(QCoreApplication.translate("Form", u"20 21 29", None))
        self.eliminate.setText(QCoreApplication.translate("Form", u"\u53ef\u6d88\u9664", None))
        self.type.setText(QCoreApplication.translate("Form", u"\u76f4\u89d2\u4e09\u89d2\u5f62", None))
        self.value.setText(QCoreApplication.translate("Form", u"16", None))
        self.cannot_play_reason.setText(QCoreApplication.translate("Form", u"\u4e0d\u53ef\u6253\u51fa\u539f\u56e0", None))
    # retranslateUi

