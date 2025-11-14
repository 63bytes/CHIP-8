
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
    if _CheckBits(v,b*2):
        return v
    else:
        return 0x00

class _BinVal():
    def __init__(self,v=0, b=1):
        self.Bytes = b
        self._VALUE = _CorrectBytes(v, self.Bytes)
    def Set(self, v=0):
        self._VALUE = _CorrectBytes(v, self.Bytes)
    def __repr__(self):
        return self._VALUE
    def __str__(self):
        return str(self._VALUE)
    def __int__(self):
        return self._VALUE

class _ByteList():#Handle setting of _BinValues
    def __init__(self, l=8, b=1):
        self.LIST = [_BinVal(b=b)]*l
    def __getitem__(self, i):
        return self.LIST[i]
    def __setitem__(self, i, v):
        self.LIST[i].Set(v)
    

class CHIP_8():
    _Memory = _ByteList(l=0x1000)
    _Reg = _ByteList(l=0x10)
    _Reg_I = _ByteList(l=1,b=2)
    _PC = _BinVal(b=2)
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

