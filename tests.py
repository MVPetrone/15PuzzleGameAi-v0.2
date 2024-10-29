listt = [[[[[ ]]]]]
total = 0
def getLayerLen(listt):
    global total
    while len(listt) != 0:
        total += 1
        listt = listt[0]
    return total
print(getLayerLen(listt))