from uihandler import *
from rooms import *


class Manager:
    def __init__(self, ui: MyWindow, roomhandler: RoomHandler):
        self.ui = ui
        self.rh = roomhandler

    def roomFocusChange(self):
        pass

    def swap(self):
        pass

    def restoreRoom(self):
        pass

    def restoreAllRooms(self):
        pass


class ItemManager(Manager):
    def __init__(self, ui: MyWindow, roomhandler: RoomHandler):
        super().__init__(ui, roomhandler)

    def roomFocusChange(self):
        self.room = self.ui.get_Room()
        self.items = self.rh.getRoomItems(self.room) or []
        self.ui.updateRoomItems(self.items)
        self.focusChange()

    def focusChange(self):
        if self.items:
            self.ritemindex = self.ui.get_RoomItemIndex()
            itemdetails = self.rh.getItemData(self.room, self.ritemindex)
            self.ui.updateItemDetails(itemdetails)

    def updateQuantity(self):
        quantity = self.ui.get_Quantity()
        self.rh.changeItemQuantity(self.room, self.ritemindex, quantity)

    def swap(self):
        newitem = self.ui.get_Item()
        quantity = self.ui.get_Quantity()
        self.rh.swapItem(self.room, self.ritemindex, newitem, quantity)
        self._refreshRoomItems()

    def restoreRoom(self):
        self.rh.restoreRoomItems(self.room)
        self._refreshRoomItems()

    def restoreAllRooms(self):
        self.rh.restoreAllItems()
        self._refreshRoomItems()

    def _refreshRoomItems(self):
        self.items = self.rh.getRoomItems(self.room) or []
        self.ui.updateRoomItems(self.items)
        self.ui.set_RoomItemRow(0)
        self.focusChange()
