import sys
import traceback
sys.path.append("../lib/")
from tweeapi.utils import EvalUser
from db import DBSingleton
import psycopg2.extras
from tweeapi import APISingleton,manager
import random

def getUsersToFollow(keyword, count=10, currentFriends=[]):
    twitterApi = APISingleton.getInstance()

    users = twitterApi.search_users(q=keyword, per_page=random.randint(20, 200), page=random.randint(1,10))
    results = []
    goodResults = []
    for u in users:
        try:
            eUser = EvalUser.load(u)
            results.append(eUser)
            results += eUser.BFS(100, random_walk=True)
            goodResults = [u.getUserObj() for u in results if u.getImpactFactor()*u.getRetweetFactor() > 0.05 and u.getUserObj().id not in currentFriends]
            print "Keyword=",keyword, "GoodResults#=",len(goodResults)
            if len(goodResults) > count:
                return goodResults
        except Exception:
            traceback.print_exc(sys.stdout)
            pass
    return goodResults

if __name__ == "__main__":

    twitterApi = APISingleton.getInstance()

    db = DBSingleton.getInstance()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("select * from site_users where manage=1")
    for row in cur:
        userId = row["oauth_uid"]
        keywords = row["keywords"].split(",")
        for keyword in keywords:
            
            cur2 = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur2.execute("select user_id from tracking_users where current_id=%s", (userId, ))
            
            currentFriends = [i["user_id"] for i in cur2]
            users = getUsersToFollow(keyword.strip(), count=5, currentFriends = currentFriends)
            manager.followUsers(row, users)
