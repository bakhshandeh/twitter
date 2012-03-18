import sys
import traceback
sys.path.append("../lib/")
from tweeapi.IR import getTFIDFArray
from db import DBSingleton
import psycopg2.extras

import simplejson

from tweeapi import APISingleton
from tweeapi.utils import EvalUser

if __name__ == "__main__":

    twitterApi = APISingleton.getInstance()

    tweets = twitterApi.search(q=sys.argv[1].lower(), rpp=100, page=1, force=True)
    tweets = [t.text for t in tweets]
    tfidfArray = getTFIDFArray(tweets)
    
    db = DBSingleton.getInstance()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select * from users where  retweet_factor > 0.2 and impact_factor > 0.2 limit 5000;")
    
    results = []
    for row in cur:
        try:
            eUser = EvalUser.loadFromDBRow(row)
            if eUser.getSim(tfidfArray) > 0:
                results.append(eUser)
        except Exception,e:
            traceback.print_exc(sys.stdout)
            pass
    
    results.sort()
    results.reverse()
    
    jsonDic = []
    for user in results[:40]:
        jsonDic.append(user.getData())
    print simplejson.dumps(jsonDic)
