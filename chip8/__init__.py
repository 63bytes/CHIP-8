from pathlib import Path
import logging
_BASE_DIR = Path(__file__).parent
_ROM_F =  _BASE_DIR/"ROM.hex"
_LOG_F = _BASE_DIR/"log.txt"

logging.basicConfig(
    filename=_LOG_F,
    filemode="w",
    level=logging.INFO,
    format="[%(levelname)s] - %(message)s"
)

def output(action, d):
    pass

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
    
class _Byte:
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
        return self._run_lmb_arith(other, lambda a,b:a&b)
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
class _ByteList:
    def __init__(self,v=0,b=8,l=16):
        self._List = [_Byte(v,b) for _ in range(l)]
    def __setitem__(self,i,v):
        self._List[i][0] = v
    def __getitem__(self,i):
        return self._List[i]
    def __len__(self):
        return len(self._List)

class _StackTrace:
    def __init__(self):
        self._List = []
    def add(self, i):
        if len(self._List)<16:
            self._List.insert(0,int(i))
        else:
            logging.warn("[STACK] Stack trace full. New value not added")
    def __getitem__(self,i):
        return self._List[i]
    def removeFirst(self):
        self._List.remove(self._List[0])

def getBytes(f):
    l = []
    with open(f, "rb") as File:
        for x in File.read():
            l.append(x)
    return l

def hexSpilt(v):
    h = f"{v:02X}"
    return int(h[0],16), int(h[1], 16)

class _OPCODEs:
    DATA = {
        0x00:[0x00,"NOP",1],
        0x01:[0x01,"EXIT",1],
        0x10:[0x10,"JMP",3],
        0x11:[0x11,"CALL",3],
        0x12:[0x12,"RET",1],
        0x13:[0x13,"SE",3],
        0x14:[0x14,"SNE",3],
        0x15:[0x15,"VSE",2],
        0x16:[0x16,"VSNE",2],
        0x17:[0x17,"JMPV",4],
        0x20:[0x20,"LDVV",3],
        0x21:[0x21,"ADDB",3],
        0x22:[0x22,"LDVV",3],
        0x23:[0x23,"OR",2],
        0x24:[0x24,"AND",2],
        0x25:[0x25,"XOR",2],
        0x26:[0x26,"ADDV",2],
        0x27:[0x27,"SUB",2],
        0x28:[0x28,"SHR",2],
        0x29:[0x29,"SUBN",2],
        0x2A:[0x2A,"SHL",2]
    }
    def __getitem__(self,i):
        if type(i)==int:
            return self.DATA[i]
        else:
            for x in self.DATA:
                if self.DATA[x][1]==i:
                    return self.DATA[x]
OpCodes = _OPCODEs()

