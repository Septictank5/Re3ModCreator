from uihandler import *
import os
import sys
import shutil


class ItemManager:
    def __init__(self, ui, roomhandler):
        self.ui = ui
        self.rh = roomhandler

    def roomfocuschange(self):
        self.room = self.ui.get_Room()
        self.items = self.rh.get_room_items(self.room) or []
        self.ui.updateRoomItems(self.items)
        self.itemfocuschange()

    def itemfocuschange(self):
        if self.items:
            self.ritemindex = self.ui.get_RoomItemIndex()
            self.ui.updateItemDetails(self.items[self.ritemindex])

    def updatequantity(self):
        quantity = self.ui.get_Quantity()
        self.rh.changeitemquantity(self.room, self.ritemindex, quantity)

    def swap(self):
        newitem = self.ui.get_Item()
        quantity = self.ui.get_Quantity()
        self.rh.swap(self.room, self.ritemindex, newitem, quantity)
        self.refresh_room_items()

    def restoreroom(self):
        self.rh.restore_room_items(self.room)
        self.refresh_room_items()

    def restoreallrooms(self):
        self.rh.restore_all_items()
        self.refresh_room_items()

    def refresh_room_items(self):
        self.items = self.rh.get_room_items(self.room)
        self.ui.updateRoomItems(self.items)
        self.ui.set_RoomItemRow(0)
        self.itemfocuschange()


def main():
    app = QApplication(sys.argv)
    window = MyApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()