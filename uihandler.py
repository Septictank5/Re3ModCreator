from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from UI.Reditor import Ui_MainWindow
from UI.loadingdialog import Ui_Dialog as LoadUIDialog
from UI.VerificationDialog import Ui_Dialog as VerifUIDialog
from codeviewer.codescript import CodeViewerWindow
from codeviewer.opcodes import *


class VerifyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        self.view = VerifUIDialog()
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
        self.updateItem(item)

    def updateItem(self, item: bytearray):
        self.item = item
        OP = I67OP if item[0] == 0x67 else I68OP
        entries = [f for f in list(OP)]
        entries.pop(-1)
        self.setVerticalHeaderLabels([f.name for f in entries])
        valuelist = []
        for index, entry in enumerate(entries):
            determiner = entries[index + 1] - entries[index] if index != len(entries) - 1 else 1
            if determiner == 1:
                valuelist.append(QStandardItem(f'{item[entry.value]:02X}'))
            else:
                valuelist.append(QStandardItem(f'{struct.unpack("<h", item[entry.value:entry.value + 2])[0]:02X}'))

        self.appendColumn(valuelist)


class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = LoadUIDialog()
        self.view.setupUi(self)
        self.view.LoadingRdtProgressBar.setMaximum(len(datapy.roomnames))

    def setProgValue(self, value):
        self.view.LoadingRdtProgressBar.setValue(value)
        if value == self.view.LoadingRdtProgressBar.maximum() - 1:
            return True

    def hide(self) -> None:
        super().hide()
        self.view.LoadingRdtProgressBar.reset()


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.view = Ui_MainWindow()
        self.view.setupUi(self)
        self.view.itemtree.verticalScrollBar().hide()
        self.setWindowTitle('RE3 Mod Maker')
        self.codeviewer = CodeViewerWindow(self)
        self.verifdialog = VerifyDialog(self)
        self.progdialog = ProgressDialog(self)
        self.view.codeviewerbutton.pressed.connect(self.codeviewer.show)
        self.progdialog.show()

    def updateProgress(self, value):
        finished = self.progdialog.setProgValue(value)
        if finished:
            self.progdialog.hide()
            self.show()

    # --------------------------Item Tab----------------------------------- #

    def connectOpenDir(self, func):
        self.view.actionOpen.triggered.connect(func)

    def connectOpenMod(self, func):
        self.view.openmodbutton.pressed.connect(func)
        self.view.actionOpen_Mod.triggered.connect(func)

    def connectCreateMod(self, func):
        self.view.actionCreate_Mod.triggered.connect(func)

    def connectSwap(self, func):
        self.view.SwapItemButton.pressed.connect(func)
        self.view.ChangeDoorTargetButton.pressed.connect(func)

    def connectQuantityUpdate(self, func):
        self.view.quantitybox.valueChanged.connect(func)

    def connectRoomChange(self, func):
        self.view.RoomList_Items.currentRowChanged.connect(func)
        self.view.RoomList_Doors.currentRowChanged.connect(func)
        # self.view.RoomList_Enemies.currentRowChanged.connect(func)

    def connectFocusChange(self, func):
        self.view.RoomItemsList.currentRowChanged.connect(func)
        self.view.RoomTargetList.currentRowChanged.connect(func)

    def connectRoomTargetChange(self, func):
        self.view.RoomTargetList.currentRowChanged.connect(func)

    def connectRestoreRoom(self, func):
        self.view.RestoreRoomItemsButton.pressed.connect(func)
        self.view.RestoreRoomDoorsButton.pressed.connect(func)

    def connectVerify(self, func):
        self.view.verifybutton.pressed.connect(func)

    def connectRestoreAllRooms(self, func):
        self.view.RestoreAllRoomsItemsButton.pressed.connect(func)
        self.view.RestoreAllRoomsDoorsButton.pressed.connect(func)

    def connectTabChanged(self, func):
        self.view.tabWidget.currentChanged.connect(func)

    def updateModTitle(self, title: str):
        self.view.modlabel.setText(title + ' Mod')

    def initUI(self, roomlist: list[str], itemlist):
        self.view.itemtree.setShowGrid(False)
        self.view.itemtree.horizontalHeader().hide()
        self.view.RoomList_Items.addItems(roomlist)
        self.view.RoomList_Doors.addItems(roomlist)
        self.view.RoomTargetList.addItems(roomlist)
        self.view.itemlist.addItems(itemlist)
        self.view.RoomList_Items.setCurrentRow(0)
        self.view.RoomList_Doors.setCurrentRow(0)
        self.view.RoomTargetList.setCurrentRow(0)

    def get_Room(self):
        index = self.view.tabWidget.currentIndex()
        match index:
            case 0:
                return self.view.RoomList_Items.currentItem().text()
            case 1:
                return self.view.RoomList_Doors.currentItem().text()

    def get_TargetRoom(self):
        return self.view.RoomTargetList.currentItem().text()

    def get_Door(self):
        return self.view.RoomDoorsList.currentItem().text()

    def get_DoorIndex(self):
        return self.view.RoomDoorsList.currentRow()

    def get_TargetDoor(self):
        return self.view.TargetDoorsList.currentItem().text()

    def get_TargetDoorIndex(self):
        return self.view.TargetDoorsList.currentRow()

    def get_RoomIndex(self):
        return self.view.RoomList_Items.currentRow()

    def get_Item(self):
        return self.view.itemlist.currentItem().text()

    def get_RoomItem(self):
        return self.view.RoomItemsList.currentItem().text()

    def get_RoomItemIndex(self):
        return self.view.RoomItemsList.currentRow()

    def get_Quantity(self):
        return self.view.quantitybox.value()

    def set_RoomItemRow(self, row):
        self.view.RoomItemsList.setCurrentRow(row)

    def set_RoomDoorRow(self, row):
        self.view.RoomDoorsList.setCurrentRow(row)

    def set_TargetDoorRow(self, row):
        self.view.TargetDoorsList.setCurrentRow(row)

    def reset_rows(self):
        self.view.RoomList_Items.setCurrentRow(0)
        self.view.RoomItemsList.setCurrentRow(0)

    def updateRoomItems(self, items: list[dict]):
        self.view.RoomItemsList.clear()
        if items:
            self.view.RoomItemsList.addItems(f['name'] for f in items)
            self.view.RoomItemsList.setCurrentRow(0)

    def updateRoomDoors(self, doors: list[dict]):
        self.view.RoomDoorsList.clear()
        if doors:
            self.view.RoomDoorsList.addItems(f"{f['ogtarget']}:{f['curtarget']}, CAM: {f['ncut']}" for f in doors)
            self.view.RoomDoorsList.setCurrentRow(0)

    def updateTargetDoors(self, doors: list[dict]):
        self.view.TargetDoorsList.clear()
        if doors:
            self.view.TargetDoorsList.addItems(f"{f['ogtarget']}:{f['curtarget']}, CAM: {f['ncut']}" for f in doors)
            self.view.TargetDoorsList.setCurrentRow(0)

    def updateItemDetails(self, item: bytearray):
        if item:
            OP = I67OP if item[0] == 0x67 else I68OP
            self.view.quantitybox.setValue(struct.unpack('<h', item[OP.AMOUNT:OP.AMOUNT+2])[0])
            model = ItemModel(self, item)
            self.view.itemtree.setModel(model)
            rowcount = model.rowCount()
            height = self.view.itemtree.height() + 10
            for row in range(rowcount):
                self.view.itemtree.setRowHeight(row, height // rowcount)