class CHIP_8():
    _Memory = _ByteList(l=0x1000)
    _Reg = _ByteList(l=0x10)
    _Reg_I = _Byte(b=16)
    _PC = _Byte(v=0x200, b=16)
    _ST = _StackTrace()
    _SKP = False
    stop = False

    def GetMemBytes(self,b=1, i=True):
        d = ""
        for x in range(b):
            d = f"{d}{(self._Memory[self._PC+x]):02X}"
            output(action="READ", d={"ad":self._PC+x,"val":self._Memory[self._PC+x]})
            logging.info(f"[READ] 0x{(self._PC+x):02X} - 0x{(self._Memory[self._PC+x]):02X}")
        if b>1:
            logging.info(f"[READ] (FULL) - 0x{d}")
        if i:
            print(b)
            self._PC += b
        return int(d,16)

    def NOP(self):
        logging.info("[EXECUTE] NOP - No operation")
        pass
    def EXIT(self):
        self.stop = True
        logging.critical("[EXECUTE] EXIT - Program stoped")
    def JMP(self):
        ad = self.GetMemBytes(b=2)
        self._PC[0] = ad
        logging.info(f"[EXECUTE] JMP - PC set to 0x{self._PC:02X}")
    def CALL(self):
        ad = self.GetMemBytes(b=2)
        logging.info(f"[EXECUTE] CALL - PC set to 0x{ad:0x}. 0x{self._PC:02X} pushed to stack")
        self._ST.add(self._PC)
        self._PC[0] = ad
    def RET(self):
        self._PC[0] = self._ST[0]
        logging.info(f"[EXECUTE] RET - PC set to 0x{self._ST[0]:02X}")
        self._ST.removeFirst()
    def SE(self):
        vx = self.GetMemBytes()
        kk = self.GetMemBytes()
        logging.info(f"[EXECUTE] SE - V{vx}=={kk} - {self._Reg[vx]==kk}")
        if self._Reg[vx]==kk:
            self._SKP = True
            logging.info("[EXECUTE] SE - Skip flag set")
    def SNE(self):
        vx = self.GetMemBytes()
        kk = self.GetMemBytes()
        logging.info(f"[EXECUTE] SNE - V{vx}!={kk} - {self._Reg[vx]!=kk}")
        if self._Reg[vx]!=kk:
            self._SKP = True
            logging.info("[EXECUTE] SNE - Skip flag set")
    def VSE(self):
        vxn = self.GetMemBytes()
        vyn = self.GetMemBytes()
        vx = self._Reg(vxn)
        vy = self._Reg(vyn)
        logging.info(f"[EXECUTE] SNE - V{vx}!={kk} - {self._Reg[vx]!=kk}")
        if vx==vy:
            self._SKP = True
            logging.info("[EXECUTE] VSE - Skip flag set")
    def VSNE(self):
        vx = self._Reg[self.GetMemBytes()]
        vy = self._Reg[self.GetMemBytes()]
        if vx!=vy:
            self._SKP = True
    def JMPV(self):
        vx = self._Reg[self.GetMemBytes()]
        n = self.GetMemBytes(b=2)
        self._PC[0] = n+vx
    def LDVB(self):
        x = self.GetMemBytes()
        kk = self.GetMemBytes()
        logging.info(f"[EXECUTE] LDVB - Set V{x:02X} to 0x{kk:02X}")
        self._Reg[x] = kk
    def ADDB(self):
        x = self.GetMemBytes()
        kk = self.GetMemBytes()
        self._Reg[x] += kk
    def LDVV(self):
        h = hexSpilt(self.GetMemBytes())
        self._Reg[h[0]] == self._Reg[h[1]]
    def OR(self):
        v = f"{self.GetMemBytes():02X}"
        vx = self._Reg[int(v[0],16)]
        vy = self._Reg[int(v[1],16)]
        vx[0] = vx|vy
    def AND(self):
        pass
    def XOR(self):
        pass
    def ADDV(self):
        pass
    def SUB(self):
        pass
    def SHR(self):
        pass
    def SUBN(self):
        pass
    def SHL(self):
        pass
    def __init__(self, dumpFile, programFile):
        #Load ROM
        self.Instrucs = {
            0x00:self.NOP,
            0x01:self.EXIT,
            0x10:self.JMP,
            0x11:self.CALL,
            0x12:self.RET,
            0x13:self.SE,
            0x14:self.SNE,
            0x15:self.VSE,
            0x16:self.VSNE,
            0x17:self.JMPV,
            0x20:self.LDVB,
            0x21:self.ADDB,
            0x22:self.LDVV,
            0x23:self.OR,
            0x24:self.AND,
            0x25:self.XOR,
            0x26:self.ADDV,
            0x27:self.SUB,
            0x28:self.SHR,
            0x29:self.SUBN,
            0x2A:self.SHL
        }
        self._PROGRAM_DATA = getBytes(programFile)
        for x in range(len(self._PROGRAM_DATA)):
            self._Memory[x] = self._PROGRAM_DATA[x]
        self._ROM_DATA = getBytes(_ROM_F)
        self._DMP_F = dumpFile
        for x in range(len(self._ROM_DATA)):
            self._Memory[x] = self._ROM_DATA[x]
        self._Memory[0xfff] = 0x01
        
    def Cycle(self):
        self.op = self.GetMemBytes(i=False)
        if self._SKP:
            output(action="DECODE",d={"val":self.op,"ins":"SKIP"})
            self._PC += OpCodes[self.op][2]
            self._SKP = False
            return
        else:
            self._PC +=  1

        output(action="DECODE",d={"val":self.op,"ins":OpCodes[self.op][1]})
        logging.info(f"[DECODE] 0x{self.op:02X} - {OpCodes[self.op][1]}")
        self.Instrucs[self.op]()

    def DumpRam(self):
        open(self._DMP_F,"w").close
        with open(self._DMP_F, "wb") as File:
            for x in range(len(self._Memory)):
                File.write(self._Memory[x]._Value.to_bytes(1,"big"))
        File.close()