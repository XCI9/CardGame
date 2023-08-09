import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QDialog, QAbstractItemView, QStyledItemDelegate, QVBoxLayout, QListView, QHBoxLayout, QStyle
from PySide6.QtCore import Qt, Signal, QAbstractListModel, QModelIndex, QSize, Slot, QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel, QPixmap, QRegion, QPainter, QIntValidator
from mainwindow_ui import Ui_MainWindow
from ServerClientDialog_ui import Ui_Dialog
from canva import Canva
from game import *
from HandChooser import HandChooser, CardTypeBlock
from client import NetworkHandler
from server import startServer
from package import Package
import socket
import pickle
import os

"""
The frame of this application
Contained a field that can show position animationally,
and tabs with different function
Each tabs is composed of two parts, widget and controller,
we'll initial the widget first and pass it to a controller to control it
"""

class ServerClientDialog(QDialog):
    make_connection = Signal(str,str,int)
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowTitle('籤筒啟動器')

        only_int = QIntValidator()
        only_int.setRange(0, 65536)
        self.ui.port.setValidator(only_int)

        #default name use current user name
        self.ui.name.setText(os.getlogin())
        self.ui.player.hide()

        self.ui.client.toggled.connect(self.modeChange)

        self.ui.submit.clicked.connect(self.submit)

    def updatePlayers(self, players: list[str]):
        player_str = f'玩家({len(players)}/3):'
        for player in players:
            player_str += f' {player},'
        self.ui.player.setText(player_str[:-1])

        if len(players) == 3: # start game
            self.accept()

    def submit(self):       
        self.ui.submit.setText('等待玩家中')
        self.ui.submit.setEnabled(False)
        self.ui.player.show()

        if self.ui.client.isChecked():
            self.make_connection.emit("client", self.ui.ip.text(), int(self.ui.port.text()))
        else:
            self.make_connection.emit("server", "127.0.0.1", int(self.ui.port.text()))

    def modeChange(self):
        if self.ui.client.isChecked():
            self.ui.ip.setEnabled(True)
        else:
            self.ui.ip.setEnabled(False)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.scene = Canva()
        self.ui.canva.setScene(self.scene)
        self.ui.canva.setSceneRect(self.scene.sceneRect())
        self.ui.canva.verticalScrollBar().blockSignals(True)
        self.ui.canva.horizontalScrollBar().blockSignals(True)
        self.ui.canva.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.selected_index = None

        self.handChooser = HandChooser(self.ui, self.socket)
        self.scene.chooseCardsChanged.connect(self.handChooser.changeChooseCards)
        self.ui.submit.clicked.connect(self.playCard)
        self.ui.eliminate.clicked.connect(self.chooseEliminate)
        self.ui.pass_.clicked.connect(self.pass_)

        self.dialog = ServerClientDialog()
        self.dialog.make_connection.connect(self.makeConnection)
        result = self.dialog.exec()

        if result != QDialog.Accepted:
            sys.exit(-1)


        self.name = self.dialog.ui.name.text()
        self.setWindowTitle(f'籤筒-User {self.name}')

        self.prev_hand = None

        self.rule_info:list[tuple[int,QLabel, str]] = [(9, self.ui.rule9, '2壓1'),
                                                       (19, self.ui.rule19, '3壓2'),
                                                       (29, self.ui.rule29, '3壓1')]

        self.ui.cannot_play_msg.hide()
        self.ui.eliminate.hide()
        self.ui.gameover_msg.hide()

    @Slot(str, str, int)
    def makeConnection(self, type:str, ip:str, port: int):
        if type == 'server':
            startServer("0.0.0.0", port)
            self.socket.connect(("127.0.0.1", port))
        else:
            self.socket.connect((ip, port))

        self.network_handler = NetworkHandler(self.socket)
        self.network_handler.response_playable.connect(self.handChooser.updatePlayableCard)
        self.network_handler.update_table.connect(self.updateTable)
        self.network_handler.init_card.connect(self.scene.initCard)
        self.network_handler.your_turn.connect(self.setMyTurn)
        self.network_handler.change_turn.connect(self.changeTurnName)
        self.network_handler.gameover.connect(self.gameover)
        self.network_handler.update_cards_count.connect(self.updateCardCount)
        self.network_handler.update_players.connect(self.dialog.updatePlayers)
        self.network_handler.start()

        self.socket.send(pickle.dumps(Package.SendName(self.dialog.ui.name.text())))

    @Slot(str)
    def gameover(self, winner: str):
        self.ui.gameover_msg.setText(f'遊戲結束! {winner}贏了!')
        self.ui.gameover_msg.show()

    @Slot(str)
    def changeTurnName(self, name:str):
        self.ui.turn_player_name.setText(f'目前輪到: {name}')

    @Slot()
    def chooseEliminate(self):
        self.handChooser.chooseEliminate(self.scene.slot)

    @Slot()
    def pass_(self):
        self.ui.cannot_play_msg.hide()

        package = pickle.dumps(Package.PlayCard(None))
        self.socket.send(package)

        self.ui.submit.setEnabled(False)
        self.ui.pass_.setEnabled(False)

    @Slot()
    def playCard(self):
        selected_index, card_type = self.handChooser.getSelectedCard()
        
        # nothing selected
        if selected_index == -1:
            self.ui.cannot_play_msg.show()
            return
        
        hand = card_type.hand

        self.ui.cannot_play_msg.hide()

        # remove played card from hand
        if card_type.hand.erased_card is not None:
            self.scene.removeCard(card_type.hand.erased_card)
        self.scene.removeCards(hand.card)

        # put played card onto table
        package = pickle.dumps(Package.PlayCard(hand))
        self.socket.send(package)
        #self.board.play_hand(hand)

        self.handChooser.clearChoose()
        self.ui.submit.setEnabled(False)
        self.ui.pass_.setEnabled(False)

    @Slot(Hand)
    def updateTable(self, hand: Hand):
        for card in hand.card:
            self.scene.playCard(card)

        if hand.erased_card is not None:
            self.scene.playCard(hand.erased_card)
        #if card_type.eliminate_card is not None:
        #    self.scene.playCard(card_type.eliminate_card)

        # update previous hand 
        if self.prev_hand is not None:
            self.ui.prev_hand.removeWidget(self.prev_hand)
            self.prev_hand.deleteLater()
        self.prev_hand = CardTypeBlock(True, hand)
        self.ui.prev_hand.addWidget(self.prev_hand)

        #update rule hint
        for enable_rule_num, label, name in self.rule_info:
            disable_rule_num = enable_rule_num - 1
            if enable_rule_num in hand.card:
                label.setText(f'{name}✔')
                label.setStyleSheet('QLabel{color:#22b14c}') # green
            if disable_rule_num in hand.card:
                label.setText(f'{name}✘')
                label.setStyleSheet('QLabel{color:#f00}')

    @Slot(bool)
    def setMyTurn(self, is_forced: bool):
        self.ui.submit.setEnabled(True)
        self.ui.turn_player_name.setText(f'目前輪到: 你')
        if not is_forced:
            self.ui.pass_.setEnabled(True)

    @Slot(list)
    def updateCardCount(self, cards_count:list):
        display_str = '剩餘牌數: '
        for name, count in cards_count:
            if name != self.name:
                display_str += f'{name}-{count} '
        self.ui.card_count.setText(display_str)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
