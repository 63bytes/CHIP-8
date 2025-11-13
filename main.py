from classes import *

class _INSTRUC(type):
    hexCode = 0x0000
    def __repr__(self):
        return self.hexCode
    def __str__(self):
        return str(self.hexCode)
    def __int__(self):
        return self.hexCode

_MEM = [0x00]*0x1000
_REG = [0x00]*0x10
_I = 0x0000

class Instrucs():
    class CLS(metaclass=_INSTRUC):
        hexCode=0x00E0
        def __call__(self):
            pass
    class RET(metaclass=_INSTRUC):
        hexCode=0x00EE
        def __call__(self):
            pass

