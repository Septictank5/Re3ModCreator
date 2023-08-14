from tools import *
from UI.Reditor import Ui_MainWindow
from UI.loadingdialog import Ui_Dialog
from codeviewer.codescript import CodeViewerWindow


class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = Ui_Dialog()
        self.view.setupUi(self)
        self.view.LoadingRdtProgressBar.setMaximum(len(roomnames))

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

    def connectQuantityUpdate(self, func):
        self.view.quantitybox.valueChanged.connect(func)

    def connectRoomChange(self, func):
        self.view.RoomList_Items.currentRowChanged.connect(func)
        self.view.RoomList_Doors.currentRowChanged.connect(func)
        # self.view.RoomList_Enemies.currentRowChanged.connect(func)

    def connectItemChange(self, func):
        self.view.RoomItemsList.clicked.connect(func)

    def connectRoomTargetChange(self, func):
        self.view.RoomTargetList.currentRowChanged.connect(func)

    def connectRestoreRoomItems(self, func):
        self.view.RestoreRoomItemsButton.pressed.connect(func)

    def connectVerify(self, func):
        self.view.verifybutton.pressed.connect(func)

    def connectRestoreAllRoomItems(self, func):
        self.view.RestoreAllRoomsItemsButton.pressed.connect(func)

    def connectTabChanged(self, func):
        self.view.tabWidget.currentChanged.connect(func)

    def updateModTitle(self, title: str):
        self.view.modlabel.setText(title + ' Mod')

    def initUI(self, roomlist, itemlist):
        self.view.itemtree.setShowGrid(False)
        self.view.itemtree.horizontalHeader().hide()
        self.view.RoomList_Items.addItems(roomlist)
        self.view.RoomList_Doors.addItems(roomlist)
        self.view.RoomTargetList.addItems(roomlist)
        self.view.itemlist.addItems(itemlist)
        self.view.RoomList_Items.setCurrentRow(0)
        self.view.RoomList_Doors.setCurrentRow(0)

    def get_Room(self):
        index = self.view.tabWidget.currentIndex()
        match index:
            case 0:
                return self.view.RoomList_Items.currentItem().text()
            case 1:
                return self.view.RoomList_Doors.currentItem().text()

    def get_TargetRoom(self):
        return self.view.RoomTargetList.currentItem().text()

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

    def reset_rows(self):
        self.view.RoomList_Items.setCurrentRow(0)
        self.view.RoomItemsList.setCurrentRow(0)

    def updateRoomItems(self, items: list[AOTOpcode]):
        self.view.RoomItemsList.clear()
        if items:
            self.view.RoomItemsList.addItems([item.itemname for item in items])
            self.view.RoomItemsList.setCurrentRow(0)

    def updateRoomDoors(self, doors: list[AOTOpcode]):
        self.view.RoomDoorsList.clear()
        if doors:
            self.view.RoomDoorsList.addItems([door.doorname for door in doors])
            self.view.RoomDoorsList.setCurrentRow(0)

    def updateTargetDoorsCams(self, doors: list[AOTOpcode]):
        self.view.TargetDoorsList.clear()
        self.view.CamerasList.clear()
        if doors:
            self.view.TargetDoorsList.addItems(door.doorname for door in doors)
            self.view.CamerasList.addItems(f'{door.ncut:02X}' for door in doors)
            self.view.TargetDoorsList.setCurrentRow(0)
            self.view.CamerasList.setCurrentRow(0)

    def updateItemDetails(self, item: AOTOpcode):
        if item:
            self.view.quantitybox.setValue(int.from_bytes(item.amount, 'little'))
            model = ItemModel(self, item)
            self.view.itemtree.setModel(model)
            rowcount = model.rowCount()
            height = self.view.itemtree.height() + 10
            for row in range(rowcount):
                self.view.itemtree.setRowHeight(row, height // rowcount)
