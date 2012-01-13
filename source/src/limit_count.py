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
	    twitterApi = APISingleton.getInstance()
	    ret = twitterApi.rate_limit_status()
	    print ret
	    sys.exit(0)
	except Exception,e:
	    print e
	    pass