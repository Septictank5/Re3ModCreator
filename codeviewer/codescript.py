from codeviewer.Codeview import Ui_MainWindow
from codeviewer.opcodes import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class CodeViewerWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.view = Ui_MainWindow()
        self.view.setupUi(self)
        self.setWindowTitle('CodeViewer')
        self.codelist = self.view.codelist
        self.codemodel = QStandardItemModel()

    def showEvent(self, event: QShowEvent) -> None:
        self.codemodel.clear()
        self.codemodel.setHorizontalHeaderLabels(['Offset', 'Opcode', 'Name', 'Parameters', 'Description'])
        room = self.parent.get_Room()
        for key, value in datapy.roomnames.items():
            if value == room:
                self.read_in_data(key)
        super().show()

    def read_in_data(self, key):
        roomfile = key + '.SCD'
        with open('SCD/' + roomfile, 'rb') as file:
            data = file.read()

        index = 0
        while index < len(data):
            opcode = data[index]
            if opcode not in opcodes.keys():
                index += 1
                continue
            opcodemanager = opcodes[opcode]()
            datasize = opcodemanager.get_size()
            opcodedata = data[index:index + datasize]
            if len(opcodedata) < datasize:
                break
            opcodemanager.set_offset(index)
            opcodemanager.update_vars(opcodedata)
            values = opcodemanager.get_details()

            itemdata = []
            for spot, value in enumerate(values):
                font = QFont()
                font.setPixelSize(12)
                itemdata.append(QStandardItem(value))
                if spot < 2:
                    font.setPixelSize(14)
                    font.setBold(True)
                    itemdata[-1].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                itemdata[0].setTextAlignment(Qt.AlignCenter)
                itemdata[-1].setFont(font)

            self.codemodel.appendRow(itemdata)
            index += datasize

        self.codelist.setModel(self.codemodel)
        width = self.codelist.width() - 16
        self.codelist.setColumnWidth(0, int(width * .05))
        self.codelist.setColumnWidth(1, int(width * .05))
        self.codelist.setColumnWidth(2, int(width * .11))
        self.codelist.setColumnWidth(3, int(width * .49))
        self.codelist.setColumnWidth(4, int(width * .3))

        for row in range(self.codemodel.rowCount()):
            self.codelist.resizeRowToContents(row)
        self.codelist.verticalHeader().hide()
