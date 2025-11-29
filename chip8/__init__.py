from pathlib import Path
import logging
import pygame
import math
from random import randint
import keyboard
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

def _RndByte():
    return randint(0,255)

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

class Display:
    def __init__(self, w=64, h=32, hc=(255,255,255), lc=(0,0,0), ps=10):
        self.WIDTH = w
        self.HEIGHT = h
        self.PIXEL_SIZE = ps
        self.HC = hc
        self.LC = lc
        self.Data = [[0 for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]
        self.screen = pygame.display.set_mode((self.WIDTH*self.PIXEL_SIZE, self.HEIGHT*self.PIXEL_SIZE))
        pygame.display.set_caption("Display")
    def Update(self):
        pygame.event.get()
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                if self.Data[x][y]==1:
                    color = self.HC
                else:
                    color = self.LC
                pygame.draw.rect(
                    self.screen,
                    color,
                    (x * self.PIXEL_SIZE, y * self.PIXEL_SIZE, self.PIXEL_SIZE, self.PIXEL_SIZE)
                )
        pygame.display.flip()
    def writeBytes(self, b, x,y):
        bs = f"{(b&0xff):08b}"
        for i in range(len(bs)):
            self.Data[(x+i)][y] = int(bs[i])

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
        0x2A:[0x2A,"SHL",2],
        0x30:[0x30,"LDI",3],
        0x31:[0x31,"ADDI",2],
        0x32:[0x32,"STV",2],
        0x33:[0x33,"LDV",2],
        0x40:[0x40,"RND",3],
        0x50:[0x50,"LDDT",2],
        0x51:[0x51,"STDT",2],
        0x52:[0x52,"STST",2],
        0x60:[0x60,"SKPK",2],
        0x61:[0x61,"SKPNK",2],
        0x62:[0x62,"LDK",2],
        0x70:[0x70,"LDF",2],
        0x71:[0x71,"BCD",2],
        0x72:[0x72,"CLR",1],
        0x73:[0x73,"DRW",3]
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
    _STACK = _StackTrace()
    _DT = _Byte()
    _ST = _Byte()
    _SKP = False
    stop = False

    DISPLAY_MEM = 0x50
    DISPLAY_BYTES = (32*62)/8
    SPRITE_START = 0x0
    SPRITE_SIZE = 0x5
    KEYS = {
        "0":0x0,
        "1":0x1,
        "2":0x2,
        "3":0x3,
        "4":0x4,
        "5":0x5,
        "6":0x6,
        "7":0x7,
        "8":0x8,
        "9":0x9,
        "a":0xA,
        "A":0xA,
        "b":0xB,
        "B":0xB,
        "c":0xC,
        "C":0xC,
        "d":0xD,
        "D":0xD,
        "e":0xE,
        "E":0xE,
        "f":0xF,
        "F":0xF
        }

    def getKeyCode(self,k):
        return self.KEYS[k]
    def GetMemBytes(self,b=1, i=True):
        d = ""
        for x in range(b):
            d = f"{d}{(self._Memory[self._PC+x]):02X}"
            output(action="READ", d={"ad":self._PC+x,"val":self._Memory[self._PC+x]})
            logging.info(f"[READ] 0x{(self._PC+x):02X} - 0x{(self._Memory[self._PC+x]):02X}")
        if b>1:
            logging.info(f"[READ] (FULL) - 0x{d}")
        if i:
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
        self._STACK.add(self._PC)
        self._PC[0] = ad
    def RET(self):
        self._PC[0] = self._STACK[0]
        logging.info(f"[EXECUTE] RET - PC set to 0x{self._STACK[0]:02X}")
        self._STACK.removeFirst()
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
        logging.info(f"[EXECUTE] SNE - V{vx}=={vy} - {self._Reg[vx]==vy}")
        if vx==vy:
            self._SKP = True
            logging.info("[EXECUTE] VSE - Skip flag set")
    def VSNE(self):
        vxn = self.GetMemBytes()
        vyn = self.GetMemBytes()
        vx = self._Reg(vxn)
        vy = self._Reg(vyn)
        logging.info(f"[EXECUTE] SNE - V{vx}!={vy} - {self._Reg[vx]!=vy}")
        if vx!=vy:
            self._SKP = True
            logging.info("[EXECUTE] VSE - Skip flag set")
    def JMPV(self):
        vxn = self.GetMemBytes()
        vx = self._Reg[vxn]
        n = self.GetMemBytes(b=2)
        self._PC[0] = n+vx
        logging.info(f"[EXECUTE] JMPV - PC set to {n+vx}. {vx} + {n} (V{vxn} + nnn)")
    def LDVB(self):
        x = self.GetMemBytes()
        kk = self.GetMemBytes()
        logging.info(f"[EXECUTE] LDVB - Set V{x:02X} to 0x{kk:02X}")
        self._Reg[x] = kk
    def ADDB(self):
        x = self.GetMemBytes()
        kk = self.GetMemBytes()
        self._Reg[x] += kk
        logging.info(f"[EXECUTE] ADDB - V{x} = V{x} + 0x{kk:02X} = {self._Reg[x]}")
    def LDVV(self):
        h = hexSpilt(self.GetMemBytes())
        logging.info(f"[EXECUTE] LDVV - V{h[0]} = V{h[1]}")
        self._Reg[h[0]] = self._Reg[h[1]]
    def OR(self):
        v = f"{self.GetMemBytes():02X}"
        vx = self._Reg[int(v[0],16)]
        vy = self._Reg[int(v[1],16)]
        vx[0] = vx|vy
        logging.info(f"[EXECUTE] OR - {vx} = V{v[0]} OR V{v[1]}")
    def AND(self):
        v = f"{self.GetMemBytes():02X}"
        vx = self._Reg[int(v[0],16)]
        vy = self._Reg[int(v[1],16)]
        vx[0] = vx & vy
        logging.info(f"[EXECUTE] AND - {vx} = V{v[0]:02X} AND V{v[1]:02X}")
    def XOR(self):
        v = f"{self.GetMemBytes():02X}"
        vx = self._Reg[int(v[0],16)]
        vy = self._Reg[int(v[1],16)]
        vx[0] = vx ^ vy
        logging.info(f"[EXECUTE] XOR - {vx} = V{v[0]:02X} XOR V{v[1]:02X}")
    def ADDV(self):
        v = f"{self.GetMemBytes():02X}"
        vx = self._Reg[int(v[0],16)]
        vy = self._Reg[int(v[1],16)]
        vx[0] = vx + vy
        if vx[0].LOST_PRECISION:
            self._Reg[0xf] = 1
        else:
            self._Reg[0xf] = 0
        logging.info(f"[EXECUTE] ADDV - {vx} = V{v[0]:02X} + V{v[1]:02X}")
    def SUB(self):
        v = f"{self.GetMemBytes():02X}"
        vx = self._Reg[int(v[0],16)]
        vy = self._Reg[int(v[1],16)]
        vx[0] = vx - vy
        if vx.LOST_PRECISION:
            self._Reg[0xf] = 1
        else:
            self._Reg[0xf] = 0
            logging.warning(f"[EXECUTE] SUB - Borrowed. Vf set to 0")
        logging.info(f"[EXECUTE] SUB - {vx} = V{v[0]:02X} - V{v[1]:02X}")
    def SHR(self):
        v = f"{self.GetMemBytes():02X}"
        vx = self._Reg[int(v[0],16)]
        vy = self._Reg[int(v[1],16)]
        vx[0] = vx + vy
        if not vx.LOST_PRECISION:
            self._Reg[0xf] = 1
        else:
            self._Reg[0xf] = 0
            logging.warning(f"[EXECUTE] SUB - Borrowed. Vf set to 0")
        logging.info(f"[EXECUTE] SUB - {vx} = V{v[0]:02X} - V{v[1]:02X}")
    def SUBN(self):
        v = f"{self.GetMemBytes():02X}"
        vx = self._Reg[int(v[0],16)]
        vy = self._Reg[int(v[1],16)]
        vx[0] = vy - vx
        if vx.LOST_PRECISION:
            self._Reg[0xf] = 1
        else:
            self._Reg[0xf] = 0
            logging.warning(f"[EXECUTE] SUB - Borrowed. Vf set to 0")
        logging.info(f"[EXECUTE] SUB - {vx} = V{v[1]:02X} - V{v[0]:02X}")
    def SHL(self):
        v = f"{self.GetMemBytes():02X}"
        vx = self._Reg[int(v[0],16)]
        vy = self._Reg[int(v[1],16)]
        vx[0] = vx + vy
        if not vx.LOST_PRECISION:
            self._Reg[0xf] = 1
        else:
            self._Reg[0xf] = 0
            logging.warning(f"[EXECUTE] SUB - Borrowed. Vf set to 0")
        logging.info(f"[EXECUTE] SUB - {vx} = V{v[0]:02X} - V{v[1]:02X}")
    def LDI(self):
        n = self.GetMemBytes(2)
        self._Reg_I[0] = n
        logging.info("[EXECUTE] LDI - I set")
    def ADDI(self):
        vxn = self.GetMemBytes()
        vx = self._Reg[vxn]
        self._Reg_I += vx
        logging.info(f"[EXECUTE] ADDI - I += V{vxn}(0x{vx:02X})")
    def STV(self):
        vxn = self.GetMemBytes()
        for x in range(vxn):
            self._Memory[self._Reg_I + x] = int(self._Reg[x])
        logging.info(f"[EXECUTE] STV - Values V0-V{vxn} stored at 0x{self._Reg_I:02X}+")
    def LDV(self):
        vxn = self.GetMemBytes()
        for x in range(vxn+1):
            self._Reg[x] = self._Memory[self._Reg_I + x]
        logging.info(f"[EXECUTE] STV - Values V0-V{vxn} loaded from 0x{self._Reg_I:02X}+")
    def RND(self):
        vxn = self.GetMemBytes()
        vx = self._Reg[vxn]
        kk = self.GetMemBytes()
        r = _RndByte()
        logging.info(f"[EXECUTE] RND - V{vxn} = {r&kk}({r}&{kk})")
        vx[0] = r&kk
    def LDDT(self):
        vx = self._Reg[self.GetMemBytes()]
        vx[0] = self._DT
        logging.info("[EXECUTE] LDDT - Vx set to {self._DT}")
    def STDT(self):
        vx = self._Reg[self.GetMemBytes()]
        self._DT[0] = int(vx)
        logging.info("[EXECUTE] STDT - DT set to 0x{vx:02X}")
    def STST(self):
        vx = self._Reg[self.GetMemBytes()]
        self._ST[0] = int(vx)
        logging.info("[EXECUTE] STDT - ST set to 0x{vx:02X}")
    def SKPK(self):
        vx = self._Reg[self.GetMemBytes()]
        if keyboard.is_pressed(f"vx:01X"):
            self._SKP = True
    def SKPNK(self):
        vx = self._Reg[self.GetMemBytes()]
        if not keyboard.is_pressed(f"vx:01X"):
            self._SKP = True
    def LDK(self):
        vx = self._Reg[self.GetMemBytes()]
        vx[0] = self.KEYS(keyboard.read_key())
    def LDF(self):
        print("LDF")
        vx = self.GetMemBytes()
        self._Reg_I[0] = (vx*self.SPRITE_SIZE)+self.SPRITE_START
    def CLR(self):
        for x in self.DISPLAY_BYTES:
            self._Memory[self.DISPLAY_MEM+x] = 0x0
    def DRW(self):
        print("DRW")
        vx = self.GetMemBytes()
        vy = self.GetMemBytes()
        n = self.GetMemBytes()
        for x in range(int(n)):
            self.Display.writeBytes(self._Memory[self._Reg_I+x],int(vx),int(vy)+x)

    def __init__(self, dumpFile, programFile):
        #Load ROM
        self.Instrucs = {
            0xffff:{
                #
            }
        }
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
            0x2A:self.SHL,
            0x30:self.LDI,
            0x31:self.ADDI,
            0x32:self.STV,
            0x33:self.LDV,
            0x40:self.RND,
            0x50:self.LDDT,
            0x51:self.STDT,
            0x52:self.STST,
            0x60:self.SKPK,
            0x61:self.SKPNK,
            0x62:self.LDK,
            0x70:self.LDF,
            #0x71:self.BCD,
            0x72:self.CLR,
            0x73:self.DRW
        }
        self._PROGRAM_DATA = getBytes(programFile)
        for x in range(len(self._PROGRAM_DATA)):
            self._Memory[x] = self._PROGRAM_DATA[x]
        self._ROM_DATA = getBytes(_ROM_F)
        self._DMP_F = dumpFile
        for x in range(len(self._ROM_DATA)):
            self._Memory[x] = self._ROM_DATA[x]
        self._Memory[0xfff] = 0x01
        self.Display = Display()
        self.Cycles = 0
        
    def Cycle(self):
        self.op = self.GetMemBytes(i=False)
        if self._SKP:
            output(action="DECODE",d={"val":self.op,"ins":"SKIP"})
            self._PC += OpCodes[self.op][2]
            self._SKP = False
            return
        else:
            self._PC +=  1
        print(f"0x{self.op:02X}")
        output(action="DECODE",d={"val":self.op,"ins":OpCodes[self.op][1]})
        logging.info(f"[DECODE] 0x{self.op:02X} - {OpCodes[self.op][1]}")
        self.Instrucs[self.op]()
        data = []
       # for bn in range(int(32*64/8)):
     #       bi = self._Memory[self.DISPLAY_MEM+bn]
     #       bb = f"{bi:08b}"
      #      for i in bb:
     #           data.append(int(i))
     #   for bn in range(32*64):
     #       x = math.floor(bn/32)
     #       y = bn-(math.floor(bn/32)*32)
     #       self.Display.Data[x][y] = data[bn]
        self.Display.Update()
        self.Cycles += 1

    def DumpRam(self):
        open(self._DMP_F,"w").close
        with open(self._DMP_F, "wb") as File:
            for x in range(len(self._Memory)):
                File.write(self._Memory[x]._Value.to_bytes(1,"big"))
        File.close()