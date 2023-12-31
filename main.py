import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QDialog
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIntValidator
from mainwindow_ui import Ui_MainWindow
from LauncherDialog_ui import Ui_Dialog as Ui_ServerClientDialog
from PlayAgainDialog_ui import Ui_Dialog as Ui_PlayAgainDialog
from canva import Canva
from utilities import TableClassic, Hand
from hand import HandSelector, CardTypeBlock
from server import startServer
import os
import winsound
from client import GameCoreClient
from typing import Optional

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

class PlayerUi:
    def __init__(self, name_label: QLabel, 
                 icon_label: QLabel, 
                 hand_count_label: QLabel):
        self.name = name_label
        self.icon = icon_label
        self.hand_count = hand_count_label
        self.normal_styleSheet = 'border: 1px solid black;'\
                                 'border-radius: 10px;'\
                                 'background-color: #ff0'
        self.activate_styleSheet = 'border: 3px solid blue;'\
                                   'border-radius: 10px;'\
                                   'background-color: #ff0'

    def show(self):
        self.name.show()
        self.icon.show()
        self.hand_count.show()

    def hide(self):
        self.name.hide()
        self.icon.hide()
        self.hand_count.hide()

    def activate(self):
        self.icon.setStyleSheet(self.activate_styleSheet)

    def deactivate(self):
        self.icon.setStyleSheet(self.normal_styleSheet)

    def setHandNumber(self, number: int):
        self.hand_count.setText(f'{number}')

    def setPlayerName(self, name: str):
        self.name.setText(name)
        self.icon.setText(name[0])


