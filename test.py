class CS:
    class C1:
        pass
    class C2:
        pass
    class C3:
        pass
l={
    0x01:CS.C1,
    0x10:CS.C2,
    0x20:CS.C3
}

c = l[0x10]()
print(c)