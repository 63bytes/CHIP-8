fail = 0
suc = 0

for x in range(255):
    for y in range(255):
        if (x|y)==(x+y):
            suc += 1
        else:
            fail+=1

print(fail)
print(suc)