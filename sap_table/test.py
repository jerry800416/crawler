import csv

# reload list
modellist = []
with open('nodata.txt','r') as f:
    for line in f.readlines():
        modellist.append(line.strip())
modellist = list(set(modellist))

with open('nodata2.txt','a') as fw:
    for i in modellist:
        fw.write(i + '\r')