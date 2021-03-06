from tweepy.cache import FileCache,DBFileCache,DBCache
from tweepy.api import API
import tweepy
from db import DBSingleton


twitter_api = None

def getInstance():
    global twitter_api
    if not twitter_api:
        #auth = tweepy.OAuthHandler("xg2hLKvf1nxw1TUALvx5xA", "MkX0lDUik0mJuc6nxserddbQDWd7ZTErQN6Tf0OhOM")
        auth = tweepy.OAuthHandler("m32EakXMmUaGJW4rm8wXEQ", "TL5LSHWBNaUcW5MBG44V6piaF8JY9JPykMagtvfc")
        auth.set_access_token("538432816-JPzoNG6xFMZ97tYthCZNKb9llfpL6rGOdNqHtZmD", "DtqSXyezDgio8JNYvHFmlML22vsonOEWCCWhZv7I")
        #auth.set_access_token("174566652-MOGbxytlmUHIN5tEMgl5rgqWdWaIQXYZ6XPyYKl1", "yem38OfoUbsoPZvOVr3k0n3X7JSUDYD8oxAKXvrJw6k")
        twitter_api = API(auth_handler=auth,
                    host='api.twitter.com', search_host='search.twitter.com',
                    cache=DBFileCache(DBCache(timeout=-1, conn=DBSingleton.getInstance()), FileCache("cache", timeout=-1), timeout = -1), 
                    secure=False, api_root='/1', search_root='',
                    retry_count=0, retry_delay=0, retry_errors=None,
                    parser=None)
    return twitter_api

twitterUsersApi = {}
def getInstanceForUser(userInfo):
    global twitterUsersApi
    userId = userInfo["oauth_uid"]
    if not twitterUsersApi.has_key(userId):
        auth = tweepy.OAuthHandler("VtJIiRqZJ72wy4aXexXZvQ", "xA79MhAkTJdzy91hnULwfKeF54CfghZCkNWwxKdhrMc")
        auth.set_access_token(userInfo["oauth_token"], userInfo["oauth_secret"])
        twitterUsersApi[userId] = API(auth_handler=auth,
                    host='api.twitter.com', search_host='search.twitter.com',
                    cache=None, secure=False, api_root='/1', search_root='',
                    retry_count=0, retry_delay=0, retry_errors=None, parser=None)
    return twitterUsersApi[userId]
