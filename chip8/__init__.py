class BYTE:
    def __init__(self, v=0, b=8):
        self.LOST_PRECISION = False
        self._Limit = (2**b)-1
        self._Bits = b
        self._Value = v
    def Binary(self):
        return f"{self._Value:0{self._Bits}b}"
    def __int__(self):
        return self._Value
    def __str__(self):
        return str(self._Value)
    def __format__(self,f):
        return f"{self._Value:{f}}"
    def __index__(self):
        return self.__int__()
    def _run_lmb(self, other, l):
        if isinstance(other, _Byte):
            other = other._Value
        elif not isinstance(other, int):
            raise NotImplemented
        return l(self._Value, other)
    def _run_lmb_arith(self, other, l):
        v = self._run_lmb(other,l)
        cv = v&self._Limit
        b = _Byte(cv, self._Bits)
        if v!=cv:
            b.LOST_PRECISION=True
        return b
    #Arithmatic
    def __add__(self, other):
        return self._run_lmb_arith(other, lambda a,b:a+b)
    def __sub__(self, other):
        return self._run_lmb_arith(other, lambda a,b:a-b)
    def __iadd__(self, other):
        return self.__add__(other)
    def __isub__(self, other):
        return self.__sub__(other)
    #Bitwise
    def __or__(self, other):
        return self._run_lmb_arith(other, lambda a,b:a|b)
    def __and__(self, other):
        return  self._run_lmb_arith(other, lambda a,b:a&b)
    def __xor__(self, other):
        return self._run_lmb_arith(other, lambda a,b:a^b)
    def __invert__(self):
        self._Value = ~self._Value
    def __lshift__(self, other):
        return self._run_lmb_arith(other, lambda a,b:a<<b)
    def __rshift__(self, other):
        return self._run_lmb_arith(other, lambda a,b:a>>b)
    #Comparison
    def __eq__(self, other):
        return self._run_lmb(other, lambda a,b:a==b)
    def __ne__(self, other):
        return self._run_lmb(other, lambda a,b:a!=b)
    #Value
    def __setitem__(self,index,val):
        if index==0:
            self._Value = int(val)&self._Limit

class BYTE_ARRAY:
    def __init__(self,v=0,b=8,l=16):
        self._List = [BYTE(v,b) for _ in range(l)]
    def __setitem__(self,i,v):
        self._List[i][0] = v
    def __getitem__(self,i):
        return self._List[i]
    def __len__(self):
        return len(self._List)
    
MEMORY_SIZE = 0xfff
KEYMAP = {}

class Emulator:
    ram_ = BYTE_ARRAY(l=MEMORY_SIZE)
    v_registers_ = BYTE_ARRAY()
    i_register_ = BYTE(b=16)
    ST = BYTE()
    DT = BYTE()

    def INS_0nnn(self):
        pass
    def INS_00E0(self):
        pass

    def __init__(self):
        pass
