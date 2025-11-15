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

class CHIP_8():
    _Memory = _ByteList(l=0x1000)
    _Reg = _ByteList(l=0x10)
    _Reg_I = _ByteList(l=1,b=2)
    _PC = _BinVal(v=0x200, b=2)
    _ST = []

    def GetMemBytes(self,b=1, i=True):
        d = ""
        for x in range(b):
            d = f"{d}{(self._Memory[self._PC+x]):02X}"
        if i:
            self._PC += b
        return int(d,16)

    def NOP(self):
        print("NOP")
        pass
    def EXIT(self):
        self._PC = 0xfff
    def JMP(self):
        print("JMP")
        ad = self.GetMemBytes(b=2)
        self._PC.Set(ad)
    def CALL(self):
        print("CALL")
        ad = self.GetMemBytes(b=2)
        self._ST.insert(0,self._PC.VALUE)
        self._PC.Set(ad)
    def RET(self):
        print("RET")
        self._PC.Set(self._ST[0])
        self._ST.remove(self._ST[0])
    Instrucs = {
            0x00:NOP,
            0x01:EXIT,
            0x10:JMP,
            0x11:CALL,
            0x12:RET
        }
    def __init__(self, dumpFile):
        #Load ROM
        self._ROM_DATA = getBytes(_ROM_F)
        self._DMP_F = dumpFile
        for x in range(len(self._ROM_DATA)):
            self._Memory[x] = self._ROM_DATA[x]

    def Cycle(self):
        print("------")
        print(f"{self._PC.VALUE:02X}")
        op = self.GetMemBytes()
        self.Instrucs[op](self)

    def DumpRam(self):
        open(self._DMP_F,"w").close
        with open(self._DMP_F, "wb") as File:
            for x in range(len(self._Memory)):
                File.write(self._Memory[x].to_bytes(1,"big"))
        File.close()