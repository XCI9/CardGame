import sys
from PySide6.QtWidgets import QWidget, QStyledItemDelegate, QListView, QStyle
from PySide6.QtCore import Qt, Signal, QAbstractListModel, QModelIndex, QSize, Slot, QObject
from PySide6.QtGui import QRegion
from mainwindow_ui import Ui_MainWindow

from cardtype_ui import Ui_Form as CardTypeForm
from utilities import *
from typing import Optional
from client import GameCoreClient

class CardTypeBlock(QWidget):
    def __init__(self, playable = True, hand: Optional[Hand] = None, is_erased = False, parent=None):
        super().__init__(parent)

        self.hand = hand
        self.is_erased = is_erased
        self.playable = playable
        self.ui = CardTypeForm()
        self.ui.setupUi(self)
        self.ui.cannot_play_reason.hide()

        # set displayed info
        if hand is not None and len(hand.card) > 0:
            # "<N> [<N> <N>]"
            card_number_str = ''
            for number in hand.card:
                card_number_str += f'{number} '
            card_number_str = card_number_str[:-1] # remove last space

            self.ui.card.setText(card_number_str)
            if self.is_erased:
                self.ui.type.setText('消除')
                self.ui.value.setText('')
                self.ui.eliminate.setText('')
                return

            match hand.rank:
                case 'void3' | 'rare triple' | 'triple':
                    card_type_name = f'{hand.value}{hand.value}{hand.value}'
                case 'triangle':
                    card_type_name = '直角三角形'
                case 'straight':
                    card_type_name = '順子'
                case 'rare double' | 'double' | 'void2':
                    card_type_name = f'對子{hand.value}'
                case 'square':
                    card_type_name = '完全平方數'
                case 'rare single' | 'single':
                    card_type_name = f'單支{hand.value}'
            
            self.ui.type.setText(card_type_name)

            if hand.suit != -1:
                self.ui.value.setText(f'附帶{hand.suit}')
            else:
                if hand.rank in ['triple', 'double', 'single']:
                    self.ui.value.setText(f'無附帶')
                else:
                    self.ui.value.setText(f'{hand.value}')
            self.ui.eliminate.setText('可消除' if hand.eraseable else '')

class CardTypeDelegate(QStyledItemDelegate):
    def __init__(self, listView: QListView, parent=None):
        super().__init__(parent)
        self.listView = listView
        self._parent = parent

    def sizeHint(self, option, index):
        return index.data(Qt.ItemDataRole.SizeHintRole)

    def paint(self, painter, option, index):
        if index.isValid():
            widget = index.data(Qt.ItemDataRole.DisplayRole)
            if isinstance(widget, CardTypeBlock):
                # Draw the CardTypeBlock widget onto the painter
                widget.render(painter, option.rect.topLeft() + self.listView.pos(), QRegion())
        super().paint(painter, option, index)

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        item_data: CardTypeBlock = index.data(Qt.ItemDataRole.DisplayRole)
        if not item_data.playable:  # Disable selection
            option.state &= ~QStyle.State_Selected

class CardListModel(QAbstractListModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []

    def rowCount(self, parent=None):
        return len(self._data)

    def data(self, index, role):
        if index.isValid() and role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()]

        if index.isValid() and role == Qt.ItemDataRole.SizeHintRole:
            return QSize(244, 54)  # Adjust size hint as needed

        return None

class HandSelector:
    def __init__(self, ui: Ui_MainWindow, core: GameCoreClient):
        self.ui = ui
        self.listView = ui.card_selector
        self.core = core

        self.listView.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.listView.setSelectionBehavior(QListView.SelectionBehavior.SelectRows)
        self.listView.clicked.connect(self.handle_item_selection)

        self.cardtypes: list[CardTypeBlock] = []

        # Create and set the data model for the QListView
        self.data_model = CardListModel(self.cardtypes)  # Example data
        self.listView.setModel(self.data_model)

        # Create and set the delegate for the QListView
        card_delegate = CardTypeDelegate(self.listView)
        self.listView.setItemDelegate(card_delegate)
    
    @Slot(QModelIndex)
    def handle_item_selection(self, index: QModelIndex):
        selected_item_data: CardTypeBlock = index.data(Qt.ItemDataRole.DisplayRole)
        if not selected_item_data.playable:
            return

        selection_model = self.listView.selectionModel()
        self.selected_index = selection_model.currentIndex().row()
        #print("Selected index:", self.selected_index)

    @Slot(list)
    def changeChooseCards(self, cards:list[int]):
        self.core.selectCards(cards)
        player_utility = self.core.current_player


        self.cardtypes = []
        playable_indexes: list[int] = []
        for i, (hand, not_playable_reason) in enumerate(zip(player_utility.avalhands, player_utility.avalhands_info)):
            cardtype = CardTypeBlock(True, hand, player_utility.for_erase)
            if not_playable_reason == 'playable':
                playable_indexes.append(i)
            else:
                cardtype.setStyleSheet('QLabel{color:#999}')
                cardtype.ui.cannot_play_reason.setText(not_playable_reason)
            self.cardtypes.append(cardtype)


        self.data_model = CardListModel(self.cardtypes)  # Example data
        self.listView.setModel(self.data_model)
        if len(playable_indexes) == 1:
            self.listView.setCurrentIndex(self.data_model.index(playable_indexes[0], 0))
            

    def getSelectedCard(self) -> tuple[int, Optional[CardTypeBlock]]:
        selection_model = self.listView.selectionModel()
        selected_index = selection_model.currentIndex().row()
        if selected_index == -1:
            return selected_index, None
        return selected_index, self.cardtypes[selected_index]

    def clearChoose(self):
        self.listView.setModel(CardListModel([]))