import sys
from PySide6.QtWidgets import QWidget, QStyledItemDelegate, QListView, QStyle
from PySide6.QtCore import Qt, Signal, QAbstractListModel, QModelIndex, QSize, Slot, QObject
from PySide6.QtGui import QRegion
from mainwindow_ui import Ui_MainWindow

from package import Package
from cardtype_ui import Ui_Form as CardTypeForm
from canva import PrivateCardPlacer
from game import *
import socket

class CardTypeBlock(QWidget):
    def __init__(self, playable = True, hand:Hand = None, need_erased_1 = False, parent=None):
        super().__init__(parent)

        self.hand = hand
        self.need_erased_1 = need_erased_1
        self.playable = playable
        self.ui = CardTypeForm()
        self.ui.setupUi(self)
        self.ui.cannot_play_reason.hide()

        # set displayed info
        if self.hand is not None:

            # "<N> [<N> <N>]"
            card_number_str = ''
            for number in hand.card:
                card_number_str += f'{number} '
            card_number_str = card_number_str[:-1] # remove last space

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
            
            self.ui.card.setText(card_number_str)
            self.ui.type.setText(card_type_name)

            if hand.suit != -1:
                self.ui.value.setText(f'附帶{hand.suit}')
            else:
                if hand.rank in ['triple', 'double', 'single']:
                    self.ui.value.setText(f'無附帶')
                else:
                    self.ui.value.setText(f'{hand.value}')
            self.ui.eliminate.setText('可消除' if hand.eraseable else '')
            if self.hand.erased_card is not None:
                self.ui.eliminate.setText(f'消除{self.hand.erased_card}')

class CardTypeDelegate(QStyledItemDelegate):
    def __init__(self, listView: QListView, parent=None):
        super().__init__(parent)
        self.listView = listView
        self._parent = parent

    def sizeHint(self, option, index):
        return index.data(Qt.SizeHintRole)

    def paint(self, painter, option, index):
        if index.isValid():
            widget = index.data(Qt.DisplayRole)
            if isinstance(widget, CardTypeBlock):
                # Draw the CardTypeBlock widget onto the painter
                widget.render(painter, option.rect.topLeft() + self.listView.pos(), QRegion())
        super().paint(painter, option, index)

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        item_data: CardTypeBlock = index.data(Qt.DisplayRole)
        if not item_data.playable:  # Disable selection
            option.state &= ~QStyle.State_Selected

