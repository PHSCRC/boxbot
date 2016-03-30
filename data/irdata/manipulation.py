

def getdata(fn):
    fd = open(fn)
    lines = fd.readlines()
    fd.close()
    return list([(int(i.strip().split(",")[0]), float(i.strip().split(",")[1]))  for i in lines])

def writedata(fn, data):
    fd = open(fn,"w")
    fd.write("\n".join([",".join([str(j) for j in i]) for i in data]))
    fd.close()

FILES = list(["{}-s.csv".format(i) for i in range(1,7)]) + list(["{}-m.csv".format(i) for i in range(1,3)])


def setaverages(fn, newfn):
    data = {}
    for cm, v in getdata(fn):
        if cm in data:
            data[cm] = str((float(data[cm]) + float(v)) / 2)
        else:
            data[cm] = v
    writedata(newfn, sorted(data.items(),key=lambda x:float(x[0])))


Medium = 70, 1000
Short = 30, 50
