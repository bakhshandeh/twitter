from tweeapi import APISingleton
from db import DBSingleton
import psycopg2.extras

def followUsers(userInfo,  users):
    api = APISingleton.getInstanceForUser(userInfo)
    
    cur = DBSingleton.getInstance().cursor()
    cur.execute("select nextval('tracking_seq')")
    id = cur.fetchone()[0]
    
    userId = userInfo["oauth_uid"];
    cur.execute("""insert into tracking(tracking_id,tracking_user_id,tracking_date, tracking_count)
                values(%s,%s,now(), %s) """, (id, userId, len(users)))
    for user in users:
        api.create_friendship(user_id=user.id)
        cur.execute("""insert into tracking_users(tracking_id, current_id, user_id, user_screen_name)
                    values(%s,%s,%s,%s)""", (id, userId, user.id, user.screen_name))
    cur.commit()
        
    