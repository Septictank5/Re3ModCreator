import datapy
import json
from copy import deepcopy
import time


class TimeTest:
    def __init__(self):
        self.time = time.time()
        print('tester initialized')

    def testTime(self):
        print(time.time() - self.time)
        self.time = time.time()


class Tracker:
    def __init__(self):
        self.ogfile = 'jsonfiles/roomdoors.json'
        with open(self.ogfile, 'r') as file:
            self.ogdict = json.load(file)
        self.setModFile()

    def _loadModDict(self):
        with open(self.modfile, 'r') as file:
            self.moddict = json.load(file)

    def _validateOgDict(self):
        with open('jsonfiles/roomdoors.json', 'r') as file:
            fresh = json.load(file)

        print(fresh == self.ogdict)

    def _dump(self):
        with open(self.modfile, 'w') as file:
            json.dump(self.moddict, file, indent=4)

    def _handleSameFlag(self, room, itemdict):
        flag = itemdict['flag']
        if flag in datapy.roomitemflags:
            for entry in datapy.roomitemflags[flag]:
                if room not in entry:
                    continue
                for otherroom in entry:
                    if otherroom == room:
                        continue
                    for item in self.moddict[otherroom]['items']:
                        if item['flag'] == flag:
                            item['name'] = itemdict['name']
                            item['amount'] = itemdict['amount']
                            item['id'] = itemdict['id']

    def _disconnectRoom(self, room, doorindex):
        doorinfo = self.moddict[room]['doors'][doorindex]
        target = doorinfo['curtarget']
        if not self._handleUniqueDCTargeting(target, doorinfo):
            for door in self.moddict[target]['doors']:
                if door['curtarget'] == room:
                    door['curtarget'] = 'NOTSET'

    def _handleUniqueDCTargeting(self, target, doorinfo):
        if target == 'Basement Alley' and doorinfo['ncut'] == 6:
            self.moddict[target]['doors'][1]['curtarget'] = 'NOTSET'
            return True
        elif target == 'Warehouse Street' and doorinfo['ncut'] == 13:
            self.moddict[target]['doors'][2]['curtarget'] = 'NOTSET'
            return True

    def setModFile(self):
        self.modfile = datapy.workingpath + 'roomdoors.json'
        self._loadModDict()

    def updateItem(self, room, index, item, quantity):
        itemdict = self.moddict[room]['items'][index]
        itemid = datapy.itemnames.index(item)
        itemdict['name'] = item
        itemdict['id'] = itemid
        itemdict['amount'] = quantity
        self._handleSameFlag(room, itemdict)
        self._dump()

    def updateItemQuantity(self, room, index, quantity):
        itemdict = self.moddict[room]['items'][index]
        itemdict['amount'] = quantity
        self._handleSameFlag(room, itemdict)
        self._dump()

    def resetRoomDoors(self, room: str):
        self.moddict[room]['doors'] = deepcopy(self.ogdict[room]['doors'])
        self._dump()

    def resetAllDoors(self):
        for entry in self.moddict.keys():
            self.moddict[entry]['doors'] = deepcopy(self.ogdict[entry]['doors'])
        self._dump()

    def resetAllItems(self):
        for entry in self.moddict.keys():
            self.moddict[entry]['items'] = deepcopy(self.ogdict[entry]['items'])
        self._dump()

    def resetRoomItems(self, room: str):
        self.moddict[room]['items'] = deepcopy(self.ogdict[room]['items'])
        self._dump()

    def retargetDoor(self, room: str, doorindex: int, targetroom: str, targetindex: int):
        properdictinfo = {}
        self._disconnectRoom(room, doorindex)
        roomwithinfo = self.ogdict[targetroom]['doors'][targetindex]['ogtarget']
        for door in self.ogdict[roomwithinfo]['doors']:
            if door['ogtarget'] == targetroom:
                properdictinfo = deepcopy(door)
        if not properdictinfo:
            return
        door = self.moddict[room]['doors'][doorindex]
        door['curtarget'] = targetroom
        door['nroom'] = properdictinfo['nroom']
        door['nstage'] = properdictinfo['nstage']
        door['ncut'] = properdictinfo['ncut']
        door['nxpos'] = properdictinfo['nxpos']
        door['nypos'] = properdictinfo['nypos']
        door['nzpos'] = properdictinfo['nzpos']
        door['nydir'] = properdictinfo['nydir']
        door['nnfloor'] = properdictinfo['nnfloor']
        self._dump()
