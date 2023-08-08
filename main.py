import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QAbstractItemView, QStyledItemDelegate, QVBoxLayout, QListView, QHBoxLayout, QStyle
from PySide6.QtCore import Qt, Signal, QAbstractListModel, QModelIndex, QSize, Slot
from PySide6.QtGui import QStandardItem, QStandardItemModel, QPixmap, QRegion, QPainter
from mainwindow_ui import Ui_MainWindow
from canva import Canva
from game import *
from HandChooser import HandChooser, CardTypeBlock

"""
The frame of this application
Contained a field that can show position animationally,
and tabs with different function
Each tabs is composed of two parts, widget and controller,
we'll initial the widget first and pass it to a controller to control it
"""

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.scene = Canva()
        self.ui.canva.setScene(self.scene)
        self.ui.canva.setSceneRect(self.scene.sceneRect())
        self.ui.canva.verticalScrollBar().blockSignals(True)
        self.ui.canva.horizontalScrollBar().blockSignals(True)
        self.ui.canva.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.selected_index = None

        self.board = TableClassic()

        self.handChooser = HandChooser(self.ui, self.board)
        self.scene.chooseCardsChanged.connect(self.handChooser.changeChooseCards)
        self.ui.submit.clicked.connect(self.playCard)
        self.ui.eliminate.clicked.connect(self.chooseEliminate)

        self.prev_hand = None

        self.ui.cannot_play_msg.hide()
        self.ui.eliminate.hide()

    @Slot()
    def chooseEliminate(self):
        self.handChooser.chooseEliminate(self.scene.slot)

    @Slot()
    def playCard(self):
        selected_index, card_type = self.handChooser.getSelectedCard()
        
        if selected_index == -1:
            self.ui.cannot_play_msg.show()
            return
        
        hand = card_type.hand
        self.ui.cannot_play_msg.hide()
        if card_type.eliminate_card is not None:
            self.scene.removeCard(card_type.eliminate_card)
        self.scene.removeCards(hand.card)

        self.board.play_hand(hand)
        for card in hand.card:
            self.scene.playCard(card)
        if card_type.eliminate_card is not None:
            self.scene.playCard(card_type.eliminate_card)
        self.handChooser.clearChoose()
        
        for rule, label, name in [(self.board.rule9, self.ui.rule9, '2壓1'),
                                  (self.board.rule19, self.ui.rule19, '3壓2'),
                                  (self.board.rule29, self.ui.rule29, '3壓1')]:
            if rule is True:
                label.setText(f'{name}✓')
                label.setStyleSheet('QLabel{color:#22b14c}')
            else:
                label.setText(f'{name}✘')
                label.setStyleSheet('QLabel{color:#f00}')

        if self.prev_hand is not None:
            self.ui.prev_hand.removeWidget(self.prev_hand)
            self.prev_hand.deleteLater()
        self.prev_hand = CardTypeBlock(True, self.board.previous_hand)
        self.ui.prev_hand.addWidget(self.prev_hand)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
