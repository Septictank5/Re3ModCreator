import struct
import datapy
from datapy import *
from enum import IntEnum


class Opcode:
    def __init__(self):
        self.name = ''
        self.description = ''
        self.parameters = ''
        self.size = 1

    def update_vars(self, data):
        self.opcode = data[0] if len(data) > 1 else int.from_bytes(data)
        self.data = bytearray(data)

    def set_offset(self, offset):
        self.offset = offset

    def get_size(self):
        return self.size

    def get_description(self):
        return self.description

    def get_details(self):
        return [f'{self.offset:04X}', f'{self.opcode:02X}', self.name, self.parameters, self.description]




class AlignedOpcode(Opcode):
    def __init__(self):
        super().__init__()
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.parameters = f'zAlign: {self.zAlign:02X}'


class BlockAlignedOpcode(Opcode):
    def __init__(self):
        super().__init__()
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.BlockLength = data[2:]
        self.parameters = f"zAlign: {self.zAlign:02X}, Block Length: {self.BlockLength.hex(' ')}"


class AOTBase(Opcode):
    def __init__(self):
        super().__init__()

    def update_vars(self, data):
        super().update_vars(data)
        self.aot = data[1]
        self.sce = data[2]
        self.sat = data[3]
        self.nfloor = data[4]
        self.super = data[5]

    def get_sce(self):
        return sce[self.sce]


class AOTOpcode(AOTBase):
    def __init__(self):
        super().__init__()

    def update_vars(self, data):
        super().update_vars(data)
        self.xpos = data[6:8]
        self.zpos = data[8:10]
        self.width = data[10:12]
        self.depth = data[12:14]


class AOT4POpcode(AOTOpcode):
    def __init__(self):
        super().__init__()

    def update_vars(self, data):
        super().update_vars(data)
        self.xpos0 = data[6:8]
        self.zpos0 = data[8:10]
        self.xpos1 = data[10:12]
        self.zpos1 = data[12:14]
        self.xpos2 = data[14:16]
        self.zpos2 = data[16:18]
        self.xpos3 = data[18:20]
        self.zpos3 = data[20:22]


