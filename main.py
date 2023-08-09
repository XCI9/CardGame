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
from ConnectionLogger import ConnectionLogger

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
        self.ui.information.setText('')
        self.ui.information.hide()

        self.ui.client.toggled.connect(self.modeChange)

        self.ui.submit.clicked.connect(self.submit)

    def updatePlayers(self, players: list[str]):
        player_str = f'玩家({len(players)}/3):'
        for player in players:
            player_str += f' {player},'
        self.ui.information.setText(player_str[:-1])

        if len(players) == 3: # start game
            self.accept()

    def submit(self):       
        self.ui.submit.setText('等待玩家中')
        self.ui.submit.setEnabled(False)
        self.ui.name.setEnabled(False)
        self.ui.ip.setEnabled(False)
        self.ui.port.setEnabled(False)
        self.ui.information.setText('')
        self.ui.information.setStyleSheet('')

        if self.ui.client.isChecked():
            self.make_connection.emit("client", self.ui.ip.text(), int(self.ui.port.text()))
        else:
            self.make_connection.emit("server", "127.0.0.1", int(self.ui.port.text()))

        self.ui.information.show()

    def reinputInfo(self, error_msg: str):
        self.ui.submit.setText('OK')
        self.ui.submit.setEnabled(True)
        self.ui.name.setEnabled(True)
        self.ui.ip.setEnabled(self.ui.client.isChecked())
        self.ui.port.setEnabled(True)
        self.ui.information.setText(error_msg)
        self.ui.information.setStyleSheet('QLabel{color:#f00}')

    def modeChange(self):
        if self.ui.client.isChecked():
            self.ui.ip.setEnabled(True)
        else:
            self.ui.ip.setEnabled(False)

class MainWindow(QMainWindow):
    cannotMakeConnection = Signal(str)
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

        self.logger = ConnectionLogger('client')

        self.selected_index = None

        self.handChooser = HandChooser(self.ui, self.socket)
        self.handChooser.sendPackage.connect(self.sendPackage)
        self.scene.chooseCardsChanged.connect(self.handChooser.changeChooseCards)
        self.ui.submit.clicked.connect(self.playCard)
        self.ui.eliminate.clicked.connect(self.chooseEliminate)
        self.ui.pass_.clicked.connect(self.pass_)

        self.dialog = ServerClientDialog()
        self.cannotMakeConnection.connect(self.dialog.reinputInfo)
        self.dialog.make_connection.connect(self.makeConnection)
        result = self.dialog.exec()

        self.run = True
        if result != QDialog.Accepted:
            self.run = False

        self.name = self.dialog.ui.name.text()
        self.setWindowTitle(f'籤筒-User {self.name}')

        self.prev_hand = None

        self.rule_info:list[tuple[int,QLabel, str]] = [(9, self.ui.rule9, '2壓1'),
                                                       (19, self.ui.rule19, '3壓2'),
                                                       (29, self.ui.rule29, '3壓1')]

        self.ui.cannot_play_msg.hide()
        self.ui.eliminate.hide()
        self.ui.gameover_msg.hide()

    @Slot(Package.Package)
    def sendPackage(self, package:Package.Package):
        package_byte = pickle.dumps(package)
        self.socket.send(package_byte)
        self.logger.log('send', self.socket, str(package))

    @Slot(str, str, int)
    def makeConnection(self, type:str, ip:str, port: int):
        if type == 'server':
            try:
                startServer("0.0.0.0", port)
            except OSError as e:
                print(e)
                self.cannotMakeConnection.emit('無法啟動伺服器!')
                return
        try:
            self.socket.connect((ip, port))
        except ConnectionRefusedError:
            self.cannotMakeConnection.emit('無法與伺服器建立連線!')
            return
        
        self.logger.log('connect', self.socket, '')

        self.network_handler = NetworkHandler(self.socket, self.logger)
        self.network_handler.response_playable.connect(self.handChooser.updatePlayableCard)
        self.network_handler.update_table.connect(self.updateTable)
        self.network_handler.init_card.connect(self.scene.initCard)
        self.network_handler.your_turn.connect(self.setMyTurn)
        self.network_handler.change_turn.connect(self.changeTurnName)
        self.network_handler.gameover.connect(self.gameover)
        self.network_handler.update_cards_count.connect(self.updateCardCount)
        self.network_handler.update_players.connect(self.dialog.updatePlayers)
        self.network_handler.connection_lose.connect(self.connectionLose)
        self.network_handler.start()

        self.socket.send(pickle.dumps(Package.SendName(self.dialog.ui.name.text())))

    def connectionLose(self):
        if self.dialog.isVisible():
            self.dialog.reinputInfo('伺服器關閉了連線!')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.handChooser.socket = self.socket

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

        self.sendPackage(Package.PlayCard(None))

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
        self.sendPackage(Package.PlayCard(hand))
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

    def terminate(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.network_handler.wait()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MainWindow()
    if widget.run:
        widget.show()
        exit_code = app.exec()
    else:
        exit_code = 0

    widget.terminate()
    sys.exit(exit_code)
