import sys,random,math,time
import hashlib
import os
sys.path.append("../lib/")
from db import DBSingleton

def getFileName(k):
    md5 = hashlib.md5()
    md5.update(k)
    return md5.hexdigest()


limit = 1000
offset = int(sys.argv[1])

cur = DBSingleton.getInstance().cursor()

while 1:
    cur.execute("select k from data limit %s offset %s", (limit, offset))
    print offset
    row = cur.fetchone()
    while row:
        fileName = getFileName(row[0]) 
        path = os.path.join("~/cache/", fileName)
        if fileName and os.path.exists(path):
            os.remove(path)
            os.remove(path+".lock")
            print "REMOVED ",path
        row = cur.fetchone()
    offset += limit
