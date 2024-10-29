def getMaxMan(length):
    m = 0
    for i in range(1, length+1):
        m += (i // 2) * 4
    return m * length

if __name__ == '__main__':

    running = True
    while running:
        inp = input("Enter length: ")
        if inp == "quit":
            running = False
        inp = int(inp)
        if type(inp) is int:
            maxMan = getMaxMan(length=inp)
            print(maxMan)
