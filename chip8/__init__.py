from pathlib import Path

_BASE_DIR = Path(__file__).parent
_ROM_F =  _BASE_DIR/"ROM.hex"

def _CheckBits(v,b):
    if v>=0 and v<=(2**b)-1:
        return True
    else:
        return False

def _CorrectBytes(v, b=1):
    if _CheckBits(v,b):
        return v
    else:
        return 0x00

class _BinVal():
    def __init__(self,v=0, b=1, bi=None):
        if bi:
            self.Bits = bi
        else:
            self.Bits = b*8
        self.VALUE = _CorrectBytes(v, self.Bits)
    def Set(self, v=0):
        self.VALUE = _CorrectBytes(v, self.Bits)
    def Get(self):
        return self.VALUE
    def __repr__(self):
        return self.VALUE
    def __str__(self):
        return str(self.VALUE)
    def __int__(self):
        return self.VALUE
    def __iadd__(self, v):
        self.VALUE += v
        return self
    def __add__(self,v):
        return self.VALUE + v

class _ByteList():#Handle setting of _BinValues
    def __init__(self, l=8, b=1):
        self.LIST = [_BinVal(b=b) for _ in range(l)]
    def __getitem__(self, i):
        return self.LIST[i].Get()
    def __setitem__(self, i, v):
        self.LIST[i].Set(v)
    def __len__(self):
        return len(self.LIST)
    
def getBytes(f):
    l = []
    with open(f, "rb") as File:
        for x in File.read():
            l.append(x)
    return l

def hexSpilt(v):
    h = f"{v:02X}"
    return int(h[0],16), int(h[1], 16)

InstrucsNH = {
            "NOP":[0x00,1],
            "EXIT":[0x01,1],
            "JMP":[0x10,3],
            "CALL":0x11,
            "RET":0x12,
            "SE":0x13,
            "SNE":0x14,
            "VSE":0x15,
            "VSNE":0x16,
            "JMPV":0x17,
            "LDVB":0x20
        }
def GetInstrucName(n=0x0):
    for x in InstrucsNH:
        if InstrucsNH[x]==n:
            return x
    return "NOP"

class CHIP_8():
    _Memory = _ByteList(l=0x1000)
    _Reg = _ByteList(l=0x10)
    _Reg_I = _ByteList(l=1,b=2)
    _PC = _BinVal(v=0x200, b=2)
    _ST = []
    _SKP = False
    stop = False

    def GetMemBytes(self,b=1, i=True):
        d = ""
        for x in range(b):
            d = f"{d}{(self._Memory[self._PC+x]):02X}"
        output(action="READ", d={"ad":self._PC+1,"val":self._Memory[self._PC+x]})
        if i:
            self._PC += b
        
        return int(d,16)

    def NOP(self):
        pass
    def EXIT(self):
        self.stop = True
    def JMP(self):
        ad = self.GetMemBytes(b=2)
        self._PC.Set(ad)
    def CALL(self):
        ad = self.GetMemBytes(b=2)
        self._ST.insert(0,self._PC.VALUE)
        self._PC.Set(ad)
    def RET(self):
        self._PC.Set(self._ST[0])
        self._ST.remove(self._ST[0])
    def SE(self):
        vx = self.GetMemBytes()
        vk = self.GetMemBytes()
        if self._Reg[r]==v:
            self._SKP = True
    def SNE(self):
        vx = self.GetMemBytes()
        kk = self.GetMemBytes()
        if self._Reg[r]!=v:
            self._SKP = True
    def VSE(self):
        vx = self.GetMemBytes()
        vy = self._Reg[self.GetMemBytes()]
        if vx==vy:
            self._SKP = True
    def VSNE(self):
        vx = self._Reg[self.GetMemBytes()]
        vy = self._Reg[self.GetMemBytes()]
        if vx!=vy:
            self._SKP = True
    def JMPV(self):
        vx = self._Reg[self.GetMemBytes()]
        n = self.GetMemBytes(b=2)
        self._PC.Set(n+vx)
    def LDVB(self):
        x = self.GetMemBytes()
        kk = self.GetMemBytes()
        self._Reg[x] = kk

    Instrucs = {
            0x00:NOP,
            0x01:EXIT,
            0x10:JMP,
            0x11:CALL,
            0x12:RET,
            0x13:SE,
            0x14:SNE,
            0x15:VSE,
            0x16:VSNE,
            0x17:JMPV,
            0x20:LDVB
        }
    def __init__(self, dumpFile, programFile):
        #Load ROM
        self._ROM_DATA = getBytes(_ROM_F)
        self._DMP_F = dumpFile
        for x in range(len(self._ROM_DATA)):
            self._Memory[x] = self._ROM_DATA[x]
        self._PROGRAM_DATA = getBytes(programFile)
        for x in range(len(self._PROGRAM_DATA)):
            self._Memory[x+0x200] = self._PROGRAM_DATA[x]
    def Cycle(self):
        self.op = self.GetMemBytes()
        output(action="DECODE",d={"val":self.op,"ins":GetInstrucName(self.op)})
        self.Instrucs[self.op](self)

    def DumpRam(self):
        open(self._DMP_F,"w").close
        with open(self._DMP_F, "wb") as File:
            for x in range(len(self._Memory)):
                File.write(self._Memory[x].to_bytes(1,"big"))
        File.close()