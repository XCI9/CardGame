import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QAbstractItemView, QStyledItemDelegate, QVBoxLayout, QListView, QHBoxLayout, QStyle
from PySide6.QtCore import Qt, Signal, QAbstractListModel, QModelIndex, QSize, Slot, QPoint
from PySide6.QtGui import QStandardItem, QStandardItemModel, QPixmap, QRegion, QPainter
from mainwindow_ui import Ui_MainWindow

from cardtype_ui import Ui_Form as CardTypeForm
from canva import PrivateCardPlacer
from game import *
from copy import deepcopy

class CardTypeBlock(QWidget):
    def __init__(self, playable = True, hand:Hand = None, parent=None):
        super().__init__(parent)

        self.eliminate_card = None
        self.hand = hand
        self.playable = playable
        self.ui = CardTypeForm()
        self.ui.setupUi(self)
        self.ui.cannot_play_reason.hide()

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
                    self.ui.value.setText(f'附帶None')
                else:
                    self.ui.value.setText(f'{hand.value}')
            self.ui.eliminate.setText('可消除' if hand.eraseable else '')


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
                #pic = QPixmap( option.rect.width(), option.rect.height() )
                #widget.setGeometry( option.rect )
                #offset = self._parent.mapTo(self._mainWindow, QPoint(0,0))
                #widget.render(painter, option.rect.topLeft())
                #widget.render(painter, option.rect, QRegion())
                #painter.setRenderHint(QPainter.Antialiasing)  
                #painter.setRenderHint(QPainter.TextAntialiasing)         
                #painter.drawPixmap( option.rect, pic )
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

class HandChooser:
    enableEliminate = Signal()
    disableElimate = Signal()
    def __init__(self, ui: Ui_MainWindow, board: TableClassic):
        self.ui = ui
        self.listView = ui.cardChooser
        self.board = board

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
    
    
    @Slot(QModelIndex)
    def handle_item_selection(self, index):
        selected_item_data: CardTypeBlock = index.data(Qt.DisplayRole)
        if not selected_item_data.playable:
            return
        if self.is_choosing_eliminate:
            return
        
        if selected_item_data.hand.eraseable:
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
                card_number = card.getCardNumber()
                if card is not None and \
                   card_number not in self.cardtypes[self.selected_index].hand.card:
                    cardtype = CardTypeBlock()
                    cardtype.ui.card.setText(f'{card_number}')
                    cardtype.ui.type.setText('')
                    cardtype.ui.value.setText('')
                    cardtype.ui.eliminate.setText('')
                    cardtypes.append(cardtype)

                    if card_number == self.cardtypes[self.selected_index].eliminate_card:
                        current_selected_index = len(cardtypes) - 1

            data_model = CardListModel(cardtypes)  # Example data
            self.listView.setModel(data_model)
            self.listView.setCurrentIndex(data_model.index(current_selected_index, 0))

            self.is_choosing_eliminate = True
        else:
            #get selected option
            selection_model = self.listView.selectionModel()
            #print(selection_model.currentIndex().row())
            eliminateNumber = selection_model.currentIndex().data(Qt.DisplayRole).ui.card.text()
            if eliminateNumber == '不消除':
                self.cardtypes[self.can_eliminate_index].eliminate_card = None
                self.cardtypes[self.can_eliminate_index].ui.eliminate.setText(f'可消除')
            else:
                eliminateNumber = int(eliminateNumber)
                self.cardtypes[self.can_eliminate_index].eliminate_card = eliminateNumber
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

        self.cardtypes = []
        for possible_type in possible_types:
            playable, not_playable_reason = self.board.is_playable_hand(possible_type)
            #playable = False

            
            cardtype = CardTypeBlock(playable, possible_type)
            if not playable:
                cardtype.setStyleSheet('QLabel{color:#999}')
                cardtype.ui.cannot_play_reason.setText(not_playable_reason)
                cardtype.ui.cannot_play_reason.show()
            self.cardtypes.append(cardtype)

        self.data_model = CardListModel(self.cardtypes)  # Example data
        self.listView.setModel(self.data_model)
        self.ui.eliminate.hide()

    def getSelectedCard(self) -> tuple[int, CardTypeBlock]:
        selection_model = self.listView.selectionModel()
        selected_index = selection_model.currentIndex().row()
        if selected_index == -1:
            return selected_index, None
        return selected_index, self.cardtypes[selected_index]

    def clearChoose(self):
        self.listView.setModel(CardListModel([]))