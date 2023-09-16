from uihandler import *
import sys
import shutil
import os
from itemmanager import ItemManager
from doormanager import DoorManager
from rooms import *


class MyApp:
    def __init__(self):
        self.ui = MyWindow()
        self.startup()
        self.localConnections()
        self.managerConnections()
        self.roomFocusChange(0)

    def localConnections(self):
        self.ui.connectOpenDir(self.chooseDirectory)
        self.ui.connectCreateMod(self.createMod)
        self.ui.connectOpenMod(self.openMod)
        self.ui.connectRestoreRoom(self.restoreRoom)
        self.ui.connectRestoreAllRooms(self.restoreAllRooms)
        self.ui.connectRoomChange(self.roomFocusChange)
        self.ui.connectFocusChange(self.generalFocusChange)
        self.ui.connectSwap(self.swap)
        self.ui.connectVerify(self.verify)
        self.ui.connectTabChanged(self.changeManager)

    def managerConnections(self):
        self.ui.connectQuantityUpdate(self.managerlist[0].updateQuantity)

    def roomFocusChange(self, row):
        self.manager.roomFocusChange()

    def generalFocusChange(self, row):
        self.manager.focusChange()

    def swap(self):
        self.manager.swap()

    def restoreRoom(self):
        self.manager.restoreRoom()

    def restoreAllRooms(self):
        self.manager.restoreAllRooms()

    def changeManager(self, value):
        self.manager = self.managerlist[value]
        self.manager.roomFocusChange()

    def chooseDirectory(self):
        chosenfolder = QFileDialog.getExistingDirectory() + '/'
        if datapy.defaultpath == chosenfolder:
            return
        datapy.defaultpath = chosenfolder
        if not os.path.exists(datapy.defaultpath + 'Mods/'):
            os.mkdir(datapy.defaultpath + 'Mods/')
        defaultloc = [f'defaultrdtdir={datapy.defaultpath}\n']
        newworkingfolder = datapy.defaultpath + 'Mods/' + self.modname + '/'
        if not os.path.exists(newworkingfolder):
            os.mkdir(newworkingfolder)
        defaultloc.append(f'workingdir={newworkingfolder}\n')
        with open('config.ini', 'r+') as file:
            file.writelines(defaultloc)
        self.copyFiles(datapy.workingpath, newworkingfolder)
        datapy.workingpath = newworkingfolder

    def startup(self):
        mode = 'r+' if os.path.exists('config.ini') else 'w+'
        with open('config.ini', mode) as file:
            file.seek(0)
            sessiondata = file.read()

            if 'defaultrdtdir=' not in sessiondata:
                datapy.defaultpath = QFileDialog.getExistingDirectory() + '/'
                if not os.path.exists(datapy.defaultpath + 'Mods/'):
                    os.mkdir(datapy.defaultpath + 'Mods/')
                file.writelines([f'defaultrdtdir={datapy.defaultpath}\n'])

            else:
                index = sessiondata.index('defaultrdtdir=') + len('defaultrdtdir=')
                endex = sessiondata[index:].index('\n')
                datapy.defaultpath = sessiondata[index:index + endex]

            if 'workingdir=' in sessiondata:
                index = sessiondata.index('workingdir=') + len('workingdir=')
                endex = sessiondata[index:].index('\n')
                datapy.workingpath = sessiondata[index:index + endex]
                self.validateFiles()

            else:
                if not self.getModName():
                    sys.exit(0)
                file.write(f'workingdir={datapy.workingpath}\n')
            self.tracker = Tracker()
            self.rh = RoomHandler(self.tracker)
            self.managerlist = [ItemManager(self.ui, self.rh), DoorManager(self.ui, self.rh)]
            self.manager = self.managerlist[0]
            self.modname = datapy.workingpath.split('/')[-2]
            self.ui.updateModTitle(self.modname)
            self.rh.progressupdate.connect(self.ui.updateProgress)
            self.rh.updateDirectorys()
            self.ui.initUI(list(datapy.roomnames.values()), datapy.itemnames)

    def createMod(self):
        if self.getModName():
            self.updateModDetails()

    def getModName(self):
        modname, ok = QInputDialog.getText(self.ui, 'QInputDialog.getText()', 'Enter Mod Name: ', QLineEdit.Normal)
        if not ok:
            return False
        self.modname = modname
        datapy.workingpath = datapy.defaultpath + 'Mods/' + self.modname + '/'
        if not os.path.exists(datapy.workingpath):
            os.mkdir(datapy.workingpath)
        self.copyFiles(datapy.defaultpath, datapy.workingpath)
        shutil.copy('jsonfiles/roomdoors.json', datapy.workingpath + 'roomdoors.json')
        return True

    def updateModDetails(self):
        self.updateConfigWorkingDir()
        self.rh.updateDirectorys()
        self.ui.updateModTitle(self.modname)
        self.ui.reset_rows()
        self.tracker.setModFile()

    def openMod(self):
        folder = QFileDialog.getExistingDirectory() + '/'
        if folder != '/':
            datapy.workingpath = folder
            self.modname = datapy.workingpath.split('/')[-2]
            self.updateModDetails()

    def updateConfigWorkingDir(self):
        linenumber = None
        with open('config.ini', 'r+') as file:
            data = file.readlines()
        for index, string in enumerate(data):
            if string.startswith(f'workingdir='):
                linenumber = index
                break
        data[linenumber] = f'workingdir={datapy.workingpath}\n'
        with open('config.ini', 'w') as file:
            file.writelines(data)

    def copyFiles(self, src, dst):
        files = [f for f in os.listdir(src) if os.path.isfile(src + f)
                 and f.endswith('.RDT')]
        for entry in files:
            shutil.copy(src + entry, dst + entry)

    def validateFiles(self):
        if os.path.exists(datapy.workingpath):
            tocheck = [f for f in os.listdir(datapy.defaultpath) if f.endswith('.RDT')]
            for file in tocheck:
                if not os.path.exists(datapy.workingpath + file):
                    shutil.copy(datapy.defaultpath + file, datapy.workingpath + file)

        else:
            os.mkdir(datapy.workingpath)
            self.copyFiles(datapy.defaultpath, datapy.workingpath)
        if not os.path.exists(datapy.workingpath + 'roomdoors.json'):
            shutil.copy('jsonfiles/roomdoors.json', datapy.workingpath + 'roomdoors.json')

    def verify(self):
        completable = False
        self.keydata = get_keydata()
        keyitems, combokeys = get_keyinfo()
        musthaves, optionals = get_checklists()
        rooms = ['Warehouse Save Room', 'Warehouse']
        collected = []
        unhandled = []
        for room in rooms:
            items = [f.itemname for f in self.rh.getRoomItems(room) or []]
            if items is None:
                continue
            for item in items:
                if item not in keyitems:
                    continue
                if item in collected:
                    collected.append(item)
                    continue
                collected.append(item)
                if item in musthaves:
                    musthaves.remove(item)
                for index, entry in enumerate(optionals):
                    if item == entry[0]:
                        optionals.pop(index)
                        break
                if item in self.keydata.keys():
                    rooms, unhandled = self.keyDataCheck(item, rooms, unhandled)
                    continue
                for entry in combokeys.values():
                    if item in entry:
                        entry.remove(item)
                        break
            popitems = []
            for key, value in combokeys.items():
                if len(value) == 0:
                    popitems.append(key)
                    if key in musthaves:
                        musthaves.remove(key)
                    for entry in combokeys.values():
                        if key in entry:
                            entry.remove(key)
                            break
                    if key in self.keydata.keys():
                        rooms, unhandled = self.keyDataCheck(key, rooms, unhandled)
            for key in popitems:
                combokeys.pop(key)
            rooms, unhandled = self.manageUnhandled(rooms, unhandled)
        if 'Escape Elevator' in rooms:
            completable = True
        self.ui.verifdialog.display(completable, collected, musthaves, optionals)

    def manageUnhandled(self, rooms: list[str], unhandled: list[str]):
        popitems = []
        for item in unhandled:
            data = self.keydata[item]
            if data['access'] in rooms:
                rooms.extend(data['unlocks'])
                popitems.append(item)
        for item in popitems:
            unhandled.remove(item)
        return rooms, unhandled

    def keyDataCheck(self, item, rooms: list[str], unhandled: list[str]):
        data = self.keydata[item]
        if data['access'] in rooms:
            rooms.extend(data['unlocks'])
        else:
            unhandled.append(item)
        return rooms, unhandled


def main():
    app = QApplication(sys.argv)
    window = MyApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()