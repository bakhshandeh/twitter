import sys,random,math,time
sys.path.append("../lib/")

from tweepy import api, error
from tweepy.cache import FileCache,DBCache, DBFileCache
from tweepy.api import API
import tweepy
from tweepy.models import *
from tweeapi import APISingleton

if __name__ == "__main__":
    while 1:
        try:
	    auth = tweepy.OAuthHandler("xg2hLKvf1nxw1TUALvx5xA", "MkX0lDUik0mJuc6nxserddbQDWd7ZTErQN6Tf0OhOM")
            auth.set_access_token("174566652-MOGbxytlmUHIN5tEMgl5rgqWdWaIQXYZ6XPyYKl1", "yem38OfoUbsoPZvOVr3k0n3X7JSUDYD8oxAKXvrJw6k")
            twitterApi = API(auth_handler=auth,
                    host='api.twitter.com', search_host='search.twitter.com',
                     cache=FileCache("cache", timeout = -1), secure=False, api_root='/1', search_root='',
                    retry_count=0, retry_delay=0, retry_errors=None,
                    parser=None)
	    
	    ret = twitterApi.rate_limit_status()
	    print ret
	    sys.exit(0)
	except Exception,e:
	    print e
	    pass