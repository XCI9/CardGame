from PySide6.QtWidgets import (QGraphicsScene,
                               QGraphicsLineItem,
                               QGraphicsEllipseItem,
                               QGraphicsTextItem,
                               QGraphicsItemGroup,
                               QGraphicsPixmapItem,
                               QGraphicsRectItem,
                               QGraphicsItem)
from PySide6.QtGui import QColor, QPen, QPixmap, QImage, QBrush, QFont
from PySide6.QtCore import Qt, Signal, QEvent
import numpy as np

class CardNumber(QGraphicsTextItem):
    def __init__(self, number, parent=None):
        super().__init__(parent)
        self.number = number
        self.setPlainText(f'{number}')

PADDING = 5

class Card(QGraphicsItemGroup):
    def __init__(self, x, y, number, parent=None):
        super().__init__(parent)

        self.original_x = x
        self.original_y = y
        self.setPos(x, y)

        self.setHandlesChildEvents(False)
        self.setAcceptHoverEvents(True)
        self.is_selected = False

        self.block_size = 10
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.card = QGraphicsRectItem(0, 0, self.block_size*2, self.block_size*20, self)
        self.number = CardNumber(number, self)

        self.addToGroup(self.card)
        self.addToGroup(self.number)

        self.is_mouse_press = False

    def getCardNumber(self):
        return self.number.number

    def setSlotManager(self, slot: "PrivateCardPlacer"):
        self.slot = slot

    def changePos(self, x, y):
        self.original_x = x
        self.original_y = y
        self.setPos(x, y)

    def changeX(self, x):
        self.original_x = x
        self.setX(x)

    def hoverEnterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)  # Change the cursor

        if not self.is_selected:
            self.setY(self.original_y-20)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if not self.is_selected:
            self.setY(self.original_y)


        self.setCursor(Qt.ArrowCursor)  # Change the cursor back
        super().hoverLeaveEvent(event)

    def mouseMoveEvent(self, event) -> None:
        current_slot = self.slot.getSlotIndexByX(int(self.x()))
        original_slot = self.slot.getSlotIndexByX(int(self.original_x))
        self.slot.insertCard(original_slot, current_slot)
        return super().mouseMoveEvent(event)

    def toggle_selection(self):
        if not self.is_mouse_press:
            return
        if self.x() == self.original_x: # not moving
            self.is_selected = not self.is_selected
        else:
            current_slot = self.slot.getSlotIndexByX(int(self.x()))
            original_slot = self.slot.getSlotIndexByX(int(self.original_x))
            self.slot.insertCard(original_slot, current_slot)
            self.setX(self.slot.getSlotX(current_slot))

        self.is_mouse_press = False

        if self.is_selected:
            self.setY(self.original_y-50)
        else:
            self.setY(self.original_y-20)

    def mousePressEvent(self, event) -> None:
        #print('press')
        self.is_mouse_press = True
        return super().mousePressEvent(event)

class PublicCardPlacer:
    def __init__(self, slot_count=31):
        self.slot_count = slot_count
        self.block_size = 10
        self.gap = int(2.5 * self.block_size)

        self.current_card_count = 0

        self.slots: list[Card] = [None] * slot_count

    def makeCard(self, number):
        group = QGraphicsItemGroup()
        card = QGraphicsRectItem(0, 0, self.block_size*2, self.block_size*20, group)
        number = CardNumber(number, group)

        group.addToGroup(card)
        group.addToGroup(number)
        group.setY(100)

        return group

    def putCard(self, canva:QGraphicsScene, number:int):
        x = self.getSlotX(self.current_card_count)
        card = self.makeCard(number)    
        card.setX(x)
        canva.addItem(card)
        self.current_card_count += 1
                
    def getSlotX(self, index):
        return PADDING + index * self.gap

class PrivateCardPlacer:
    def __init__(self, slot_count):
        self.slot_count = slot_count
        self.block_size = 10
        self.gap = int(2.5 * self.block_size)

        self.slots: list[Card] = [None] * slot_count

    def setCard(self, index, card: Card= None):
        self.slots[index] = card
        if card is not None:
            card.setX(self.getSlotX(index))
    
    def swapCard(self, index1:int, index2:int):
        #print(f'swap {index1} {index2}')
        self.slots[index1], self.slots[index2] = self.slots[index2], self.slots[index1]
        
        if self.slots[index2] is not None:
            self.slots[index2].changeX(self.getSlotX(index2))
        if self.slots[index1] is not None:
            self.slots[index1].changeX(self.getSlotX(index1))
    
    def insertCard(self, fromIndex:int, toIndex:int):
        if self.slots[toIndex] is None:
            self.swapCard(fromIndex, toIndex)
            return
        
        if fromIndex > toIndex:
            for i in range(fromIndex, toIndex, -1):
                self.swapCard(i, i-1)
        else:
            for i in range(fromIndex, toIndex):
                self.swapCard(i, i+1)

    def getSlotIndexByNumber(self, target_card):
        for i, slot in enumerate(self.slots):
            if slot is not None and slot.getCardNumber() == target_card:
                return i
                
    def getSlotX(self, index):
        return PADDING + index * self.gap
    
    def getSlotIndexByX(self, x):
        x -= PADDING
        
        dist_to_last_slot = x % self.gap
        slot = x // self.gap

        if dist_to_last_slot > self.gap/2:
            slot += 1

        if slot < 0:
            return 0
        elif slot >= self.slot_count:
            return self.slot_count - 1

        return slot


class Canva(QGraphicsScene):
    clicked = Signal(int, int)
    chooseCardsChanged = Signal(list)

    def __init__(self, parent=None):
        super().__init__()

        self.block_size = 10
        self.gap = int(2.5 * self.block_size)

        # anchor block to make (0, 0) on left top
        self.block = QGraphicsRectItem(0, 0, 1, 1)
        self.addItem(self.block)

        number = [i for i in range(1, 32)]

        self.played_card = PublicCardPlacer()

        self.slot = PrivateCardPlacer(11)
        
    def initCard(self, numbers:list):
        for i, n in enumerate(numbers):
            card = Card(PADDING + i* self.gap, 350, n)#Card(PADDING + i* self.gap , 441, n)
            card.setSlotManager(self.slot)
            self.addItem(card)
            self.slot.setCard(i, card)

    def playCard(self, number):
        self.played_card.putCard(self, number)

    def removeCard(self, target_card):
        i = self.slot.getSlotIndexByNumber(target_card)
        self.removeItem(self.slot.slots[i])
        self.slot.slots[i] = None


    def removeCards(self, target_cards):
        for i in target_cards:
            self.removeCard(i)

    def mouseReleaseEvent(self, event):
        items = self.items(event.scenePos())
        for item in items:
            if isinstance(item, Card):
                item.toggle_selection()

        selected_card = []
        for card in self.slot.slots:
            if card is not None and card.is_selected:
                selected_card.append(card.number.number)
        self.chooseCardsChanged.emit(selected_card)
                
        super().mouseReleaseEvent(event)
