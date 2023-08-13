import struct
from data import *
from codeviewer.opcodes import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from UI.VerificationDialog import Ui_Dialog


class VerifyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        self.view = Ui_Dialog()
        self.view.setupUi(self)
        self.infodisplay = self.view.infodisplay

    def display(self, completable: bool, collected: list[str], musthaves: list[str], optionals: list[str]):
        self.musthaves = musthaves
        self.optionals = optionals
        self.info = []
        for index, item in enumerate(collected):
            times_appeared = collected.count(item)
            if times_appeared > 1:
                self.info.append([item, times_appeared])
        self.collected = []
        [self.collected.append(s) for s in self.info if s not in self.collected]
        self.setFixedSize(800, (len(musthaves) + len(optionals) + len(self.collected)) * 20 + 40)
        self.completable = completable
        self.update()
        self.show()

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        red = QColor(Qt.red)
        yellow = QColor(230, 120, 0)
        green = QColor(Qt.darkGreen)
        painter.setPen(green) if self.completable else painter.setPen(red)
        point = QPoint(self.width() // 2 - len(f'COMPLETABLE: {self.completable}') - 50, 20)
        painter.drawText(point,  f'COMPLETABLE: {self.completable}')
        entries = 1
        for text in self.musthaves:
            painter.setPen(red)
            point = QPoint(20, 20 + entries * 20)
            painter.drawText(point, text + ': Missing')
            entries += 1
        for text in self.optionals:
            painter.setPen(yellow)
            point = QPoint(20, 20 + entries * 20)
            painter.drawText(point, ' Missing: '.join(text))
            entries += 1
        for item in self.collected:
            painter.setPen(yellow)
            point = QPoint(20, 20 + entries * 20)
            painter.drawText(point, f'{item[0]} used {item[1]} times')
            entries += 1


class ItemModel(QStandardItemModel):
    def __init__(self, parent, item):
        super().__init__(parent)
        self.update_item(item)

    def update_item(self, item: Item):
        self.item = item
        self.setVerticalHeaderLabels([f.upper() for f in self.item.__dict__.keys() if f != 'itemname' and f != 'name'
                                      and f != 'size' and f != 'description' and f != 'parameters' and f != 'name' and
                                      f != 'data'])
        valuelist = []
        for key, value in item.__dict__.items():
            if key == 'itemname' or key == 'name' or key == 'size' or key == 'description' or key == 'parameters' or \
                    key == 'name' or key == 'data':
                continue
            valuelist.append(self.convert_to_string(key, value))
        self.appendColumn(valuelist)

    def convert_to_string(self, key, value):
        if isinstance(value, bytes) or isinstance(value, bytearray):
            item = QStandardItem(value.hex())
        else:
            item = QStandardItem(f'{value:02X}')
        # item.setTextAlignment(Qt.AlignRight)
        return item


class Room:
    def __init__(self, name, workingpath, filename, defaultpath):
        self.name = name
        self.workingpath = workingpath
        self.filename = filename
        self.defaultpath = defaultpath
        self.set_scddata()
        self.readinitems()

    def set_scddata(self):
        with open(self.workingpath + self.filename, 'rb') as file:
            self.data = bytearray(file.read())

        self.scdstartoff = struct.unpack('<i', self.data[0x48:0x4C])[0]
        self.scdendoff = struct.unpack('<i', self.data[0x3C:0x40])[0]

        if self.scdendoff == 0:
            self.scdendoff = -1

        self.relevantdata = self.data[self.scdstartoff:self.scdendoff]

    def readinitems(self):
        self.items = []
        for index, value in enumerate(self.relevantdata):
            if value == 0x67 and self.relevantdata[index + 2] == 0x2 and (self.relevantdata[index + 3] == 0x31 or
                                                                          self.relevantdata[index + 3] == 0x21):
                data = self.relevantdata[index:index + 22]
                item = ItemAOTSet()
            elif value == 0x68 and len(self.relevantdata[index:]) >= 30 and self.relevantdata[index + 2] == 0x2 \
                    and self.relevantdata[index + 3] == 0x31:
                data = self.relevantdata[index:index + 30]
                item = ItemAOTSet4P()
            else:
                continue

            item.update_vars(data)

            if self.is_exception(item):
                continue

            self.items.append([item, self.scdstartoff + index])

    def is_exception(self, item: AOTOpcode):
        match self.name:
            case 'Construction Site':
                if item.itemname == 'Battery':
                    return True
            case 'Synthesis Room':
                if item.itemname == 'Vaccine Medium':
                    return True
            case 'Chronos Room':
                return True

    def get_items(self) -> list[str]:
        return [key for key, value in self.items]

    def get_item_at_index(self, index) -> Item:
        if len(self.items) > 0:
            return self.items[index][0]

    def changeitem(self, itemindex: int, newitem: str, quantity: int):
        olditem, offset = self.items[itemindex]
        data = olditem.data
        itemid = struct.pack('<h', itemnames.index(newitem))
        quantity = struct.pack('<h', quantity)
        if olditem.opcode == 0x67:
            data[I67OP.ID:I67OP.ID + 2] = itemid
            data[I67OP.AMOUNT:I67OP.AMOUNT + 2] = quantity
        elif olditem.opcode == 0x68:
            data[I68OP.ID:I68OP.ID + 2] = itemid
            data[I68OP.AMOUNT:I68OP.AMOUNT + 2] = quantity
        olditem.update_vars(data)
        self.writeitemstofile()
        return olditem

    def updatequantity(self, itemindex: int, quantity: int):
        olditemdata, offset = self.items.pop(itemindex)
        if olditemdata.opcode == 0x67:
            olditemdata.data[I67OP.AMOUNT:I67OP.AMOUNT + 2] = struct.pack('<h', quantity)
        elif olditemdata.opcode == 0x68:
            olditemdata.data[I68OP.AMOUNT:I68OP.AMOUNT + 2] = struct.pack('<h', quantity)
        self.items.insert(itemindex, [olditemdata, offset])
        self.writeitemstofile()
        return olditemdata

    def writeitemstofile(self):
        for item, offset in self.items:
            self.data[offset:offset + len(item.data)] = item.data
        with open(self.workingpath + self.filename, 'wb') as file:
            file.write(self.data)

    def changeitemwithflag(self, newitem: AOTOpcode):
        for item, offset in self.items:
            if item.flag == newitem.flag:
                if item.opcode == 0x67:
                    item.data[I67OP.ID:I67OP.ID + 2] = newitem.id
                    item.data[I67OP.AMOUNT:I67OP.AMOUNT + 2] = newitem.amount
                if item.opcode == 0x68:
                    item.data[I68OP.ID:I68OP.ID + 2] = newitem.id
                    item.data[I68OP.AMOUNT:I68OP.AMOUNT + 2] = newitem.amount
                item.update_vars(item.data)
                self.writeitemstofile()
                break

    def resetitems(self):
        with open(self.defaultpath + self.filename, 'rb') as file:
            data = file.read()
            for item, index in self.items:
                item.data = data[index:index + item.size]
                item.update_vars(item.data)
            self.writeitemstofile()


class FileManager(QObject):
    progressupdate = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def update_directorys(self, defaultdirectory: str, workingdirectory: str):
        self.defaultdirectory = defaultdirectory
        self.workingdirectory = workingdirectory
        self.rooms = []
        QApplication.processEvents()
        for key, value in roomnames.items():
            self.progressupdate.emit(len(self.rooms))
            self.rooms.append(Room(value, workingdirectory, key + '.RDT', defaultdirectory))

    def restore_room_items(self, roomname: str):
        room = self.find_room(roomname)
        room.resetitems()

    def restore_all_items(self):
        for room in self.rooms:
            room.resetitems()

    def get_directory(self):
        return self.directory

    def get_room_names(self):
        return list(roomnames.values())

    def get_all_items(self):
        return [f for f in itemnames]

    def find_room(self, name: str):
        for room in self.rooms:
            if room.name == name:
                return room

    def room_has_items(self, roomname: str):
        room = self.find_room(roomname)
        items = room.get_items()
        return len(items) > 0

    def get_room_items(self, roomname: str):
        room = self.find_room(roomname)
        items = room.get_items()
        if len(items) > 0:
            return items

    def get_item_at_index(self, roomname: str, index: int):
        if self.room_has_items(roomname):
            room = self.find_room(roomname)
            return room.get_item_at_index(index)

    def changeitemquantity(self, roomname: str, itemindex:int, quantity: int):
        room = self.find_room(roomname)
        item = room.updatequantity(itemindex, quantity)
        self.handlesameflag(roomname, item)

    def swap(self, roomname: str, olditemindex: int, newitem: str, quantity:int):
        room = self.find_room(roomname)
        item = room.changeitem(olditemindex, newitem, quantity)
        self.handlesameflag(roomname, item)

    def handlesameflag(self, roomname: str, item: AOTOpcode):
        flag = int.from_bytes(item.flag, 'little')
        if flag in roomitemflags.keys():
            for collection in roomitemflags[flag]:
                if roomname in collection:
                    for otherroom in collection:
                        if otherroom != roomname:
                            room = self.find_room(otherroom)
                            room.changeitemwithflag(item)

    def get_all_file_contents(self, roomname: str):
        room = self.find_room(roomname)
        with open(room.file, 'rb') as file:
            return file.read()


