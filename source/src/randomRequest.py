import sys,random,math,time
sys.path.append("../lib/")

from tweepy import api, error
from tweepy.cache import FileCache,DBCache, DBFileCache
from tweepy.api import API
import tweepy
from tweepy.models import *

def handle_func(func, **args):
    if str(args["user_id"])+"\n" in open("not_auths").readlines():
	return [],(0,0)
    while 1:
	try:
	    ret = func(**args)
	    return ret
	except Exception,e:
	    handle_exception(e)
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
            auth = tweepy.OAuthHandler("xg2hLKvf1nxw1TUALvx5xA", "MkX0lDUik0mJuc6nxserddbQDWd7ZTErQN6Tf0OhOM")
            auth.set_access_token("174566652-MOGbxytlmUHIN5tEMgl5rgqWdWaIQXYZ6XPyYKl1", "yem38OfoUbsoPZvOVr3k0n3X7JSUDYD8oxAKXvrJw6k")

            twitterApi = API(auth_handler=auth,
                    host='api.twitter.com', search_host='search.twitter.com',
                     cache=DBFileCache(DBCache(timeout=-1), FileCache("cache", timeout=-1), timeout = -1), secure=False, api_root='/1', search_root='',
                    retry_count=0, retry_delay=0, retry_errors=None,
                    parser=None)
            i = random.randint(1, 1000000000)
    	    u = handle_func(twitterApi.get_user, user_id=i)
    	    tweets = u.timeline(count=100, include_rts=1)
    	    friends = twitterApi.friends_ids(user_id=u.id)
    	    followers = twitterApi.followers_ids(user_id=u.id)
    	except Exception, e:
    	    print e