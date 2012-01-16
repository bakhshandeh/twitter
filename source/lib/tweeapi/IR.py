import re,math

all_idfs = None
stopwords = []

def getIDF(word):
    global all_idfs
    fileName = "enidf.txt"
    if not all_idfs:
        all_idfs = {}
        f = open(fileName, 'r')
        for line in f.readlines():
            list = line.split()
            all_idfs[list[0].lower()] = float(list[1])
    word = word.lower()
    if all_idfs.has_key(word):
        return all_idfs[word]
    return 0

def getTFIDFArray(lines):
    global stopwords
    if not stopwords:
        stopwords = []
        ll = open("english.stop").readlines()
        for l in ll:
            stopwords.append(l.strip())
    n = 110151172.000
    tfs = {}
    dels = "#,\"\'.?!;:|0123456789@()-"
    for line in lines:
        l = line.lower().strip()
        l = re.sub("http://\S*\s", "", l)
        l = re.sub("http://\S$", "", l)
        for d in dels:
            l = l.replace(d," ")
            list = l.strip().split()
            for w in list:
                if tfs.has_key(w): 
                    tfs[w]+=1
                else: 
                    tfs[w]=1
    for i in tfs.keys():
        idf = getIDF(i)
        if i not in stopwords and idf:
            tfs[i] = tfs[i]*math.log(n/(idf+1.000), 2)
        else: tfs.pop(i)
    return tfs

def getSim(tfidf1, tfidf2):
    p1 = p2 = p12 = 0
    for w in tfidf1.keys():
        p1 += tfidf1[w]**2
    if w in tfidf2.keys():
        p12 += tfidf1[w]*tfidf2[w]
    for w in tfidf2.keys():
        p2 += tfidf2[w]**2
    if not p1 or not p2:
        return 0
    return p12/(math.sqrt(p1)*math.sqrt(p2))