class CardListModel(QAbstractListModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []

    def rowCount(self, parent=None):
        return len(self._data)

    def data(self, index, role):
        if index.isValid() and role == Qt.DisplayRole:
            return self._data[index.row()]

        if index.isValid() and role == Qt.SizeHintRole:
            return QSize(244, 54)  # Adjust size hint as needed

        return None

class HandSelector(QObject):
    sendPackage = Signal(Package.Package)

    def __init__(self, ui: Ui_MainWindow, sock: socket.socket):
        super().__init__()
        self.ui = ui
        self.listView = ui.card_selector
        self.socket = sock

        self.listView.setSelectionMode(QListView.SingleSelection)
        self.listView.setSelectionBehavior(QListView.SelectRows)
        self.listView.clicked.connect(self.handle_item_selection)

        self.cardtypes: list[CardTypeBlock] = []

        # Create and set the data model for the QListView
        self.data_model = CardListModel(self.cardtypes)  # Example data
        self.listView.setModel(self.data_model)

        # Create and set the delegate for the QListView
        card_delegate = CardTypeDelegate(self.listView)
        self.listView.setItemDelegate(card_delegate)

        self.is_choosing_eliminate = False

        self.can_eliminate_index = None

        self.possible_types = None
    
    
    @Slot(QModelIndex)
    def handle_item_selection(self, index):
        selected_item_data: CardTypeBlock = index.data(Qt.DisplayRole)
        if not selected_item_data.playable:
            return
        if self.is_choosing_eliminate:
            return
        
        if selected_item_data.hand.eraseable and not selected_item_data.need_erased_1:
            self.ui.eliminate.show()
        else:
            self.ui.eliminate.hide()

        selection_model = self.listView.selectionModel()
        self.selected_index = selection_model.currentIndex().row()
        #print("Selected index:", self.selected_index)

    def chooseEliminate(self, slot:PrivateCardPlacer):
        if not self.is_choosing_eliminate:
            self.can_eliminate_index = self.selected_index

            self.ui.submit.hide()
            self.ui.eliminate.setText('選擇')
            cardtypes = []
            
            cardtype = CardTypeBlock()
            cardtype.ui.card.setText(f'不消除')
            cardtype.ui.type.setText('')
            cardtype.ui.value.setText('')
            cardtype.ui.eliminate.setText('')
            cardtypes.append(cardtype)

            current_selected_index = 0
            for card in slot.slots:
                
                if card is not None and \
                   card.getCardNumber() not in self.cardtypes[self.selected_index].hand.card:
                    card_number = card.getCardNumber()
                    cardtype = CardTypeBlock()
                    cardtype.ui.card.setText(f'{card_number}')
                    cardtype.ui.type.setText('')
                    cardtype.ui.value.setText('')
                    cardtype.ui.eliminate.setText('')
                    cardtypes.append(cardtype)

                    if card_number == self.cardtypes[self.selected_index].hand.erased_card:
                        current_selected_index = len(cardtypes) - 1

            data_model = CardListModel(cardtypes)
            self.listView.setModel(data_model)
            self.listView.setCurrentIndex(data_model.index(current_selected_index, 0))

            self.is_choosing_eliminate = True
        else:
            # get selected option
            selection_model = self.listView.selectionModel()
            #print(selection_model.currentIndex().row())
            eliminateNumber = selection_model.currentIndex().data(Qt.DisplayRole).ui.card.text()
            if eliminateNumber == '不消除':
                self.cardtypes[self.can_eliminate_index].hand.erased_card = None
                self.cardtypes[self.can_eliminate_index].ui.eliminate.setText(f'可消除')
            else:
                eliminateNumber = int(eliminateNumber)
                self.cardtypes[self.can_eliminate_index].hand.erased_card = eliminateNumber
                self.cardtypes[self.can_eliminate_index].ui.eliminate.setText(f'消除{eliminateNumber}')

            self.listView.setModel(self.data_model)
            self.listView.setCurrentIndex(self.data_model.index(self.can_eliminate_index, 0))
            self.is_choosing_eliminate = False
            self.ui.submit.show()
            self.ui.eliminate.setText('消除')

    @Slot(list)
    def changeChooseCards(self, cards:list):
        # may be hide by eliminate function
        self.ui.submit.show()
        self.is_choosing_eliminate = False

        possible_types = evaluate_cards(cards)
        #print(possible_types)
        self.ui.eliminate.hide()

        if possible_types == self.possible_types:
            return

        # update directly if there is impossible to have any card type
        if len(possible_types) == 0 or len(possible_types) >= 4:
            self.data_model = CardListModel([])
            self.listView.setModel(self.data_model)
        else:
            self.sendPackage.emit(Package.ChkValid(possible_types))

        self.possible_types = possible_types

        

    def updatePlayableCard(self, replies: list[tuple[Hand, bool, str]]):
        self.cardtypes: list[CardTypeBlock] = []
        for hand, playable, not_playable_reason in replies:
            hand.erased_card = None

            # 1 can also be erased
            if not playable and not_playable_reason == '首家需要打出1' and hand.eraseable:
                hand.erased_card = 1
                cardtype = CardTypeBlock(True, hand, need_erased_1=True)
            else:
                cardtype = CardTypeBlock(playable, hand)
                if not playable:
                    cardtype.setStyleSheet('QLabel{color:#999}')
                    cardtype.ui.cannot_play_reason.setText(not_playable_reason)
                    cardtype.ui.cannot_play_reason.show()
                    cardtype.ui.eliminate.hide()
            self.cardtypes.append(cardtype)

        self.data_model = CardListModel(self.cardtypes)  # Example data
        self.listView.setModel(self.data_model)
        if len(self.cardtypes) == 1:
            self.listView.setCurrentIndex(self.data_model.index(0, 0))
            

    def getSelectedCard(self) -> tuple[int, CardTypeBlock]:
        selection_model = self.listView.selectionModel()
        selected_index = selection_model.currentIndex().row()
        if selected_index == -1:
            return selected_index, None
        return selected_index, self.cardtypes[selected_index]

    def clearChoose(self):
        self.listView.setModel(CardListModel([]))