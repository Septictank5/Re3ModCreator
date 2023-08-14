from uihandler import *
from tools import *
from itemmanager import Manager


class DoorManager(Manager):
    def __init__(self, ui: MyWindow, roomhandler: RoomHandler):
        super().__init__(ui, roomhandler)

    def roomfocuschange(self):
        self.room = self.ui.get_Room()
        self.doors = self.rh.get_room_doors(self.room) or []
        self.ui.updateRoomDoors(self.doors)

    def targetfocuschange(self, row):
        self.target = self.ui.get_TargetRoom()
        self.targetdoors = self.rh.get_room_doors(self.target) or []
        self.ui.updateTargetDoorsCams(self.targetdoors)


