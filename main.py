import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QDialog
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIntValidator
from mainwindow_ui import Ui_MainWindow
from LauncherDialog_ui import Ui_Dialog as Ui_ServerClientDialog
from PlayAgainDialog_ui import Ui_Dialog as Ui_PlayAgainDialog
from canva import Canva
from utilities import *
from hand import HandSelector, CardTypeBlock
from client import NetworkHandler
from server import startServer
from package import Package
import socket
import pickle
import os
import struct
from logger import ConnectionLogger
import winsound

"""
The frame of this application
Contained a field that can show position animationally,
and tabs with different function
Each tabs is composed of two parts, widget and controller,
we'll initial the widget first and pass it to a controller to control it
"""

class LauncherDialog(QDialog):
    make_connection = Signal(str,str,int,int)
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = Ui_ServerClientDialog()
        self.ui.setupUi(self)

        only_int = QIntValidator()
        only_int.setRange(0, 65536)
        self.ui.port.setValidator(only_int)

        only_int = QIntValidator()
        only_int.setRange(2, 3)
        self.ui.player_count.setValidator(only_int)

        #default name use current user name
        self.ui.name.setText(os.getlogin())
        self.ui.information.setText('')
        self.ui.information.hide()

        self.ui.client.toggled.connect(self.modeChange)

        self.ui.submit.clicked.connect(self.submit)

    def updatePlayers(self, players: list[str], full_count: int):
        player_str = f'玩家({len(players)}/{full_count}):'
        for player in players:
            player_str += f' {player},'
        self.ui.information.setText(player_str[:-1])

        if len(players) == full_count: # start game
            self.accept()

    def submit(self):       
        self.ui.submit.setText('等待玩家中')
        self.ui.submit.setEnabled(False)
        self.ui.name.setEnabled(False)
        self.ui.ip.setEnabled(False)
        self.ui.port.setEnabled(False)
        self.ui.player_count.setEnabled(False)
        self.ui.client.setEnabled(False)
        self.ui.server.setEnabled(False)
        self.ui.information.setText('')
        self.ui.information.setStyleSheet('')

        if self.ui.client.isChecked():
            self.make_connection.emit("client", self.ui.ip.text(), int(self.ui.port.text()), -1)
        else:
            self.make_connection.emit("server", "127.0.0.1", 
                                      int(self.ui.port.text()), int(self.ui.player_count.text()))

        self.ui.information.show()

    def reinputInfo(self, error_msg: str):
        self.ui.submit.setText('OK')
        self.ui.submit.setEnabled(True)
        self.ui.name.setEnabled(True)
        self.ui.ip.setEnabled(self.ui.client.isChecked())
        self.ui.player_count.setEnabled(self.ui.server.isChecked())
        self.ui.port.setEnabled(True)
        self.ui.client.setEnabled(True)
        self.ui.server.setEnabled(True)
        self.ui.information.setText(error_msg)
        self.ui.information.setStyleSheet('QLabel{color:#f00}')

    def modeChange(self):
        if self.ui.client.isChecked():
            self.ui.ip.setEnabled(True)
            self.ui.player_count.setEnabled(False)
        else:
            self.ui.ip.setEnabled(False)
            self.ui.player_count.setEnabled(True)

class PlayAgainDialog(QDialog):
    play_again = Signal()
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = Ui_PlayAgainDialog()
        self.ui.setupUi(self)

        self.ui.play_again.clicked.connect(self.playAgain)
        self.ui.exit.clicked.connect(self.reject)

    def playAgain(self):
        self.ui.play_again.setEnabled(False)

        self.ui.play_again.setText('等待其餘玩家')
        self.play_again.emit()