class MainWindow(QMainWindow):
    connect_failed = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.sound_path = os.environ['WINDIR'] + "\Media\Windows Battery Critical.wav"

        self.dialog = LauncherDialog()
        self.connect_failed.connect(self.dialog.reinputInfo)
        self.dialog.make_connection.connect(self.makeConnection)

        self.core = GameCoreClient()
        self.core.network_handler.gameover.connect(self.gameover)
        self.core.network_handler.update_players.connect(self.dialog.updatePlayers)
        self.core.network_handler.sync_game.connect(self.syncGame)
        self.core.network_handler.connection_lose.connect(self.connectionLose)
        self.core.network_handler.others_play_hand.connect(self.othersPlayerHand)
        self.core.network_handler.others_erase_hand.connect(self.othersEraseHand)
        self.core.network_handler.connection_error.connect(self.connect_failed)

        self.scene = Canva()
        self.ui.canva.setScene(self.scene)
        self.ui.canva.setSceneRect(self.scene.sceneRect())
        self.ui.canva.verticalScrollBar().blockSignals(True)
        self.ui.canva.horizontalScrollBar().blockSignals(True)
        self.ui.canva.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.hand_selector = HandSelector(self.ui, self.core)
        self.scene.chooseCardsChanged.connect(self.hand_selector.changeChooseCards)
        self.ui.submit.clicked.connect(self.playCard)
        self.ui.pass_.clicked.connect(self.pass_)

        result = self.dialog.exec()

        self.gameover_dialog = PlayAgainDialog()
        self.gameover_dialog.play_again.connect(lambda: self.core.playAgain())
 
        self.run = True
        if result != QDialog.DialogCode.Accepted:
            self.run = False

        self.name = self.dialog.ui.name.text()
        self.setWindowTitle(f'籤筒-User {self.name}')

        self.prev_hand = None

        self.rule_info:list[tuple[QLabel, str]] = [(self.ui.rule9, '2壓1'),
                                                    (self.ui.rule19, '3壓2'),
                                                    (self.ui.rule29, '3壓1')]

        self.ui.cannot_play_msg.hide()       

        player0 = PlayerUi(self.ui.player0_name, self.ui.player0_icon, self.ui.player0_hand_count)
        player1 = PlayerUi(self.ui.player1_name, self.ui.player1_icon, self.ui.player1_hand_count)
        player2 = PlayerUi(self.ui.player2_name, self.ui.player2_icon, self.ui.player2_hand_count)
        player3 = PlayerUi(self.ui.player3_name, self.ui.player3_icon, self.ui.player3_hand_count)
        self.player_ui: list[PlayerUi] = [player0, player1, player2, player3]
        self.player_order = [0, 1, 2, 3]

    @Slot(str, str, int, int)
    def makeConnection(self, type:str, ip:str, port: int, player_count: int):
        if type == 'server':
            try:
                startServer("0.0.0.0", port, player_count)
            except OSError as e:
                print(e)
                self.connect_failed.emit('無法啟動伺服器!')
                return
            
        self.core.network_handler.connect_to_server(ip, port, 
                                                    self.dialog.ui.name.text())

    @Slot(Hand, int)
    def othersPlayerHand(self, hand:Optional[Hand], id: int):
        success = self.core.othersPlayHand(id, hand)

        # TODO: success check
        if not success:
            print('not success')
            pass
        
        if hand is not None:
            for card in hand.card:
                self.scene.playCard(card)

        self.updateGameStatus()

    @Slot(int, int)
    def othersEraseHand(self, card: int, id: int):
        success = self.core.othersEraseHand(id, card)

        # TODO: success check
        if not success:
            print('not success')
            pass

        self.scene.playCard(card)

        self.updateGameStatus()

    @Slot(TableClassic, int)
    def syncGame(self, table: TableClassic, id: int):
        self.core.setup(table, id)

        player_utility = self.core.current_player
        player = player_utility.player
        # reset status
        if self.gameover_dialog.isVisible():
            self.gameover_dialog.accept()
        self.scene.resetTable()
        for card in self.core.table.cards:
            self.scene.playCard(card)
        self.scene.initCard(player.cards)

        match len(table.players):
            case 4:
                self.player_ui[3].show()
                self.player_ui[2].show()
                self.player_ui[1].show()
                self.player_order = [0, 1, 2, 3]
            case 3:
                self.player_ui[3].show()
                self.player_ui[2].hide()
                self.player_ui[1].show()
                self.player_order = [0, 1, 3]
            case 2:
                self.player_ui[3].hide()
                self.player_ui[2].show()
                self.player_ui[1].hide()
                self.player_order = [0, 2]
            case _:
                raise NotImplementedError
        
        # move current player to first
        index = self.core.current_player_index
        move_diff = len(self.player_order)-index
        self.player_order = self.player_order[move_diff:] + self.player_order[:move_diff]
            
            
        for i, position in enumerate(self.player_order):
            name = self.core.table.players[i].name
            self.player_ui[position].setPlayerName(name)

        self.updateGameStatus()

        #for i in range(1, 43):
        #    self.scene.playCard(i)

    def updateGameStatus(self):
        player_utility = self.core.current_player
        player = player_utility.player

        self.ui.submit.setText('提交')
        self.ui.submit.setEnabled(False)
        self.ui.pass_.setEnabled(False)
        if player.his_turn:
            winsound.PlaySound(self.sound_path, winsound.SND_ALIAS)
            self.ui.submit.setEnabled(True)
            if player_utility.for_erase:
                self.ui.submit.setText('消除')
            if not player.lastplayed:
                self.ui.pass_.setEnabled(True)
           
        #self.hand_selector.refreshPlayableCard()

        # reset rule
        for (label, name), enable in zip(self.rule_info, self.core.getRule()):
            if enable:
                label.setText(f'{name}✔')
                label.setStyleSheet('QLabel{color:#22b14c}') # green
            else:
                label.setText(f'{name}✘')
                label.setStyleSheet('QLabel{color:#f00}')

        # update previous hand 
        if self.prev_hand is not None:
            self.ui.prev_hand.removeWidget(self.prev_hand)
            self.prev_hand.deleteLater()
            self.prev_hand = None
        if self.core.table.previous_hand.rank != 'None':
            self.prev_hand = CardTypeBlock(True, self.core.table.previous_hand)
            self.ui.prev_hand.addWidget(self.prev_hand)
            
        for i, position in enumerate(self.player_order):
            hand_num = len(self.core.table.players[i].cards)
            self.player_ui[position].setHandNumber(hand_num)

        last_player = self.core.table.get_player_index(-1)
        self.player_ui[self.player_order[last_player]].deactivate()
        
        current_player = self.core.table.get_player_index(0)
        self.player_ui[self.player_order[current_player]].activate()        

    def connectionLose(self):
        if self.dialog.isVisible():
            self.dialog.reinputInfo('伺服器關閉了連線!')
        else:
            if self.gameover_dialog.isVisible():
                self.gameover_dialog.close()
            self.close()
            return
        
        #self.core.resetSocket()

    @Slot(str)
    def gameover(self, winner: str):
        self.gameover_dialog.ui.winner.setText(f'遊戲結束! {winner}贏了!')
        self.gameover_dialog.ui.play_again.setEnabled(True)
        self.gameover_dialog.ui.play_again.setText('再來一場')
        result = self.gameover_dialog.exec()

        self.ui.submit.setEnabled(False)
        self.ui.pass_.setEnabled(False)

        self.ui.prev_hand.removeWidget(self.prev_hand)
        self.prev_hand.deleteLater()
        self.prev_hand = None

        if result == QDialog.DialogCode.Rejected:
            self.close()

    @Slot()
    def pass_(self):
        self.ui.cannot_play_msg.hide()

        self.core.passTurn()

        self.ui.submit.setEnabled(False)
        self.ui.pass_.setEnabled(False)

        self.updateGameStatus()

    @Slot()
    def playCard(self):
        selected_index, card_type = self.hand_selector.getSelectedCard()
        
        # nothing selected
        if selected_index == -1:
            self.ui.cannot_play_msg.show()
            return
        
        hand = card_type.hand

        self.ui.cannot_play_msg.hide()

        self.core.playHand(hand)

        for card in hand.card:
            self.scene.playCard(card)
        self.scene.removeCards(hand.card)

        self.hand_selector.clearChoose()

        self.updateGameStatus()

    def terminate(self):
        self.core.network_handler.disconnect_from_server()

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
