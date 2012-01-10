import sys,random,time,os
import traceback
sys.path.append("../lib/")
from tweeapi.utils import EvalUser
from tweeapi import APISingleton
from tweepy.models import handle_exception


def handle_func(func, **args):
    if str(args["user_id"])+"\n" in open("not_auths").readlines():
        return [],(0,0)
    while 1:
        try:
            ret = func(**args)
            return ret
        except Exception,e:
            time.sleep(5)
            print args
            print "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE: ",e,sys.argv, args["user_id"]
            if str(e).find("Not au") != -1 or str(e).find("requires authentication") != -1:
                open("not_auths", "a").write(str(args["user_id"])+"\n")
                return [],(0,0)
            if str(e).find("No such file or ") != -1:
                l = str(e).split()
                file = l[-1].replace("'", "").replace(".lock", "")
                print file
                os.remove(file)
            raise e

if __name__ == "__main__":
    while 1:
        try:
            twitterApi = APISingleton.getInstance() 
            i = random.randint(1, 1000000000)
            u = handle_func(twitterApi.get_user, user_id=i)
            EvalUser.load(u)
            for fId in twitterApi.friends_ids(user_id=i)[0]:
                EvalUser.loadFromDB(fId)
        except Exception, e:
            print e