class MainWindow(QMainWindow):
    connect_failed = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.sound_path = os.environ['WINDIR'] + "\Media\Windows Battery Critical.wav"

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self.scene = Canva()
        self.ui.canva.setScene(self.scene)
        self.ui.canva.setSceneRect(self.scene.sceneRect())
        self.ui.canva.verticalScrollBar().blockSignals(True)
        self.ui.canva.horizontalScrollBar().blockSignals(True)
        self.ui.canva.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.logger = ConnectionLogger('client')

        self.hand_selector = HandSelector(self.ui, self.socket)
        self.hand_selector.sendPackage.connect(self.sendPackage)
        self.scene.chooseCardsChanged.connect(self.hand_selector.changeChooseCards)
        self.ui.submit.clicked.connect(self.playCard)
        self.ui.eliminate.clicked.connect(self.chooseEliminate)
        self.ui.pass_.clicked.connect(self.pass_)

        self.network_handler = None

        self.dialog = LauncherDialog()
        self.connect_failed.connect(self.dialog.reinputInfo)
        self.dialog.make_connection.connect(self.makeConnection)
        result = self.dialog.exec()

        self.gameover_dialog = PlayAgainDialog()
        self.gameover_dialog.play_again.connect(lambda: self.sendPackage(Package.AgainChk(True)))
 
        self.run = True
        if result != QDialog.Accepted:
            self.run = False

        self.name = self.dialog.ui.name.text()
        self.setWindowTitle(f'籤筒-User {self.name}')

        self.prev_hand = None

        self.rule_info:list[tuple[int, QLabel, str]] = [(9, self.ui.rule9, '2壓1'),
                                                       (19, self.ui.rule19, '3壓2'),
                                                       (29, self.ui.rule29, '3壓1')]

        self.ui.cannot_play_msg.hide()
        self.ui.eliminate.hide()

    @Slot(Package.Package)
    def sendPackage(self, package:Package.Package):
        package_byte = pickle.dumps(package)
        message_length = len(package_byte)
        header = struct.pack("!I", message_length)  # "!I" indicates network byte order for an unsigned int
        self.socket.sendall(header + package_byte)
        self.logger.log('send', self.socket, str(package))

    @Slot(str, str, int, int)
    def makeConnection(self, type:str, ip:str, port: int, player_count: int):
        if type == 'server':
            try:
                startServer("0.0.0.0", port, player_count)
            except OSError as e:
                print(e)
                self.connect_failed.emit('無法啟動伺服器!')
                return
        try:
            self.socket.connect((ip, port))
        except ConnectionRefusedError:
            self.connect_failed.emit('無法與伺服器建立連線!')
            return
        
        self.logger.log('connect', self.socket, '')

        self.network_handler = NetworkHandler(self.socket, self.logger)
        self.network_handler.response_playable.connect(self.hand_selector.setPlayableCard)
        self.network_handler.update_table.connect(self.updateTable)
        self.network_handler.init_card.connect(self.initCard)
        self.network_handler.your_turn.connect(self.setMyTurn)
        self.network_handler.change_turn.connect(self.changeTurnName)
        self.network_handler.gameover.connect(self.gameover)
        self.network_handler.update_cards_count.connect(self.updateCardCount)
        self.network_handler.update_players.connect(self.dialog.updatePlayers)
        self.network_handler.connection_lose.connect(self.connectionLose)
        self.network_handler.start()

        self.sendPackage(Package.SendName(self.dialog.ui.name.text()))

    @Slot(list)
    def initCard(self, cards):
        if self.gameover_dialog.isVisible():
            self.gameover_dialog.accept()
        self.scene.resetTable()
        self.scene.initCard(cards)

        # reset rule
        for enable_rule_num, label, name in self.rule_info:
            label.setText(f'{name}✘')
            label.setStyleSheet('QLabel{color:#f00}')

    def connectionLose(self):
        if self.dialog.isVisible():
            self.dialog.reinputInfo('伺服器關閉了連線!')
        else:
            if self.gameover_dialog.isVisible():
                self.gameover_dialog.close()
            self.close()
            return

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.hand_selector.socket = self.socket

    @Slot(str)
    def gameover(self, winner: str):
        self.gameover_dialog.ui.winner.setText(f'遊戲結束! {winner}贏了!')
        self.gameover_dialog.ui.play_again.setEnabled(True)
        self.gameover_dialog.ui.play_again.setText('再來一場')
        result = self.gameover_dialog.exec()

        self.ui.submit.setEnabled(False)
        self.ui.pass_.setEnabled(False)
        self.ui.eliminate.hide()

        self.ui.prev_hand.removeWidget(self.prev_hand)
        self.prev_hand.deleteLater()
        self.prev_hand = None

        if result == QDialog.DialogCode.Rejected:
            self.close()

    @Slot(str)
    def changeTurnName(self, name:str):
        self.ui.turn_player_name.setText(f'目前輪到: {name}')
        self.hand_selector.refreshPlayableCard()

    @Slot()
    def chooseEliminate(self):
        self.hand_selector.chooseEliminate(self.scene.slot)

    @Slot()
    def pass_(self):
        self.ui.cannot_play_msg.hide()

        self.sendPackage(Package.PlayCard(None))

        self.ui.submit.setEnabled(False)
        self.ui.pass_.setEnabled(False)

    @Slot()
    def playCard(self):
        selected_index, card_type = self.hand_selector.getSelectedCard()
        
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

        self.hand_selector.clearChoose()
        self.ui.submit.setEnabled(False)
        self.ui.pass_.setEnabled(False)
        self.ui.eliminate.hide()

    @Slot(Hand)
    def updateTable(self, hand: Hand):
        for card in hand.card:
            self.scene.playCard(card)

        if hand.erased_card is not None:
            self.scene.playCard(hand.erased_card)

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
        winsound.PlaySound(self.sound_path, winsound.SND_ALIAS)
        self.hand_selector.refreshPlayableCard()
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
        if self.socket.fileno() != -1:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
        if self.network_handler is not None:
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