class NOP0(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'NOP0'
        self.description = '!!NOP!!'


class EvtEnd(AlignedOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'EVT_END'
        self.description = 'Exit Function, Return Value'


class EvtNext(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'EVT_NEXT'
        self.description = 'Await Player Input'


class EvtChain(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'EVT_CHAIN'
        self.description = 'Reinit Script Before Executing New Func'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = self.data[1]
        self.parameters = f'Data0: {self.data0:02X}'


class EvtExec(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'EVT_EXEC'
        self.description = 'Execute Embedded Two-Byte Instruction'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.Condition = data[1]
        self.T_Opcode = data[2]
        self.Event = data[3]
        self.parameters = f'Condition: {self.Condition:02X}, T.Opcode: {self.T_Opcode:02X}, Event: {self.Event:02X}'


class EvtKill(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'EVT_KILL'
        self.description = 'Disable Event'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.Event = data[1]
        self.parameters = f'Event: {self.Event:02X}'


class IfElseCheck(BlockAlignedOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'IFEL_CK'
        self.description = '--If Block--'


class ElseCheck(BlockAlignedOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'ELSE_CK'
        self.description = '--ELSE--'


class EndIf(AlignedOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'END_IF'
        self.description = '--END OF IF STATEMENT--'


class Sleep(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SLEEP'
        self.description = 'Sleep for Count Time'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.Count = data[2:]
        self.parameters = f"zAlign: {self.zAlign:02X}, Count: {self.Count.hex(' ')}"


class Sleeping(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SLEEPING'
        self.description = 'Current Evt Sleeps For Count Time'
        self.size = 3

    def update_vars(self, data):
        super().update_vars(data)
        self.Count = data[1:]
        self.parameters = f"Count: {self.Count.hex(' ')}"


class WSleep(AlignedOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'WSLEEP'
        self.description = 'Init Global Sleep'


class WSleeping(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'WSLEEPING'
        self.description = 'Init Global Sleep'


class For(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'FOR'
        self.description = 'Loop Block Count Times'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.BlockLength = data[2:4]
        self.Count = data[4:]
        self.parameters = f"zAlign: {self.zAlign:02X}, Block Length: {self.BlockLength.hex(' ')}, " \
                          f"Count: {self.Count.hex(' ')}"


class For2(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'FOR2'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign0 = data[1]
        self.data0 = data[2:4]
        self.zAlign1 = data[4]
        self.data1 = data[5]
        self.parameters = f"zAlign0: {self.zAlign0:02X}, Data0: {self.data0.hex(' ')}, zAlign1: {self.zAlign1:02X}, " \
                          f"Data1: {self.data1:02X}"


class Next(AlignedOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'NEXT'
        self.description = 'End Of For Block'


class While(BlockAlignedOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'WHILE'
        self.description = 'Loop Until Follow Check Is False'


class EndWhile(AlignedOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'END_WHILE'
        self.description = 'END Of While Block'


class Do(BlockAlignedOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'DO'
        self.description = 'Loop Until Check Is False, Check At End Of Block'


class EndDo(AlignedOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'END_DO'
        self.description = 'End Of Do Block'


class Switch(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SWITCH'
        self.description = 'Execute Instructions Based On Var Value'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.var = data[1]
        self.BlockLength = data[2:]
        self.parameters = f"Var: {self.var:02X}, Block Length: {self.BlockLength.hex(' ')}"


class Case(AlignedOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'CASE'
        self.description = 'Execute If Value == Switch Var'


class Default(AlignedOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'DEFAULT'
        self.description = 'If No CASE Matches, Execute Block'


class EndSwitch(AlignedOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'END_SWITCH'
        self.description = 'End Of Switch Block'


class Goto(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'GOTO'
        self.description = 'Go To Relative Offset'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.Unk0 = data[1]
        self.Unk1 = data[2]
        self.Unk2 = data[3]
        self.zoffset = data[4:]
        self.parameters = f"Unk0: {self.Unk0:02X}, Unk1: {self.Unk1:02X}, Unk2: {self.Unk2:02X}, " \
                          f"Offset: {self.zoffset.hex(' ')}"


class Gosub(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'GOSUB'
        self.description = 'Execute Subroutine'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.subroutine = data[1]
        self.parameters = f'Subroutine: {self.subroutine:02X}'


class Return(AlignedOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'RETURN'
        self.description = 'End Subroutine'


class Break(AlignedOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'BREAK'
        self.description = 'Exit Current Block'


class BreakPoint(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'BREAKPOINT'
        self.description = '???'


class WorkCopy(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'WORKCOPY'
        self.description = 'Write Var At Offset With Size Bytes'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.var = data[1]
        self.zoffset = data[2]
        self.bytesize = data[3]
        self.parameters = f'Var: {self.var:02X}, Offset: {self.zoffset:02X}, Size: {self.bytesize:02X}'


class Save(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SAVE'
        self.description = 'Set Variable At Index To Value'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.index = data[1]
        self.Value = data[2:]
        self.parameters = f"Index: {self.index:02X}, Value: {self.Value.hex(' ')}"


class Copy(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'COPY'
        self.description = 'Copy A Word From Source Var To Destination Var'
        self.size = 3

    def update_vars(self, data):
        super().update_vars(data)
        self.Destination = data[1]
        self.Source = data[2]
        self.parameters = f'Destination: {self.Destination:02X}, Source: {self.Source:02X}'


class Calc(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'CALC'
        self.description = 'Perform Operation On Var Using IMM Value'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.oper = data[2]
        self.var = data[3]
        self.value = data[4:]
        self.parameters = f"zAlign: {self.zAlign:02X}, Operation: {self.oper:02x}, Var: {self.var:02X}, " \
                          f"Value: {self.value.hex(' ')}"


class Calc2(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'CALC2'
        self.description = 'Perform Operation On Var Using Source Var'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.oper = data[1]
        self.var = data[2]
        self.source = data[3]
        self.parameters = f'Operation: {calcop[self.oper]}, Var: {self.var:02X}, Source: {self.source:02X}'


class EvtCut(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'EVT_CUT'
        self.description = '???'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.zAlign = data[2]
        self.data1 = data[3]
        self.parameters = f'Data0: {self.data0:02X}, zAlign: {self.zAlign:02X}, Data1: {self.data1:02X}'


class NOP1(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'NOP1'
        self.description = '!!NOP!!'


class ChaserEvtClr(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'CHASER_EVT_CLR'
        self.description = '???'


class OpenMap(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'OPEN_MAP'
        self.description = 'Open Map'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign0 = data[1]
        self.Data0 = data[2]
        self.zAlign1 = data[3]
        self.parameters = f'zAlign0: {self.zAlign0:02X}, Data: {self.Data0:02X}, zAlign1: {self.zAlign1:02X}'


class PointAdd(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'POINTADD'
        self.description = '???'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.data0 = data[2:4]
        self.data1 = data[4:]
        self.parameters = f"zAlign: {self.zAlign:02X}, Data0: {self.data0.hex(' ')}, Data1: {self.data1.hex(' ')}"


class DoorCheck(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'DOOR_CK'
        self.description = 'Door Check'


class DieDemoOn(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'DIEDEMO_ON'
        self.description = 'Demo??'


class DirCK(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'DIR_CK'
        self.description = '???'
        self.size = 8

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.data0 = data[2:4]
        self.data1 = data[4:6]
        self.data2 = data[6:]
        self.parameters = f"zAlign: {self.zAlign:02X}, Data0: {self.data0.hex(' ')}, Data1: {self.data1.hex(' ')}, " \
                          f"Data2: {self.data2.hex(' ')}"


class PartsSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'PARTS_SET'
        self.description = 'Set Value In Mem Location'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.data0 = data[2]
        self.data1 = data[3]
        self.value = data[4:]
        self.parameters = f"zAlign: {self.zAlign:02X}, Data0: {self.data0:02X}, Data1: {self.data1:02X}, " \
                          f"Value: {self.value.hex(' ')}"


class VloopSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'VLOOP_SET'
        self.description = '???'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.parameters = f'Data0: {self.data0:02X}'


class OTABESet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'OTA_BE_SET'
        self.description = '???'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2]
        self.data2 = data[3]
        self.parameters = f'Data0: {self.data0:02X}, Data1: {self.data1:02X}, Data2: {self.data2:02X}'


class LineStart(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'LINE_START'
        self.description = '???'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2:]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1.hex(' ')}"


class LineMain(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'LINE_MAIN'
        self.description = '???'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2:4]
        self.data2 = data[4:]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1.hex(' ')}, Data2: {self.data2.hex(' ')}"


class LineEnd(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'LINE_END'
        self.description = '???'


class LightPosSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'LIGHT_POS_SET'
        self.description = 'Set A Light Position Component For Current Camera'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.light = data[2]
        self.axis = data[3]
        self.value = data[4:]
        self.parameters = f"zAlign = {self.zAlign:02X}, Light: {self.light:02X}, Axis: {self.axis:02X}, " \
                          f"Value: {self.value.hex(' ')}"


class LightKidoSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'LIGHT_KIDO_SET'
        self.description = 'Changes Brightness Of One Light, For Current Camera'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.light = data[1]
        self.brightness = data[2:]
        self.parameters = f"Light: {self.light:02X}, Brightness: {self.brightness.hex(' ')}"


class LightColorSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'LIGHT_COLOR_SET'
        self.description = 'Set Color Of One Light, For Current Camera'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.light = data[1]
        self.red = data[2]
        self.green = data[3]
        self.blue = data[4]
        self.zAlign = data[5]
        self.parameters = f'Light: {self.light:02X}, Red: {self.red:02X}, Green: {self.green:02X}, ' \
                          f'Blue: {self.blue:02X}, zAlign: {self.zAlign:02X}'


class AheadRoomSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'AHEAD_ROOM_SET'
        self.description = '???'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.value = data[2:]
        self.parameters = f"zAlign: {self.zAlign:02X}, Value: {self.value.hex(' ')}"


class EsprCtr(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'ESPR_CTR'
        self.description = '???'
        self.size = 10

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2]
        self.data2 = data[3]
        self.data3 = data[4]
        self.data4 = data[5]
        self.data5 = data[6]
        self.data6 = data[7]
        self.data7 = data[8]
        self.zAlign = data[9]
        self.parameters = f'Data0: {self.data0:02X}, Data1: {self.data1:02X}, Data2: {self.data2:02X}, ' \
                          f'Data3: {self.data3:02X}, Data4: {self.data4:02X}, Data5: {self.data5:02X}, ' \
                          f'Data6: {self.data6:02X}, Data7: {self.data7:02X}, zAlign: {self.zAlign:02X}'


class BgmTableCheck(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'BGM_TBL_CK'
        self.description = '???'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.data0 = data[2]
        self.data1 = data[3]
        self.data2 = data[4:]
        self.parameters = f"'Data0: {self.data0:02X}, Data1: {self.data1:02X}, Data2: {self.data2.hex(' ')}"


class ItemGetCheck(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'ITEM_GET_CK'
        self.description = 'Adds Item To Inventory'
        self.size = 3

    def update_vars(self, data):
        super().update_vars(data)
        self.id = data[1]
        self.amount = data[2]
        self.parameters = f'Item: {itemnames[self.id]}, Amount: {self.amount:02X}'


class OmRev(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'OM_REV'
        self.description = '???'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.parameters = f'Data: {self.data0:02X}'


class ChaserLifeInit(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'CHASER_LIFE_INIT'
        self.description = '???'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.parameters = f'Data: {self.data0:02X}'


class PartsBomb(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'PARTS_BOMB'
        self.description = '???'
        self.size = 16

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2]
        self.data2 = data[3]
        self.data3 = data[4]
        self.data4 = data[5]
        self.data5 = data[6:8]
        self.data6 = data[8:10]
        self.data7 = data[10:12]
        self.data8 = data[12:14]
        self.data9 = data[14:]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1:02X}, Data2: {self.data2:02X}, " \
                          f"Data3: {self.data3:02X}, Data4: {self.data4:02X}, Data5: {self.data5.hex(' ')}, " \
                          f"Data6: {self.data6.hex(' ')}, Data7: {self.data7.hex(' ')}, Data8: {self.data8.hex(' ')}," \
                          f" Data9: {self.data9.hex(' ')}"


class PartsDown(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'PARTS_DOWN'
        self.description = '???'
        self.size = 16

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2:4]
        self.data2 = data[4:6]
        self.data3 = data[6:8]
        self.data4 = data[8:10]
        self.data5 = data[10:12]
        self.data6 = data[12:14]
        self.data7 = data[14:]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1.hex(' ')}, Data2: {self.data2.hex(' ')}, " \
                          f"Data3: {self.data3.hex(' ')}, Data4: {self.data4.hex(' ')}, Data5: {self.data5.hex(' ')}," \
                          f" Data6: {self.data6.hex(' ')}, Data7: {self.data7.hex(' ')}"


class ChaserItemSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'CHASER_ITEM_SET'
        self.description = '???'
        self.size = 3

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2]
        self.parameters = f'Data0: {self.data0:02X}, Data1: {self.data1:02X}'


class WeaponChangeOld(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'WPN_CHG_OLD'
        self.description = '???'


class SelectEventOn(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SEL_EVT_ON'
        self.description = '???'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.parameters = f'Data: {self.data0:02X}'


class ItemLost(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'ITEM_LOST'
        self.description = 'Remove Item From Player Inventory'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.id = data[1]
        self.parameters = f'Item: {itemnames[self.id]}'


class FlrSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'FLR_SET'
        self.description = "Set Or Clear Flag Of Object with index 'Id' At Offset 11 Of File"
        self.size = 3

    def update_vars(self, data):
        super().update_vars(data)
        self.id = data[1]
        self.flag = data[2]
        self.parameters = f'ID: {self.id:02X}, Flag: {set_ck_flags[self.flag]}'


class MemberSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'MEMB_SET'
        self.description = 'Set Value For An Entity'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2:]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1.hex(' ')}"


class MemberSet2(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'MEMB_SET2'
        self.description = 'Copy var value to given value for current entity'
        self.size = 3

    def update_vars(self, data):
        super().update_vars(data)
        self.id = data[1]
        self.var = data[2]
        self.parameters = f'ID: {self.id:02X}, Var: {self.var:02X}'


class MemberCopy(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'MEMB_COPY'
        self.description = 'Copy Value For Current Entity To Var'
        self.size = 3

    def update_vars(self, data):
        super().update_vars(data)
        self.var = data[1]
        self.id = data[2]
        self.parameters = f'Var: {self.var:02X}, ID: {self.id:02X}'


class MemberCompare(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'MEMB_CMP'
        self.description = 'Compare IMM Value To Memory Location Using Function'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.function = data[2:4]
        func = struct.unpack('<h', self.function)[0]
        self.value = data[4:]
        self.parameters = f"zAlign: {self.zAlign:02X}, Func: {self.function.hex(' ').upper()}, Value: {self.value.hex(' ')}"


class MemberCalc(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'MEMB_CALC'
        self.description = '???'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.data0 = data[2:4]
        self.data1 = data[4:]
        self.parameters = f"zAlign: {self.zAlign:02X}, Data0: {self.data0.hex(' ')}, Data1: {self.data1.hex(' ')}"


class MemberCalc2(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'MEMB_CALC2'
        self.description = '???'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2]
        self.data2 = data[3]
        self.parameters = f'Data0: {self.data0:02X}, Data1: {self.data1:02X}, Data2: {self.data2:02X}'


class FadeSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'FADE_SET'
        self.description = ''
        self.size = 11

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2]
        self.data2 = data[3]
        self.data3 = data[4]
        self.data4 = data[5]
        self.data5 = data[6]
        self.data6 = data[7]
        self.data7 = data[8]
        self.data8 = data[9]
        self.data9 = data[10]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1:02X}, Data2: {self.data2:02X}, " \
                          f"Data3: {self.data3:02X}, Data4: {self.data4:02X}, Data5: {self.data5:02X}, " \
                          f"Data6: {self.data6:02X}, Data7: {self.data7:02X}, Data8: {self.data8:02X}, " \
                          f"Data9: {self.data9:02X}"


class WorkSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'WORK_SET'
        self.description = 'Selects Current Object For Further Instructions'
        self.size = 3

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.object = data[2]
        self.parameters = f'Data: {self.data0:02X}, Object: {self.object:02X}'


class SpeedSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SPEED_SET'
        self.description = 'Sets One Of The Words Of Internal Register'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.component = data[1]
        self.value = data[2:4]
        value = struct.unpack('<h', self.value)[0]
        self.parameters = f"Component: {self.component:02X}, Value: {self.value.hex(' ').upper()}"


class AddSpeed(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'ADD_SPEED'
        self.description = 'Sets Internal Register From A Memory Location'


class AddASpeed(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'ADD_ASPEED'
        self.description = 'Add 6 Words Together'


class AddVSpeed(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'ADD_VSPEED'
        self.description = '???'


class EvalCheck(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'EVAL_CK'
        self.description = 'Check Flag In Object Is Value'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.flag = data[1]
        self.object = data[2]
        self.value = data[3]
        self.parameters = f'Flag: {self.flag}, Object: {self.object:02X}, Value: {self.value:02X}'


class Set(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SET'
        self.description = 'Change Bit Number In Array Using Operation'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.bitarray = data[1]
        self.number = data[2]
        self.operation = data[3]
        self.parameters = f'Bitarray: {self.bitarray:02X}, Number: {self.number:02X}, Operation: {self.operation:02x}'


class Compare(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'COMPARE'
        self.description = 'Compare Value Against One In An Internal Array'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.index = data[2]
        self.function = data[3]
        self.value = data[4:]
        self.parameters = f"zAlign: {self.zAlign:02X}, Index: {self.index:02X}, Func: {cmp[self.function]}, " \
                          f"Value: {self.value.hex(' ')}"


class Rnd(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'RND'
        self.description = 'Random Seeding? Round?'


class CutChange(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'CUT_CHG'
        self.description = 'In Cutscene, Change Camera Angle'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.angle = data[1]
        self.parameters = f'Angle: {self.angle:02X}'


class CutOld(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'CUT_OLD'
        self.description = '???'


class CutAuto(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'CUT_AUTO'
        self.description = 'Select Inv Or Map Screen When Switching To Status Screen'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.screen = data[0]
        self.parameters = f'Screen: {self.screen:02X}'


class CutReplace(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'CUT_REPLACE'
        self.description = 'Swap All From/To Values In List Of Camera Switches If Matches Cam0 and Cam1'
        self.size = 3

    def update_vars(self, data):
        super().update_vars(data)
        self.cam0 = data[1]
        self.cam1 = data[2]
        self.parameters = f'Camera0: {self.cam0:02X}, Camera1: {self.cam1:02X}'


class CutBeSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'CUT_BE_SET'
        self.description = 'Relates To Camera Switches'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2]
        self.data2 = data[3]
        self.parameters = f'Data0: {self.data0:02X}, Data1: {self.data1:02X}, Data2: {self.data2:02X}'


class PositionSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'POS_SET'
        self.description = 'Set X,Y,Z Position'
        self.size = 8

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.xpos = data[2:4]
        self.ypos = data[4:6]
        self.zpos = data[6:]
        self.parameters = f"zAlign: {self.zAlign:02X}, X: {self.xpos.hex(' ')}, Y: {self.ypos.hex(' ')}, " \
                          f"Z: {self.zpos.hex(' ')}"


class DirectionSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'DIR_SET'
        self.description = 'Set X,Y,Z Direction'
        self.size = 8

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.xpos = data[2:4]
        self.ypos = data[4:6]
        self.zpos = data[6:]
        self.parameters = f"zAlign: {self.zAlign:02X}, X: {self.xpos.hex(' ')}, Y: {self.ypos.hex(' ')}, " \
                          f"Z: {self.zpos.hex(' ')}"


class SetVib0(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SET_VIB0'
        self.description = '???'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.data0 = data[2:4]
        self.data1 = data[4:]
        self.parameters = f"zAlign: {self.zAlign:02X}, Data0: {self.data0.hex(' ')}, Data1: {self.data1.hex(' ')}"


class SetVib1(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SET_VIB1'
        self.description = '???'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2:4]
        self.data2 = data[4:]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1.hex(' ')}, Data1: {self.data2.hex(' ')}"


class SetVibFade(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SET_VIB_FADE'
        self.description = '???'
        self.size = 8

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.data0 = data[2]
        self.data1 = data[3]
        self.data2 = data[4:6]
        self.data3 = data[6:]
        self.parameters = f"zAlign: {self.zAlign:02X}, Data0: {self.data0:02X}, Data1: {self.data1:02X}, " \
                          f"Data2: {self.data2.hex(' ')}, Data3: {self.data3.hex(' ')}"


class RbjSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'RBJ_SET'
        self.description = '???'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.parameters = f'Data: {self.data0:02X}'


class MessageOn(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'MSG_ON'
        self.description = 'Show Message?'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.msgID = data[1]
        self.data0 = data[2:4]
        self.data1 = data[4:]
        self.parameters = f"MSGID: {self.msgID:02X}, Data0: {self.data0.hex(' ')}, Data1: {self.data1.hex(' ')}"


class RainSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'RAIN_SET'
        self.description = ''
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.parameters = f'Data: {self.data0:02X}'


class MessageOff(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'MSG_OFF'
        self.description = 'Clears Message Off Screen?'


class ShakeOn(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SHAKE_ON'
        self.description = 'Starts Screen Shake?'
        self.size = 3

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2]
        self.parameters = f'Data0: {self.data0:02X}, Data1: {self.data1:02X}'


class WeaponChange(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'WEAPON_CHG'
        self.description = 'Checks Player Inventory For Item ID'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.itemid = data[1]
        self.parameters = f'ItemID: {self.itemid:02X}'


class DoorModelSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'DOOR_MDL_SET'
        self.description = 'Set Door Model'
        self.size = 22

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2]
        self.data2 = data[3]
        self.data3 = data[4]
        self.data4 = data[5]
        self.data5 = data[6:8]
        self.data6 = data[8:10]
        self.data7 = data[10:12]
        self.data8 = data[12:14]
        self.data9 = data[14:16]
        self.data10 = data[16:18]
        self.data11 = data[18:20]
        self.data12 = data[20:]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1:02X}, Data2: {self.data2:02X}, " \
                          f"Data3: {self.data3:02X}, Data4: {self.data4:02X}, Data5: {self.data5.hex(' ')}, " \
                          f"Data6: {self.data6.hex(' ')}, Data7: {self.data7.hex(' ')}, Data8: {self.data8.hex(' ')}," \
                          f" Data9: {self.data9.hex(' ')}, Data10: {self.data10.hex(' ')}, " \
                          f"Data11: {self.data11.hex(' ')}, Data12: {self.data12.hex(' ')}"


class D61OP(IntEnum):
    OPCODE = 0
    AOT = 1
    SCE = 2
    SAT = 3
    NFLOOR = 4
    SUPER = 5
    XPOS = 6
    ZPOS = 8
    WIDTH = 10
    DEPTH = 12
    NXPOS = 14
    NYPOS = 16
    NZPOS = 18
    NYDIR = 20
    NSTAGE = 22
    NROOM = 23
    NCUT = 24
    NNFLOOR = 25
    DO2 = 26
    ANIM = 27
    SOUND = 28
    KEYID = 29
    KEYTYPE = 30
    FREE = 31
    SIZE = 32


class DoorAOTSet(AOTOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'DOOR_AOT_SET'
        self.description = 'Door Added To Room Objects List'
        self.size = 32

    def update_vars(self, data):
        super().update_vars(data)
        self.nxpos = data[14:16]
        self.nypos = data[16:18]
        self.nzpos = data[18:20]
        self.nydir = data[20:22]
        self.nstage = data[22]
        self.nroom = data[23]
        self.ncut = data[24]
        self.nnfloor = data[25]
        self.do2 = data[26]
        self.anim = data[27]
        self.sound = data[28]
        self.keyid = data[29]
        self.keytype = data[30]
        self.free = data[31]
        self.parameters = f"AOT: {self.aot:02X}, SCE: {sce[self.sce]}, SAT: {get_sat_flags(self.sat)}, NFloor: {self.nfloor:02X}, "\
                          f"SUPER: {self.super:02X}, XPOS: {self.xpos.hex(' ')}, ZPOS: {self.zpos.hex(' ')}, " \
                          f"Width: {self.width.hex(' ')}, Depth: {self.depth.hex(' ')}, NextX: {self.nxpos.hex(' ')}, "\
                          f"NextY: {self.nypos.hex(' ')}, NextZ: {self.nzpos.hex(' ')}, " \
                          f"NextYDIR: {self.nydir.hex(' ')}, NextStage: {self.nstage:02X}, " \
                          f"NextRoom: {self.nroom:02X}, NextCut: {self.ncut:02X}, NextNFloor: {self.nnfloor:02X}, " \
                          f"DO2: {self.do2:02X}, Anim: {self.anim:02X}, Sound: {self.sound:02X}, " \
                          f"KeyID: {self.keyid:02X}, KeyType: {self.keytype:02X}, Free: {self.free:02X}"

    def update_doorname(self, roomname):
        self.doorname = ''
        with open('jsonfiles/roomdoors.json', 'r') as file:
            doorsdict = json.load(file)
        if roomname not in doorsdict.keys():
            return
        test = f'R{self.nstage+1}{self.nroom:02X}'
        if roomname == 'Scenario Start':
            self.doorname = f'CANNOTCHANGE:{roomnames[test]} Door, CAM:{self.ncut}'
            return
        for entry in doorsdict[roomname]:
            if self.nstage == 255 and self.doorid == entry['id']:
                self.doorname = f"{entry['from']}:NOT SET-{self.doorid}"
                return
            if entry['from'] == roomnames[test]:
                self.doorname = f"{entry['from']}:{roomnames[test]} Door, CAM:{self.ncut}"

    def set_connection(self, connector):
        self.connected_door = connector


class D62OP(IntEnum):
    OPCODE = 0
    AOT = 1
    SCE = 2
    SAT = 3
    NFLOOR = 4
    SUPER = 5
    XPOS0 = 6
    ZPOS0 = 8
    XPOS1 = 10
    ZPOS1 = 12
    XPOS2 = 14
    ZPOS2 = 16
    XPOS3 = 18
    ZPOS3 = 20
    NXPOS = 22
    NYPOS = 24
    NZPOS = 26
    NYDIR = 28
    NSTAGE = 30
    NROOM = 31
    NCUT = 32
    NNFLOOR = 33
    DO2 = 34
    ANIM = 35
    SOUND = 36
    KEYID = 37
    KEYTYPE = 38
    FREE = 39
    SIZE = 40


class DoorAOTSet4P(AOT4POpcode):
    def __init__(self):
        super().__init__()
        self.name = 'DOOR_AOT_SET_4P'
        self.description = 'This Object Is Added To Room Objects List'
        self.size = 40

    def update_vars(self, data):
        super().update_vars(data)
        self.nxpos = data[22:24]
        self.nypos = data[24:26]
        self.nzpos = data[26:28]
        self.nydir = data[28:30]
        self.nstage = data[30]
        self.nroom = data[31]
        self.ncut = data[32]
        self.nnfloor = data[33]
        self.do2 = data[34]
        self.anim = data[35]
        self.sound = data[36]
        self.keyid = data[37]
        self.keytype = data[38]
        self.free = data[39]
        self.parameters = f"AOT: {self.aot:02X}, SCE: {sce[self.sce]}, SAT: {get_sat_flags(self.sat)}, NFloor: {self.nfloor:02X}, "\
                          f"SUPER: {self.super:02X}, XPOS0: {self.xpos0.hex(' ')}, ZPOS0: {self.zpos0.hex(' ')}, " \
                          f"XPOS1: {self.xpos1.hex(' ')}, ZPOS1: {self.zpos1.hex(' ')}, XPOS2: {self.xpos2.hex(' ')}, "\
                          f"XPOS3: {self.xpos3.hex(' ')}, ZPOS3: {self.zpos3.hex(' ')}, PXPOS: {self.nxpos.hex(' ')}, "\
                          f"PYPOS: {self.nypos.hex(' ')}, PZPOS: {self.nzpos.hex(' ')}, PDIR: {self.nydir.hex(' ')}, " \
                          f"NextStage: {self.nstage:02X}, NextRoom: {self.nroom:02X}, NextCut: {self.ncut:02X}, " \
                          f"NextNFloor: {self.nnfloor:02X}, DO2: {self.do2:02X}, Anim: {dooranim[self.anim]}, " \
                          f"Sound: {self.sound:02X}, KeyID: {self.keyid:02X}, KeyType: {self.keytype:02X}, " \
                          f"Free: {self.free:02X}"

    def update_doorname(self, roomname):
        self.doorname = ''
        with open('jsonfiles/roomdoors.json', 'r') as file:
            doorsdict = json.load(file)
        if roomname not in doorsdict.keys():
            return
        test = f'R' + str((self.nstage + 1)) + f'{self.nroom:02X}'
        if roomname == 'Scenario Start':
            self.doorname = f'CANNOTCHANGE:{roomnames[test]} Door, CAM:{self.ncut}'
            return
        for entry in doorsdict[roomname]:
            if self.nstage == 255 and self.doorid == entry['id']:
                self.doorname = f"{entry['from']}:NOT SET-{self.doorid}"
                return
            if entry['from'] == roomnames[f'R{self.nstage+1}{self.nroom:02X}']:
                self.doorname = f"{entry['from']}:{roomnames[test]} Door, CAM:{self.ncut}"

    def set_connection(self, connector):
        self.connected_door = connector


class AOTSet(AOTOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'AOT_SET'
        self.description = 'Add Non-Pickable Object To Room Objects List'
        self.size = 20

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[14:16]
        self.data1 = data[16:18]
        self.data2 = data[18:20]
        self.parameters = f"AOT: {self.aot:02X}, SCE: {sce[self.sce]}, SAT: {get_sat_flags(self.sat)}, NFloor: {self.nfloor:02X}, "\
                          f"SUPER: {self.super:02X}, XPOS: {self.xpos.hex(' ')}, ZPOS: {self.zpos.hex(' ')}, " \
                          f"Width: {self.width.hex(' ')}, Depth: {self.depth.hex(' ')}, Data0: {self.data0.hex(' ')}, "\
                          f"Data1: {self.data1.hex(' ')}, Data2: {self.data2.hex(' ')}"


class AOTSet4P(AOT4POpcode):
    def __init__(self):
        super().__init__()
        self.name = 'AOT_SET_4P'
        self.description = 'Wall Added To Room Objects List'
        self.size = 28

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[22:24]
        self.data1 = data[24:26]
        self.data2 = data[26:28]
        self.parameters = f"AOT: {self.aot:02X}, SCE: {sce[self.sce]}, SAT: {get_sat_flags(self.sat)}, NFloor: {self.nfloor:02X}, " \
                          f"SUPER: {self.super:02X}, XPOS0: {self.xpos0.hex(' ')}, ZPOS0: {self.zpos0.hex(' ')}, " \
                          f"XPOS1: {self.xpos1.hex(' ')}, ZPOS1: {self.zpos1.hex(' ')}, XPOS2: {self.xpos2.hex(' ')}, " \
                          f"XPOS3: {self.xpos3.hex(' ')}, ZPOS3: {self.zpos3.hex(' ')}, Data0: {self.data0.hex(' ')}, "\
                          f"Data1: {self.data1.hex(' ')}, Data2: {self.data2.hex(' ')}"


class AOTReset(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'AOT_RESET'
        self.description = 'Defines What To Do When Player Triggers An Event'
        self.size = 10

    def update_vars(self, data):
        super().update_vars(data)
        self.aot = data[1]
        self.data0 = data[2]
        self.data1 = data[3]
        self.data2 = data[4:6]
        self.data3 = data[6:8]
        self.data4 = data[8:10]
        self.parameters = f"AOT: {self.aot:02X}, Data0: {self.data0:02X}, Data1: {self.data1:02X}, " \
                          f"Data2: {self.data2.hex(' ')}, Data3: {self.data3.hex(' ')}, Data4: {self.data4.hex(' ')}"


class AOTOn(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'AOT_ON'
        self.description = 'Activates Object For Interaction'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.aot = data[1]
        self.parameters = f'AOT: {self.aot:02X}'


class I67OP(IntEnum):
    OPCODE = 0
    AOT = 1
    SCE = 2
    SAT = 3
    NFLOOR = 4
    SUPER = 5
    XPOS = 6
    ZPOS = 8
    WIDTH = 10
    DEPTH = 12
    ID = 14
    AMOUNT = 16
    FLAG = 18
    MDI = 20
    ACTION = 21
    SIZE = 22


class ItemAOTSet(AOTOpcode):
    def __init__(self):
        super().__init__()
        self.name = 'ITEM_AOT_SET'
        self.description = 'Item Added To Room Object List'
        self.size = 22

    def update_vars(self, data):
        super().update_vars(data)
        self.id = data[14:16]
        self.amount = data[16:18]
        self.flag = data[18:20]
        self.md1 = data[20]
        self.action = data[21]
        intid = struct.unpack('<h', self.id)[0]
        self.itemname = itemnames[intid] if intid < len(itemnames) else 'DOC'
        try:
            action = itemaction[self.action]
        except:
            action = f'ACTION_{self.action:02X}'
        self.parameters = f"AOT: {self.aot:02X}, SCE: {sce[self.sce]}, SAT: {get_sat_flags(self.sat)}, NFloor: {self.nfloor:02X}, "\
                          f"SUPER: {self.super:02X}, XPOS: {self.xpos.hex(' ')}, ZPOS: {self.zpos.hex(' ')}, " \
                          f"Width: {self.width.hex(' ')}, Depth: {self.depth.hex(' ')}, " \
                          f"Item: {self.itemname}, Amount: {self.amount.hex(' ')}, " \
                          f"Flag: {self.flag.hex(' ')}, MD1: {self.md1:02X}, Action: {action}"


class I68OP(IntEnum):
    OPCODE = 0
    AOT = 1
    SCE = 2
    SAT = 3
    NFLOOR = 4
    SUPER = 5
    XPOS0 = 6
    ZPOS0 = 8
    XPOS1 = 10
    ZPOS1 = 12
    XPOS2 = 14
    ZPOS2 = 16
    XPOS3 = 18
    ZPOS3 = 20
    ID = 22
    AMOUNT = 24
    FLAG = 26
    MDI = 28
    ACTION = 29
    SIZE = 30


class ItemAOTSet4P(AOT4POpcode):
    def __init__(self):
        super().__init__()
        self.name = 'ITEM_AOT_SET_4P'
        self.description = 'This Object Is Added To Room Objects List'
        self.size = 30

    def update_vars(self, data):
        super().update_vars(data)
        self.id = data[22:24]
        self.amount = data[24:26]
        self.flag = data[26:28]
        self.md1 = data[28]
        self.action = data[29]
        intid = struct.unpack('<h', self.id)[0]
        self.itemname = itemnames[intid] if intid < len(itemnames) else 'DOC'
        try:
            action = itemaction[self.action]
        except:
            action = f'ACTION_{self.action:02X}'
        self.parameters = f"AOT: {self.aot:02X}, SCE: {sce[self.sce]}, SAT: {get_sat_flags(self.sat)}, NFloor: {self.nfloor:02X}, " \
                          f"SUPER: {self.super:02X}, XPOS0: {self.xpos0.hex(' ')}, ZPOS0: {self.zpos0.hex(' ')}, " \
                          f"XPOS1: {self.xpos1.hex(' ')}, ZPOS1: {self.zpos1.hex(' ')}, XPOS2: {self.xpos2.hex(' ')}, " \
                          f"XPOS3: {self.xpos3.hex(' ')}, ZPOS3: {self.zpos3.hex(' ')}, " \
                          f"Item: {self.itemname}, Amount: {self.amount.hex(' ')}, " \
                          f"Flag: {self.flag.hex(' ')}, MD1: {self.md1:02X}, Action: {action}"


class KageSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'KAGE_SET'
        self.description = '???'
        self.size = 14

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2]
        self.data2 = data[3]
        self.data3 = data[4]
        self.data4 = data[5]
        self.data5 = data[6:8]
        self.data6 = data[8:10]
        self.data7 = data[10:12]
        self.data8 = data[12:14]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1:02X}, Data2: {self.data2:02X}, " \
                          f"Data3: {self.data3:02X}, Data4: {self.data4:02X}, Data5: {self.data5.hex(' ')}, " \
                          f"Data6: {self.data6.hex(' ')}, Data7: {self.data7.hex(' ')}, Data8: {self.data8.hex(' ')}"


class SuperSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SUPER_SET'
        self.description = '???'
        self.size = 16

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.data0 = data[2]
        self.data1 = data[3]
        self.data2 = data[4:6]
        self.data3 = data[6:8]
        self.data4 = data[8:10]
        self.data5 = data[10:12]
        self.data6 = data[12:14]
        self.data7 = data[14:16]
        self.parameters = f"zAlign: {self.zAlign:02X}, Data0: {self.data0:02X}, Data1: {self.data1:02X}, " \
                          f"Data2: {self.data2.hex(' ')}, Data3: {self.data3.hex(' ')}, Data4: {self.data4.hex(' ')}, "\
                          f"Data5: {self.data5.hex(' ')}, Data6: {self.data6.hex(' ')}, Data7: {self.data7.hex(' ')}"


class KeepItemCheck(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'KEEP_ITEM_CK'
        self.description = 'Check If Player Has Item In Inventory'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.id = data[1]
        self.parameters = f'Item: {itemnames[self.id]}'


class KeyCheck(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'KEY_CK'
        self.description = 'Check If Player Has Key In Inventory (?)'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2:4]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1.hex(' ')}"


class TriggerCheck(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'TRG_CK'
        self.description = 'Trigger(?)'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2:4]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1.hex(' ')}"


class SCDIdSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SCD_ID_SET'
        self.description = '???'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2:4]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1.hex(' ')}"


class ObjectModelBomb(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'OM_BOMB'
        self.description = '???'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.parameters = f"Data0: {self.data0:02X}"


class EsprOn(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'ESPR_ON'
        self.description = '2D Animation Above Background'
        self.size = 16

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2:4]
        self.data2 = data[4:6]
        self.data3 = data[6:8]
        self.data4 = data[8:10]
        self.data5 = data[10:12]
        self.data6 = data[12:14]
        self.data7 = data[14:16]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1.hex(' ')}, Data2: {self.data2.hex(' ')}, " \
                          f"Data3: {self.data3.hex(' ')}, Data4: {self.data4.hex(' ')}, Data5: {self.data5.hex(' ')}, "\
                          f"Data6: {self.data6.hex(' ')}, Data7: {self.data7.hex(' ')}"


class EsprOn2(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'ESPR_ON2'
        self.description = '???'
        self.size = 18

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.data0 = data[2]
        self.data1 = data[3]
        self.data2 = data[4:6]
        self.data3 = data[6:8]
        self.data4 = data[8:10]
        self.data5 = data[10:12]
        self.data6 = data[12:14]
        self.data7 = data[14:16]
        self.data8 = data[16:18]
        self.parameters = f"zAlign: {self.zAlign:02X}, Data0: {self.data0:02X}, Data1: {self.data1:02X}, Data2: " \
                          f"{self.data2.hex(' ')}, Data3: {self.data3.hex(' ')}, Data4: {self.data4.hex(' ')}, " \
                          f"Data5: {self.data5.hex(' ')}, Data6: {self.data6.hex(' ')}, Data7: {self.data7.hex(' ')}, "\
                          f"Data8: {self.data8.hex(' ')}"


class Espr3DOn(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'ESPR_3D_ON'
        self.description = '3D Animation Above Background'
        self.size = 22

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2:4]
        self.data2 = data[4:6]
        self.data3 = data[6:8]
        self.data4 = data[8:10]
        self.data5 = data[10:12]
        self.data6 = data[12:14]
        self.data7 = data[14:16]
        self.data8 = data[16:18]
        self.data9 = data[18:20]
        self.data10 = data[20:22]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1.hex(' ')}, Data2: {self.data2.hex(' ')}, " \
                          f"Data3: {self.data3.hex(' ')}, Data4: {self.data4.hex(' ')}, Data5: {self.data5.hex(' ')}, "\
                          f"Data6: {self.data6.hex(' ')}, Data7: {self.data7.hex(' ')}, Data8: {self.data8.hex(' ')}, "\
                          f"Data9: {self.data9.hex(' ')}, Data10: {self.data10.hex(' ')}"


class Espr3DOn2(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'ESPR_3D_ON2'
        self.description = '???'
        self.size = 24

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.data0 = data[2]
        self.data1 = data[3]
        self.data2 = data[4:6]
        self.data3 = data[6:8]
        self.data4 = data[8:10]
        self.data5 = data[10:12]
        self.data6 = data[12:14]
        self.data7 = data[14:16]
        self.data8 = data[16:18]
        self.data9 = data[18:20]
        self.data10 = data[20:22]
        self.data11 = data[22:24]
        self.parameters = f"zAlign: {self.zAlign:02X}, Data0: {self.data0:02X}, Data1: {self.data1:02X}, Data2: " \
                          f"{self.data2.hex(' ')}, Data3: {self.data3.hex(' ')}, Data4: {self.data4.hex(' ')}, " \
                          f"Data5: {self.data5.hex(' ')}, Data6: {self.data6.hex(' ')}, Data7: {self.data7.hex(' ')}, " \
                          f"Data8: {self.data8.hex(' ')}, Data9: {self.data9.hex(' ')}, " \
                          f"Data10: {self.data10.hex(' ')}, Data11: {self.data11.hex(' ')}"


class EsprKill(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'ESPR_KILL'
        self.description = '???'
        self.size = 5

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2]
        self.data2 = data[3]
        self.data3 = data[4]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1:02X}, Data2: {self.data2:02X}, " \
                          f"Data3: {self.data3:02X}"


class EsprKill2(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'ESPR_KILL2'
        self.description = '???'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.parameters = f'Data: {self.data0:02X}'


class EsprKillAll(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'ESPR_KILL_ALL'
        self.description = '???'
        self.size = 3

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2]
        self.parameters = f'Data0: {self.data0:02X}, Data1 {self.data1:02X}'


class SEOn(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SE_ON'
        self.description = '???'
        self.size = 12

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2:4]
        self.data2 = data[4:6]
        self.data3 = data[6:8]
        self.data4 = data[8:10]
        self.data5 = data[10:12]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1.hex(' ')}, Data2: {self.data2.hex(' ')}, " \
                          f"Data3: {self.data3.hex(' ')}, Data4: {self.data4.hex(' ')}, Data5: {self.data5.hex(' ')}"


class BgmCtl(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'BGM_CTL'
        self.description = 'Related To Music Init'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2]
        self.data2 = data[3]
        self.data3 = data[4]
        self.data4 = data[5]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1:02X}, Data2: {self.data2:02X}, " \
                          f"Data3: {self.data3:02X}, Data4: {self.data4:02X}"


class XAOn(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'XA_ON'
        self.description = 'Plays Sound (Character Voice For Example)'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.channel = data[1]
        self.soundid = data[2:4]
        self.parameters = f"Channel: {self.channel:02X}, SoundID: {self.soundid.hex(' ').upper()}"


class MovieOn(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'MOVIE_ON'
        self.description = 'Play Movie'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.id = data[1]
        self.parameters = f'MovieID: {self.id:02X}'


class BgmTblSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'BGM_TBL_SET'
        self.description = '???'
        self.size = 6

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.data0 = data[2]
        self.data1 = data[3]
        self.data2 = data[4:6]
        self.parameters = f"zAlign: {self.zAlign:02X}, Data0: {self.data0:02X}, Data1: {self.data1:02X}, " \
                          f"Data2: {self.data2.hex(' ')}"


class StatusOn(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'STATUS_ON'
        self.description = '???'


class EnemyModelSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'EM_SET'
        self.description = 'Entity Model (Enemy, Other Character)'
        self.size = 24

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.data0 = data[2]
        self.data1 = data[3]
        self.data2 = data[4:6]
        self.data3 = data[6:8]
        self.data4 = data[8]
        self.data5 = data[9]
        self.data6 = data[10]
        self.data7 = data[11]
        self.data8 = data[12:14]
        self.data9 = data[14:16]
        self.data10 = data[16:18]
        self.data11 = data[18:20]
        self.data12 = data[20:22]
        self.data13 = data[22:24]
        self.parameters = f"zAlign: {self.zAlign:02X}, Data0: {self.data0:02X}, Data1: {self.data1:02X}, " \
                          f"Data2: {self.data2.hex(' ')}, Data3: {self.data3.hex(' ')}, Data4: {self.data4:02X}, " \
                          f"Data5: {self.data5:02X}, Data6: {self.data6:02X}, Data7: {self.data7:02X}, " \
                          f"Data8: {self.data8.hex(' ')}, Data9: {self.data9.hex(' ')}, " \
                          f"Data10: {self.data10.hex(' ')}, Data11: {self.data11.hex(' ')}, " \
                          f"Data12: {self.data12.hex(' ')}, Data13: {self.data13.hex(' ')}"


class MizuDiv(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'MIZU_DIV'
        self.description = 'Related To 3D Model Creation(?)'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.parameters = f'Data: {self.data0:02X}'


class ObjectModelSet(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'OM_SET'
        self.description = 'Object Model For Pickable Item'
        self.size = 40

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2]
        self.data2 = data[3]
        self.data3 = data[4:6]
        self.data4 = data[6:8]
        self.data5 = data[8]
        self.data6 = data[9]
        self.data7 = data[10]
        self.data8 = data[11]
        self.data9 = data[12:14]
        self.data10 = data[14:16]
        self.data11 = data[16:18]
        self.data12 = data[18:20]
        self.data13 = data[20:22]
        self.data14 = data[22:24]
        self.data15 = data[24:26]
        self.data16 = data[26:28]
        self.data17 = data[28:30]
        self.data18 = data[30:32]
        self.data19 = data[32:34]
        self.data20 = data[34:36]
        self.data21 = data[36:38]
        self.data22 = data[38:40]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1:02X}, Data2: {self.data2:02X}, " \
                          f"Data3: {self.data3.hex(' ')}, Data4: {self.data4.hex(' ')}, Data5: {self.data5:02X}, " \
                          f"Data6: {self.data6:02X}, Data7: {self.data7:02X}, Data8: {self.data8:02X}, " \
                          f"Data9: {self.data9.hex(' ')}, Data10: {self.data10.hex(' ')}, " \
                          f"Data11: {self.data11.hex(' ')}, Data12: {self.data12.hex(' ')}, " \
                          f"Data13: {self.data13.hex(' ')}, Data14: {self.data14.hex(' ')}, " \
                          f"Data15: {self.data15.hex(' ')}, Data16: {self.data16.hex(' ')}, " \
                          f"Data17: {self.data17.hex(' ')}, Data18: {self.data18.hex(' ')}, " \
                          f"Data19: {self.data13.hex(' ')}, Data19: {self.data19.hex(' ')}, " \
                          f"Data20: {self.data20.hex(' ')}, Data21: {self.data21.hex(' ')}, " \
                          f"Data22: {self.data22.hex(' ')}"


class PlcMotion(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'PLC_MOTION'
        self.description = '???'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2]
        self.data2 = data[3]
        self.parameters = f'Data0: {plcaction[self.data0]}, Data1: {self.data1:02X}, Data2: {self.data2:02X}'


class PlcDestination(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'PLC_DEST'
        self.description = '???'
        self.size = 8

    def update_vars(self, data):
        super().update_vars(data)
        self.zAlign = data[1]
        self.data0 = data[2]
        self.data1 = data[3]
        self.data2 = data[4:6]
        self.data3 = data[6:8]
        self.parameters = f"zAlign: {self.zAlign:02X}, Data0: {self.data0:02X}, Data1: {self.data1:02X}, " \
                          f"Data2: {self.data2.hex(' ')}, Data3: {self.data3.hex(' ')}"


class PlcNeck(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'PLC_NECK'
        self.description = '???'
        self.size = 10

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2:4]
        self.data2 = data[4:6]
        self.data3 = data[6:8]
        self.data4 = data[8:10]
        self.parameters = f"Data0: {plcneck[self.data0]}, Data1: {self.data1.hex(' ')}, Data2: {self.data2.hex(' ')}, " \
                          f"Data3: {self.data3.hex(' ')}, Data4: {self.data4.hex(' ')}"


class PlcReturn(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'PLC_RETURN'
        self.description = '???'


class PlcFlag(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'PLC_FLAG'
        self.description = '???'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2:4]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1.hex(' ')}"


class PlcGun(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'PLC_GUN'
        self.description = '???'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.parameters = f'Data: {self.data0:02X}'


class PlcGunEff(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'PLC_GUN_EFF'
        self.description = '???'


class PlcStop(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'PLC_STOP'
        self.description = '???'


class PlcRot(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'PLC_ROT'
        self.description = '???'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2:4]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1.hex(' ')}"


class PlcCount(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'PLC_CNT'
        self.description = '???'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.parameters = f'Data: {self.data0:02X}'


class SplcReturn(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SPLC_RETURN'
        self.description = '???'


class SplcSCE(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SPLC_SCE'
        self.description = '???'


class PlcSCE(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'PLC_SCE'
        self.description = '???'


class SplWeaponChange(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'SPL_WPN_CHG'
        self.description = '???'


class PlcMotNum(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'PLC_MOT_NUM'
        self.description = '???'
        self.size = 4

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.data1 = data[2:4]
        self.parameters = f"Data0: {self.data0:02X}, Data1: {self.data1.hex(' ')}"


class EnemyModelReset(Opcode):
    def __init__(self):
        super().__init__()
        self.name = 'EM_RESET'
        self.description = '???'
        self.size = 2

    def update_vars(self, data):
        super().update_vars(data)
        self.data0 = data[1]
        self.parameters = f"Data0: {self.data0:02X}"


opcodes = {
    0x00: NOP0, 0x01: EvtEnd, 0x02: EvtNext, 0x03: EvtChain, 0x04: EvtExec, 0x05: EvtKill, 0x06: IfElseCheck,
    0x07: ElseCheck, 0x08: EndIf, 0x09: Sleep, 0x0A: Sleeping, 0x0B: WSleep, 0x0C: WSleeping, 0x0D: For, 0x0E: For2,
    0x0F: Next, 0x10: While, 0x11: EndWhile, 0x12: Do, 0x13: EndDo, 0x14: Switch, 0x15: Case, 0x16: Default,
    0x17: EndSwitch, 0x18: Goto, 0x19: Gosub, 0x1A: Return, 0x1B: Break, 0x1C: BreakPoint, 0x1D: WorkCopy, 0x1E: Save,
    0x1F: Copy, 0x20: Calc, 0x21: Calc2, 0x22: EvtCut, 0x23: NOP1, 0x24: ChaserEvtClr, 0x25: OpenMap, 0x26: PointAdd,
    0x27: DoorCheck, 0x28: DieDemoOn, 0x29: DirCK, 0x2A: PartsSet, 0x2B: VloopSet, 0x2C: OTABESet, 0x2D: LineStart,
    0x2E: LineMain, 0x2F: LineEnd, 0x30: LightPosSet, 0x31: LightKidoSet, 0x32: LightColorSet, 0x33: AheadRoomSet,
    0x34: EsprCtr, 0x35: BgmTableCheck, 0x36: ItemGetCheck, 0x37: OmRev, 0x38: ChaserLifeInit, 0x39: PartsBomb,
    0x3A: PartsDown, 0x3B: ChaserItemSet, 0x3C: WeaponChangeOld, 0x3D: SelectEventOn, 0x3E: ItemLost, 0x3F: FlrSet,
    0x40: MemberSet, 0x41: MemberSet2, 0x42: MemberCopy, 0x43: MemberCompare, 0x44: MemberCalc, 0x45: MemberCalc2,
    0x46: FadeSet, 0x47: WorkSet, 0x48: SpeedSet, 0x49: AddSpeed, 0x4A: AddASpeed, 0x4B: AddVSpeed, 0x4C: EvalCheck,
    0x4D: Set, 0x4E: Compare, 0x4F: Rnd, 0x50: CutChange, 0x51: CutOld, 0x52: CutAuto, 0x53: CutReplace, 0x54: CutBeSet,
    0x55: PositionSet, 0x56: DirectionSet, 0x57: SetVib0, 0x58: SetVib1, 0x59: SetVibFade, 0x5A: RbjSet,
    0x5B: MessageOn, 0x5C: RainSet, 0x5D: MessageOff, 0x5E: ShakeOn, 0x5F: WeaponChange, 0x60: DoorModelSet,
    0x61: DoorAOTSet, 0x62: DoorAOTSet4P, 0x63: AOTSet, 0x64: AOTSet4P, 0x65: AOTReset, 0x66: AOTOn, 0x67: ItemAOTSet,
    0x68: ItemAOTSet4P, 0x69: KageSet, 0x6A: SuperSet, 0x6B: KeepItemCheck, 0x6C: KeyCheck, 0x6D: TriggerCheck,
    0x6E: SCDIdSet, 0x6F: ObjectModelBomb, 0x70: EsprOn, 0x71: EsprOn2, 0x72: Espr3DOn, 0x73: Espr3DOn2, 0x74: EsprKill,
    0x75: EsprKill2, 0x76: EsprKillAll, 0x77: SEOn, 0x78: BgmCtl, 0x79: XAOn, 0x7A: MovieOn, 0x7B: BgmTblSet,
    0x7C: StatusOn, 0x7D: EnemyModelSet, 0x7E: MizuDiv, 0x7F: ObjectModelSet, 0x80: PlcMotion, 0x81: PlcDestination,
    0x82: PlcNeck, 0x83: PlcReturn, 0x84: PlcFlag, 0x85: PlcGun, 0x86: PlcGunEff, 0x87: PlcStop, 0x88: PlcRot,
    0x89: PlcCount, 0x8A: SplcReturn, 0x8B: SplcSCE, 0x8C: PlcSCE, 0x8D: SplWeaponChange, 0x8E: PlcMotNum,
    0x8F: EnemyModelReset
}
