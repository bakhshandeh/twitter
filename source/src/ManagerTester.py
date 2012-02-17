import sys
from db import DBSingleton
import psycopg2, psycopg2.extras
sys.path.append("../lib/")

from tweeapi import APISingleton, manager

if __name__ == "__main__":

    twitterApi = APISingleton.getInstance()

    users = [twitterApi.get_user(sys.argv[1])]
    db = DBSingleton.getInstance()
    cur = DBSingleton.getInstance().cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("select * from site_users where oauth_uid=%s", (sys.argv[2], ))
    row = cur.fetchone()
    
    manager.followUsers(row, users)