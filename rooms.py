import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from trackers import Tracker
from codeviewer.opcodes import *
import json


class Room:
    def __init__(self, name: str, filename: str):
        self.name = name
        self.filename = filename

    def getDoors(self):
        with open(datapy.workingpath + 'roomdoors.json', 'r') as file:
            doorentries = json.load(file)[self.name]['doors']

        return [f for f in doorentries]

    def getItems(self):
        with open(datapy.workingpath + 'roomdoors.json', 'r') as file:
            itementries = json.load(file)[self.name]['items']

        return [f for f in itementries]

    def getItemData(self, index):
        with open(datapy.workingpath + 'roomdoors.json', 'r') as file:
            iteminfo = json.load(file)[self.name]['items'][index]

        size = I67OP.SIZE if iteminfo['optype'] == 0x67 else I68OP.SIZE
        with open(datapy.workingpath + self.filename, 'rb') as file:
            return file.read()[iteminfo['indices'][0]:iteminfo['indices'][0] + size]

    def write(self):
        with open(datapy.workingpath + 'roomdoors.json', 'r') as file:
            datadict = json.load(file)[self.name]

        with open(datapy.workingpath + self.filename, 'rb') as file:
            data = bytearray(file.read())

        for door in datadict['doors']:
            OP = D61OP if door['optype'] == 0x61 else D62OP
            xpos = struct.pack('<h', door['nxpos'])
            ypos = struct.pack('<h', door['nypos'])
            zpos = struct.pack('<h', door['nzpos'])
            ydir = struct.pack('<h', door['nydir'])
            for offset in door['indices']:
                data[offset + OP.NXPOS:offset + OP.NXPOS + 2] = xpos
                data[offset + OP.NYPOS:offset + OP.NYPOS + 2] = ypos
                data[offset + OP.NZPOS:offset + OP.NZPOS + 2] = zpos
                data[offset + OP.NYDIR:offset + OP.NYDIR + 2] = ydir
                data[offset + OP.NROOM] = door['nroom']
                data[offset + OP.NSTAGE] = door['nstage']
                data[offset + OP.NNFLOOR] = door['nnfloor']
                data[offset + OP.NCUT] = door['ncut']

            for offset in door['resets']:
                data[offset + 4:offset + 6] = xpos
                data[offset + 6:offset + 8] = ypos
                data[offset + 8: offset + 10] = zpos

        for item in datadict['items']:
            OP = I67OP if item['optype'] == 0x67 else I68OP
            for offset in item['indices']:
                data[offset + OP.ID:offset + OP.ID + 2] = struct.pack('<h', item['id'])
                data[offset + OP.AMOUNT:offset + OP.AMOUNT + 2] = struct.pack('<h', item['amount'])

        with open(datapy.workingpath + self.filename, 'wb') as file:
            file.write(data)


class RoomHandler(QObject):
    progressupdate = pyqtSignal(int)

    def __init__(self, tracker: Tracker):
        super().__init__()
        self.tracker = tracker

    def _findRoom(self, name: str):
        for room in self.rooms:
            if room.name == name:
                return room

    def _writeRoomData(self, roomname):
        room = self._findRoom(roomname)
        room.write()

    def _writeAllRoomsData(self):
        for room in self.rooms:
            room.write()

    def updateDirectorys(self):
        self.rooms = []
        QApplication.processEvents()
        for key, value in datapy.roomnames.items():
            self.progressupdate.emit(len(self.rooms))
            self.rooms.append(Room(value, key + '.RDT'))

    def restoreRoomItems(self, roomname: str):
        self.tracker.resetRoomItems(roomname)
        self._writeAllRoomsData()

    def restoreRoomDoors(self, roomname: str):
        self.tracker.resetRoomDoors(roomname)
        self._writeAllRoomsData()

    def restoreAllItems(self):
        self.tracker.resetAllItems()
        self._writeAllRoomsData()

    def restoreAllDoors(self):
        self.tracker.resetAllDoors()
        self._writeAllRoomsData()

    def getRoomItems(self, roomname: str):
        room = self._findRoom(roomname)
        items = room.getItems()
        if len(items) > 0:
            return items

    def getItemData(self, roomname, index):
        room = self._findRoom(roomname)
        return room.getItemData(index)

    def getRoomDoors(self, roomname: str):
        room = self._findRoom(roomname)
        doors = room.getDoors()
        if len(doors) > 0:
            return doors

    def changeItemQuantity(self, roomname: str, itemindex: int, quantity: int):
        self.tracker.updateItemQuantity(roomname, itemindex, quantity)
        self._writeRoomData(roomname)

    def swapItem(self, roomname: str, itemindex: int, newitem: str, quantity: int):
        self.tracker.updateItem(roomname, itemindex, newitem, quantity)
        self._writeRoomData(roomname)

    def changeDoor(self, roomname, doorindex, targetroom, targetdoorindex):
        self.tracker.retargetDoor(roomname, doorindex, targetroom, targetdoorindex)
        self._writeRoomData(roomname)