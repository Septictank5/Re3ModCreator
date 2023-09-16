from uihandler import *
from rooms import *
from itemmanager import Manager


class DoorManager(Manager):
    def __init__(self, ui: MyWindow, roomhandler: RoomHandler):
        super().__init__(ui, roomhandler)

    def roomFocusChange(self):
        self.room = self.ui.get_Room()
        self.doors = self.rh.getRoomDoors(self.room) or []
        self.ui.updateRoomDoors(self.doors)
        self.focusChange()

    def focusChange(self):
        self.target = self.ui.get_TargetRoom()
        self.target_doors = self.rh.getRoomDoors(self.target)
        self.ui.updateTargetDoors(self.target_doors)

    def swap(self):
        roomnameA = self.ui.get_Room()
        roomnameB = self.ui.get_TargetRoom()
        doorindexA = self.ui.get_DoorIndex()
        doorindexB = self.ui.get_TargetDoorIndex()
        self.rh.changeDoor(roomnameA, doorindexA, roomnameB, doorindexB)
        self.rh.changeDoor(roomnameB, doorindexB, roomnameA, doorindexA)
        self._refreshRoomDoors()

    def restoreRoom(self):
        self.rh.restoreRoomDoors(self.room)
        self._refreshRoomDoors()

    def restoreAllRooms(self):
        self.rh.restoreAllDoors()
        self._refreshRoomDoors()

    def _refreshRoomDoors(self):
        self.doors = self.rh.getRoomDoors(self.room) or []
        self.target_doors = self.rh.getRoomDoors(self.target) or []
        self.ui.updateRoomDoors(self.doors)
        self.ui.updateTargetDoors(self.target_doors)
        self.ui.set_RoomDoorRow(0)
        self.ui.set_TargetDoorRow(0)
        self.focusChange()
