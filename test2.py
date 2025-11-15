class OpCodes:
    DATA = {
        0x00:[0x00,"NOP",1],
        0x01:[0x01,"EXIT",1]
    }
    def __getitem__(self,i):
        if type(i)==int:
            return self.DATA[i]
        else:
            for x in self.DATA:
                if self.DATA[x][1]==i:
                    return self.DATA[x]
op = OpCodes()
print(op[0x01])