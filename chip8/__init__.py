from pathlib import Path

_BASE_DIR = Path(__file__).parent
_ROM_F =  _BASE_DIR/"ROM.hex"


class _INSTRUC(type):
    hexCode = 0x0000
    def __repr__(self):
        return self.hexCode
    def __str__(self):
        return str(self.hexCode)
    def __int__(self):
        return self.hexCode

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
    _SP = _BinVal()
    _ST = _ByteList(l=16,b=2)
    
    class Instrucs():
        ID = {
            0x0:Instrucs.MNG,
            0x1:Instrucs.JP,
            0x2:Instrucs.CALL,
            0x3:Instrucs.SE,
            0x4:Instrucs.SNE,
            0x5:Instrucs.SE,
            0x6:Instrucs.LD,
            0x7:Instrucs.ADD,
            0x8:Instrucs.ARLG,
            0x9:Instrucs.SNEV,
            0xA:Instrucs.LD,
            "1nnn":Instrucs.JP
        }
        class NOP():
            def __call__(self):
                pass
        class CLS(metaclass=_INSTRUC):
            def __call__(self):
                pass
        class RET(metaclass=_INSTRUC):
            def __call__(self):
                pass
    
    def __init__(self, dumpFile):
        #Load ROM
        self.op = []
        self._ROM_DATA = getBytes(_ROM_F)
        self._DMP_F = dumpFile
        for x in range(len(self._ROM_DATA)):
            self._Memory[x] = self._ROM_DATA[x]

    def Cycle(self):
        self.op = int(f"{self._Memory[self._PC.VALUE]:02X}{self._Memory[self._PC.VALUE+1]:02X}",16)
        self._PC.VALUE +=2
        
        

    def DumpRam(self):
        open(self._DMP_F,"w").close
        with open(self._DMP_F, "wb") as File:
            for x in range(len(self._Memory)):
                File.write(self._Memory[x].to_bytes(1,"big"))
        File.close()