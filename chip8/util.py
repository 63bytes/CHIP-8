class Byte:
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
    def _run_lmb(self, other, l):
        if isinstance(other, Byte):
            other = other._Value
        elif not isinstance(other, int):
            raise NotImplemented
        return l(self._Value, other)
    def _run_lmb_arith(self, other, l):
        v = self._run_lmb(other,l)
        cv = v&self._Limit
        self._Value = cv
        if v!=cv:
            self.LOST_PRECISION=True
    def __add__(self, other):
        r =  self._run_lmb_arith(other, lambda a,b:a+b)
        return self
    def __sub__(self, other):
        r =  self._run_lmb_arith(other, lambda a,b:a-b)
        return self
    def __iadd__(self, other):
        return self.__add__(other)
    def __isub__(self, other):
        return self.__sub__(other)
    def __lshift__(self, other):
        r =  self._run_lmb_arith(other, lambda a,b:a<<b)
        return self
    def __rshift__(self, other):
        r =  self._run_lmb_arith(other, lambda a,b:a>>b)
        return self
    def __eq__(self, other):
        return self._run_lmb(other, lambda a,b:a==b)
    def __ne__(self, other):
        return self._run_lmb(other, lambda a,b:a!=b)

b = Byte(255)
print(b.Binary())