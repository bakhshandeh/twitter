from tweepy.cache import FileCache,DBFileCache,DBCache
from tweepy.api import API
import tweepy
from db import DBSingleton


twitter_api = None

def getInstance():
    global twitter_api
    if not twitter_api:
        auth = tweepy.OAuthHandler("xg2hLKvf1nxw1TUALvx5xA", "MkX0lDUik0mJuc6nxserddbQDWd7ZTErQN6Tf0OhOM")
        auth.set_access_token("174566652-MOGbxytlmUHIN5tEMgl5rgqWdWaIQXYZ6XPyYKl1", "yem38OfoUbsoPZvOVr3k0n3X7JSUDYD8oxAKXvrJw6k")
        twitter_api = API(auth_handler=auth,
                    host='api.twitter.com', search_host='search.twitter.com',
                    cache=DBFileCache(DBCache(timeout=-1, conn=DBSingleton.getInstance()), FileCache("cache", timeout=-1), timeout = -1), secure=False, api_root='/1', search_root='',
                    retry_count=0, retry_delay=0, retry_errors=None,
                    parser=None)
    return twitter_api