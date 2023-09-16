import json

with open('jsonfiles/rooms.json', 'r') as loadfile:
    roomnames = json.load(loadfile)

with open('jsonfiles/items.json', 'r') as loadfile:
    itemnames = json.load(loadfile)

with open('jsonfiles/vars.json', 'r') as loadfile:
    variables = json.load(loadfile)
    set_ck_flags = variables['set_ck_flags']
    sce = variables['sce']
    sceproto = variables['sceproto']
    work = {int(key):value for key, value in variables['work'].items()}
    spdset = variables['spdset']
    memb_func = variables['memb_func']
    cmp = variables['cmp']
    plcneck = variables['plcneck']
    plcaction = variables['plcaction']
    itemaction = {int(key):value for key, value in variables['itemaction'].items()}
    calcop = variables['calcop']
    bgmid = variables['bgmid']
    bgmop = variables['bgmop']
    bgmtype = variables['bgmtype']
    sevab = variables['sevab']
    dooranim = {int(key):value for key, value in variables['dooranim'].items()}
    satflags = {int(key):value for key, value in variables['satflags'].items()}


def get_sat_flags(flagvalue):
    if flagvalue == 0:
        return 'AUTO'
    return '|'.join(value for key, value in satflags.items() if flagvalue & key == key)


class Item:
    def __init__(self, iteminfo: bytes):
        self.opcode = iteminfo[0]
        self.aot = iteminfo[1]
        self.sce = iteminfo[2]
        self.sat = iteminfo[3]
        self.nfloor = iteminfo[4]
        self.super = iteminfo[5]

    def update_name(self):
        itemtype = int.from_bytes(self.type, 'little')
        if itemtype < len(itemnames):
            self.typename = itemnames[itemtype]
        else:
            self.typename = 'DOCUMENT'

    def createbytesobj(self):
        pass


class Item67(Item):
    def __init__(self, iteminfo):
        super().__init__(iteminfo)
        self.xpos = iteminfo[6:8]
        self.ypos = iteminfo[8:10]
        self.zpos = iteminfo[10:12]
        self.rotation = iteminfo[12:14]
        self.type = iteminfo[14:16]
        self.update_name()
        self.quantity = iteminfo[16:18]
        self.flag = iteminfo[18:20]
        self.mdi = iteminfo[20]
        self.action = iteminfo[21]

    def createbytesobj(self):
        bytesobj = bytearray()
        bytesobj.append(self.opcode)
        bytesobj.append(self.aot)
        bytesobj.append(self.sce)
        bytesobj.append(self.sat)
        bytesobj.append(self.nfloor)
        bytesobj.append(self.super)
        bytesobj.extend(self.xpos)
        bytesobj.extend(self.ypos)
        bytesobj.extend(self.zpos)
        bytesobj.extend(self.rotation)
        bytesobj.extend(self.type)
        bytesobj.extend(self.quantity)
        bytesobj.extend(self.flag)
        bytesobj.append(self.mdi)
        bytesobj.append(self.action)
        return bytesobj


class Item68(Item):
    def __init__(self, iteminfo):
        super().__init__(iteminfo)
        self.xpos0 = iteminfo[6:8]
        self.zpos0 = iteminfo[8:10]
        self.xpos1 = iteminfo[10:12]
        self.zpos1 = iteminfo[12:14]
        self.xpos2 = iteminfo[14:16]
        self.zpos2 = iteminfo[16:18]
        self.xpos3 = iteminfo[18:20]
        self.zpos3 = iteminfo[20:22]
        self.type = iteminfo[22:24]
        self.update_name()
        self.quantity = iteminfo[24:26]
        self.flag = iteminfo[26:28]
        self.mdi = iteminfo[28]
        self.action = iteminfo[29]

    def createbytesobj(self):
        bytesobj = bytearray()
        bytesobj.append(self.opcode)
        bytesobj.append(self.aot)
        bytesobj.append(self.sce)
        bytesobj.append(self.sat)
        bytesobj.append(self.nfloor)
        bytesobj.append(self.super)
        bytesobj.extend(self.xpos0)
        bytesobj.extend(self.zpos0)
        bytesobj.extend(self.xpos1)
        bytesobj.extend(self.zpos1)
        bytesobj.extend(self.xpos2)
        bytesobj.extend(self.zpos2)
        bytesobj.extend(self.xpos3)
        bytesobj.extend(self.zpos3)
        bytesobj.extend(self.type)
        bytesobj.extend(self.quantity)
        bytesobj.extend(self.flag)
        bytesobj.append(self.mdi)
        bytesobj.append(self.action)
        return bytesobj


def get_keydata():
    with open('jsonfiles/keydata.json', 'r') as file:
        keydata = json.load(file)
    return keydata


def get_checklists():
    with open('jsonfiles/musthaves.json', 'r') as file:
        musthaves = json.load(file)

    with open('jsonfiles/optionals.json', 'r') as file:
        optionals = json.load(file)
    return musthaves, optionals


def get_keyinfo():
    with open('jsonfiles/keyitems.json', 'r') as file:
        keyitems = json.load(file)

    with open('jsonfiles/combokeys.json', 'r') as file:
        combokeys = json.load(file)

    return keyitems, combokeys

roomitemflags = {
    0x73: [['Pharmacy Room 2', 'Stagla Gas']],
    0x74: [['Pharmacy Room 2', 'Stagla Gas']],
    0x75: [['Pharmacy Room 2', 'Stagla Gas']],
    0x4B: [['Pharmacy Room 2', 'Power Station']],
    0x4C: [['Pharmacy Room 2', 'Power Station']],
    0x7F: [['Pharmacy Room 2', 'Power Station']],
    0x34: [['RPD Big Office', 'RPD Meeting Room']],
    0x2B: [['Restaurant', 'Press Offices'], ['Factory Save 1F', 'Water Puzzle']],
    0x6D: [['Restaurant', 'Press Offices']],
    0x3C: [['Stagla Gas Outside', 'Power Station Access', 'Stagla Escape']],
    0x3D: [['Stagla Gas Outside', 'Power Station Access', 'Stagla Escape']],
    0x29: [['Municipal Alley', 'Fire Hose Alley']],
    0x2A: [['Municipal Alley', 'Fire Hose Alley']],
    0x4D: [['Municipal Alley', 'Fire Hose Alley']],
    0x63: [['ClockTower Dining Room', 'ClockTower Library']],
    0x5f: [['ClockTower Chapel', 'ClockTower Bedroom']],
    0x60: [['ClockTower Chapel', 'ClockTower Bedroom']],
    0x61: [['ClockTower Chapel', 'ClockTower Bedroom']],
    0x62: [['ClockTower Chapel', 'ClockTower Bedroom']],
    0x35: [['RPD Corridor', 'RPD STARS Corridor']],
    0x36: [['RPD Corridor', 'RPD STARS Corridor']],
    0x09: [['Room 401', 'Laboratory']],
    0x0A: [['Room 401', 'Laboratory']],
    0x56: [['Laboratory', 'Data Room']],
    0x50: [['Factory Save 1F', 'Water Puzzle']],
    0x51: [['Factory Save 1F', 'Water Puzzle']],
    0x52: [['Factory Save 1F', 'Water Puzzle']],
    0x2E: [['Factory Save 1F', 'Water Puzzle']],
    0x2F: [['Factory Save 1F', 'Water Puzzle']],
}

defaultpath = ''
workingpath = ''
