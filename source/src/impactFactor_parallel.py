import sys,random
sys.path.append("../lib/")

from tweepy import api, error
from tweepy.cache import FileCache,DBFileCache,DBCache
from tweepy.api import API
import tweepy
from tweepy.models import *
import Queue, threading
from db import DBSingleton


class EvalThread(threading.Thread):
    
    def __init__(self, queue):
	self.queue = queue
	threading.Thread.__init__(self)
    
    def run(self):
	while True:
    	    user = self.queue.get()
    	    evaluate_user(user)
            self.queue.task_done()
    

def evaluate_user(u):
	global results,twitterApi
	try:
	    tweets = twitterApi.user_timeline(user_id=u.id, count=100, include_rts=1)
	    retweets = len([i for i in tweets if  hasattr(i, "retweeted_status")])
	    
	    friends = twitterApi.friends_ids(user_id=u.id)
	    friends_ids = friends[0]
	    
	    followers = twitterApi.followers_ids(user_id=u.id)
	    followers_ids = followers[0]
	    
	    impact = len([i for i in followers_ids if i in friends_ids])/(len(followers_ids)+0.0000)
	    
	    results.append(Result(u.screen_name, retweets/100.00, impact))
	except Exception,e:
	    import sys,traceback
	    print "ERRRRRRRRRRRRRRRRRR: ",
	    traceback.print_exc(sys.stdout)
	#pass
    

class Result:
    def __init__(self,username, retweets, fi):
	self.username = username
	self.retweets = retweets
	self.followImpact = fi
    def __str__(self):
	return self.username+" "+str(self.retweets)+ " " + str(self.followImpact)

    def __cmp__(self, other):
	if float(self.retweets*self.followImpact) > float(other.retweets*other.followImpact):
	    return 1
	if float(self.retweets*self.followImpact) < float(other.retweets*other.followImpact):
	    return -1
	if float(self.retweets+self.followImpact) > float(other.retweets+other.followImpact):
	    return 1
	if float(self.retweets+self.followImpact) < float(other.retweets+other.followImpact):
	    return -1
	return 0


if __name__ == "__main__":

    #Initialize 
    auth = tweepy.OAuthHandler("xg2hLKvf1nxw1TUALvx5xA", "MkX0lDUik0mJuc6nxserddbQDWd7ZTErQN6Tf0OhOM")
    auth.set_access_token("174566652-MOGbxytlmUHIN5tEMgl5rgqWdWaIQXYZ6XPyYKl1", "yem38OfoUbsoPZvOVr3k0n3X7JSUDYD8oxAKXvrJw6k")
    twitterApi = API(auth_handler=auth,
                    host='api.twitter.com', search_host='search.twitter.com',
                    cache=DBFileCache(DBCache(timeout=-1, conn=DBSingleton.getInstance()), FileCache("cache", timeout=-1), timeout = -1), secure=False, api_root='/1', search_root='',
                    retry_count=0, retry_delay=0, retry_errors=None,
                    parser=None)
    
    #main
    #try:
    users = twitterApi.search_users(q=sys.argv[1], per_page=200)
    results = []
    queue = Queue.Queue()
    for i in range(20):
	t = EvalThread(queue)
	t.setDaemon(True)
        t.start()
    
    for u in users:
	queue.put(u)
    queue.join()
    
    results.sort()
    results.reverse()
    for i in results:
	print i
