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
        self._VALUE = _CorrectBytes(v, self.Bits)
    def Set(self, v=0):
        self._VALUE = _CorrectBytes(v, self.Bits)
    def Get(self):
        return self._VALUE
    def __repr__(self):
        return self._VALUE
    def __str__(self):
        return str(self._VALUE)
    def __int__(self):
        return self._VALUE

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
    _PC = _BinVal()
    _SP = _BinVal()
    _ST = _ByteList(l=16,b=2)
    
    class Instrucs():
        class NOP(metaclass=_INSTRUC):
            hexCode=0x0000
            def __call__(self):
                pass
        class CLS(metaclass=_INSTRUC):
            hexCode=0x00E0
            def __call__(self):
                pass
        class RET(metaclass=_INSTRUC):
            hexCode=0x00EE
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
        self.op[1] = self._Memory[self._PC]
        self._PC+=1
        self.op[2] = self._Memory[self._PC]
        self._PC+=1

    def DumpRam(self):
        open(self._DMP_F,"w").close
        with open(self._DMP_F, "wb") as File:
            for x in range(len(self._Memory)):
                File.write(self._Memory[x].to_bytes(1,"big"))
        File.close()