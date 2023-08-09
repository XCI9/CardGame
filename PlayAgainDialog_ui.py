# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PlayAgainDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(334, 125)
        self.winner = QLabel(Dialog)
        self.winner.setObjectName(u"winner")
        self.winner.setGeometry(QRect(10, 30, 321, 31))
        font = QFont()
        font.setPointSize(20)
        self.winner.setFont(font)
        self.winner.setAlignment(Qt.AlignCenter)
        self.horizontalLayoutWidget = QWidget(Dialog)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(60, 80, 221, 41))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setSpacing(50)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.play_again = QPushButton(self.horizontalLayoutWidget)
        self.play_again.setObjectName(u"play_again")

        self.horizontalLayout.addWidget(self.play_again)

        self.exit = QPushButton(self.horizontalLayoutWidget)
        self.exit.setObjectName(u"exit")

        self.horizontalLayout.addWidget(self.exit)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"\u904a\u6232\u7d50\u675f", None))
        self.winner.setText(QCoreApplication.translate("Dialog", u"\u904a\u6232\u7d50\u675f! \u4f60\u8d0f\u4e86!", None))
        self.play_again.setText(QCoreApplication.translate("Dialog", u"\u518d\u4f86\u4e00\u5834", None))
        self.exit.setText(QCoreApplication.translate("Dialog", u"\u9000\u51fa\u904a\u6232", None))
    # retranslateUi

