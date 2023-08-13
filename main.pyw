from uihandler import *
import os
import sys
import shutil


class MyApp:
    def __init__(self):
        self.ui = MyWindow()
        self.doconnections()
        self.startup()

    def doconnections(self):
        self.ui.connectOpenDir(self.choosedirectory)
        self.ui.connectCreateMod(self.create_mod)
        self.ui.connectOpenMod(self.open_mod)
        self.ui.connectRestoreRoomItems(self.restoreroomitems)
        self.ui.connectRestoreAllRoomItems(self.restoreallroomitems)
        self.ui.connectRoomChange_Items(self.roomfocuschange_items)
        self.ui.connectRoomChange_Doors(self.roomfocuschange_doors)
        self.ui.connectItemChange(self.itemfocuschange)
        self.ui.connectQuantityUpdate(self.updatequantity)
        self.ui.connectSwap(self.swapitem)
        self.ui.connectVerify(self.verify)

    def choosedirectory(self):
        chosenfolder = QFileDialog.getExistingDirectory() + '/'
        if self.defaultfolder == chosenfolder:
            return
        self.defaultfolder = chosenfolder
        if not os.path.exists(self.defaultfolder + 'Mods/'):
            os.mkdir(self.defaultfolder + 'Mods/')
        defaultloc = [f'defaultrdtdir={self.defaultfolder}\n']
        newworkingfolder = self.defaultfolder + 'Mods/' + self.modname + '/'
        if not os.path.exists(newworkingfolder):
            os.mkdir(newworkingfolder)
        defaultloc.append(f'workingdir={newworkingfolder}\n')
        with open('config.ini', 'r+') as file:
            file.writelines(defaultloc)
        self.copy_files(self.workingfolder, newworkingfolder)
        self.workingfolder = newworkingfolder

    def startup(self):
        with open('config.ini', 'r+') as file:
            sessiondata = file.read()

            if 'defaultrdtdir=' not in sessiondata:
                self.defaultfolder = QFileDialog.getExistingDirectory() + '/'
                if not os.path.exists(self.defaultfolder + 'Mods/'):
                    os.mkdir(self.defaultfolder + 'Mods/')
                file.writelines([f'defaultrdtdir={self.defaultfolder}\n'])

            else:
                index = sessiondata.index('defaultrdtdir=') + len('defaultrdtdir=')
                endex = sessiondata[index:].index('\n')
                self.defaultfolder = sessiondata[index:index + endex]

            if 'workingdir=' in sessiondata:
                index = sessiondata.index('workingdir=') + len('workingdir=')
                endex = sessiondata[index:].index('\n')
                self.workingfolder = sessiondata[index:index + endex]
                self.validate_files()

            else:
                if not self.get_modname():
                    sys.exit(0)
                file.write(f'workingdir={self.workingfolder}\n')
            self.modname = self.workingfolder.split('/')[-2]
            self.ui.updateModTitle(self.modname)
            self.fm = FileManager()
            self.fm.progressupdate.connect(self.ui.updateProgress)
            self.fm.update_directorys(self.defaultfolder, self.workingfolder)
            self.ui.initUI(self.fm.get_room_names(), self.fm.get_all_items())

    def roomfocuschange_items(self, row):
        self.room = self.ui.get_Room()
        self.items = self.fm.get_room_items(self.room) or []
        self.ui.updateRoomItems(self.items)
        self.itemfocuschange()

    def roomfocuschange_doors(self, row):
        pass

    def itemfocuschange(self):
        if self.items:
            self.ritemindex = self.ui.get_RoomItemIndex()
            self.ui.updateItemDetails(self.items[self.ritemindex])

    def updatequantity(self):
        quantity = self.ui.get_Quantity()
        self.fm.changeitemquantity(self.room, self.ritemindex, quantity)

    def swapitem(self):
        newitem = self.ui.get_Item()
        quantity = self.ui.get_Quantity()
        self.fm.swap(self.room, self.ritemindex, newitem, quantity)
        self.refresh_room_items()

    def restoreroomitems(self):
        self.fm.restore_room_items(self.room)
        self.refresh_room_items()

    def restoreallroomitems(self):
        self.fm.restore_all_items()
        self.refresh_room_items()

    def refresh_room_items(self):
        self.items = self.fm.get_room_items(self.room)
        self.ui.updateRoomItems(self.items)
        self.ui.set_RoomItemRow(0)
        self.itemfocuschange()

    def create_mod(self):
        if self.get_modname():
            self.updatemoddetails()

    def get_modname(self):
        modname, ok = QInputDialog.getText(self.ui, 'QInputDialog.getText()', 'Enter Mod Name: ', QLineEdit.Normal)
        if not ok:
            return False
        self.modname = modname
        self.workingfolder = self.defaultfolder + 'Mods/' + self.modname + '/'
        if not os.path.exists(self.workingfolder):
            os.mkdir(self.workingfolder)
        self.copy_files(self.defaultfolder, self.workingfolder)
        return True

    def updatemoddetails(self):
        self.update_config_workingdir()
        self.fm.update_directory(self.workingfolder)
        self.ui.updateModTitle(self.modname)
        self.ui.reset_rows()

    def open_mod(self):
        folder = QFileDialog.getExistingDirectory() + '/'
        if folder != '/':
            self.workingfolder = folder
            self.modname = self.workingfolder.split('/')[-2]
            self.updatemoddetails()

    def update_config_workingdir(self):
        linenumber = None
        with open('config.ini', 'r+') as file:
            data = file.readlines()
        for index, string in enumerate(data):
            if string.startswith(f'workingdir='):
                linenumber = index
                break
        data[linenumber] = f'workingdir={self.workingfolder}\n'
        with open('config.ini', 'w') as file:
            file.writelines(data)

    def copy_files(self, src, dst):
        files = [f for f in os.listdir(src) if os.path.isfile(src + f)
                 and f.endswith('.RDT')]
        for entry in files:
            shutil.copy(src + entry, dst + entry)

    def validate_files(self):
        if os.path.exists(self.workingfolder):
            for key in roomnames.keys():
                filename = self.workingfolder + key + '.RDT'
                if not os.path.isfile(filename):
                    shutil.copy(self.defaultfolder + key + '.RDT', filename)

        else:
            os.mkdir(self.workingfolder)
            self.copy_files(self.defaultfolder, self.workingfolder)

    def verify(self):
        completable = False
        self.keydata = get_keydata()
        keyitems, combokeys = get_keyinfo()
        musthaves, optionals = get_checklists()
        rooms = ['Warehouse Save Room', 'Warehouse']
        collected = []
        unhandled = []
        for room in rooms:
            items = [f.typename for f in self.fm.get_room_items(room) or []]
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
                    rooms, unhandled = self.keydatacheck(item, rooms, unhandled)
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
                        rooms, unhandled = self.keydatacheck(key, rooms, unhandled)
            for key in popitems:
                combokeys.pop(key)
            rooms, unhandled = self.manageunhandled(rooms, unhandled)
        if 'Escape Elevator' in rooms:
            completable = True
        self.ui.verifdialog.display(completable, collected, musthaves, optionals)

    def manageunhandled(self, rooms: list[str], unhandled: list[str]):
        popitems = []
        for item in unhandled:
            data = self.keydata[item]
            if data['access'] in rooms:
                rooms.extend(data['unlocks'])
                popitems.append(item)
        for item in popitems:
            unhandled.remove(item)
        return rooms, unhandled

    def keydatacheck(self, item, rooms: list[str], unhandled: list[str]):
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