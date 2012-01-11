
from tweepy.utils import parse_datetime, parse_html_value, parse_a_href, \
        parse_search_datetime, unescape_html
import os,time,sys
from tweepy import error

countries = None
followers = None

torBadNodes = "";
def handle_exception(e):
    global torBadNodes
    error.toLog("changing the ip ...."+str(e))
    if sys.argv.count("-no-check") > 0:
        return 0
    if str(e).find("hour") != -1:
        error.toLog("bash -c \"echo authenticate \\\"\\\";echo signal newnym;echo quit \"|nc 127.0.0.1 9051");
        ret = os.popen("bash ~/bin/get_exits.sh").readline()
        ret.strip()
        torBadNodes += ret.replace(" ", "").replace("$", "\$")
        os.system("bash ~/bin/change_ip.sh \""+torBadNodes+"\"")
        time.sleep(10)


def findCountry(city):
    global countries
    if not countries:
	dic = {}
	f = open("cities.out")
	for line in f.readlines():
	    ret = line.split("::")
	    ret = map(str.strip, ret)
	    ret = map(str.lower, ret)
	    cos = ret[1].split("|")
	    if dic.has_key(ret[0]):
		dic[ret[0]]+= cos
	    else:
		dic[ret[0]] = cos
	countries = dic
    if not city:
	return []
    city = city.strip().lower()
    l = city.split(",")
    #l = map(str.strip, l)
    if countries.has_key(l[0]):
	return countries[l[0]]+l
    return l

def checkCountry(u1, u2):
    list1 = findCountry(u1.location)
    list2 = findCountry(u2.location)
    for c in list1:
	if c in list2 and c:
	    return 1
    return 0
    
class ResultSet(list):
    """A list like object that holds results from a Twitter API query."""


class Model(object):

    def __init__(self, api=None):
        self._api = api

    def __getstate__(self):
        # pickle
        pickle = dict(self.__dict__)
        try:
            del pickle['_api']  # do not pickle the API reference
        except KeyError:
            pass
        return pickle

    @classmethod
    def parse(cls, api, json):
        """Parse a JSON object into a model instance."""
        raise NotImplementedError

    @classmethod
    def parse_list(cls, api, json_list):
        """Parse a list of JSON objects into a result set of model instances."""
        results = ResultSet()
        for obj in json_list:
            results.append(cls.parse(api, obj))
        return results


class Status(Model):

    @classmethod
    def parse(cls, api, json):
        status = cls(api)
        for k, v in json.items():
            if k == 'user':
                user = User.parse(api, v)
                setattr(status, 'author', user)
                setattr(status, 'user', user)  # DEPRECIATED
            elif k == 'created_at':
                setattr(status, k, parse_datetime(v))
            elif k == 'source':
                if '<' in v:
                    setattr(status, k, parse_html_value(v))
                    setattr(status, 'source_url', parse_a_href(v))
                else:
                    setattr(status, k, v)
                    setattr(status, 'source_url', None)
            elif k == 'retweeted_status':
                setattr(status, k, Status.parse(api, v))
            else:
                setattr(status, k, v)
        return status

    def destroy(self):
        return self._api.destroy_status(self.id)

    def retweet(self):
        return self._api.retweet(self.id)

    def retweets(self):
        return self._api.retweets(self.id)

    def favorite(self):
        return self._api.create_favorite(self.id)
    
    def __cmp__(self, other):
        if self.screen_name == other.screen_name:
            return 0
        elif self.screen_name > other.screen_name:
            return 1
        return -1


class User(Model):

    @classmethod
    def parse(cls, api, json):
        user = cls(api)
        for k, v in json.items():
            if k == 'created_at':
                setattr(user, k, parse_datetime(v))
            elif k == 'status':
                setattr(user, k, Status.parse(api, v))
            elif k == 'following':
                # twitter sets this to null if it is false
                if v is True:
                    setattr(user, k, True)
                else:
                    setattr(user, k, False)
            else:
                setattr(user, k, v)
        return user

    @classmethod
    def parse_list(cls, api, json_list):
        if isinstance(json_list, list):
            item_list = json_list
        else:
            item_list = json_list['users']

        results = ResultSet()
        for obj in item_list:
            results.append(cls.parse(api, obj))
        return results
    
    def setDst(self, dst):
	self.dst = dst
    
    def __cmp__(self, other):
	if self.protected: return -1
	if other.protected: return 1
	#compare cities
    	if self.friends_count == other.friends_count:
    	    return 0
    	if self.friends_count > other.friends_count:
    	    return 1
    	return -1

    def timeline(self, **kargs):
        return self._api.user_timeline(user_id=self.id, **kargs)

    def friends(self, **kargs):
        return self._api.friends(user_id=self.id, **kargs)
    
    def all_friend_ids(self, **kargs):
	cursor = (-1,-1)
	all_ids = ids = []
	while cursor[1] != 0:
	    try:
		ids,cursor = self._api.friends_ids(user_id=self.id, cursor=cursor[-1], **kargs)
	    except Exception,e:
		handle_exception(e)
	    all_ids += ids
	return all_ids
    
    def all_follower_ids(self, **kargs):
	print "getting follower ids "+self.screen_name
	cursor = (-1,-1)
	all_ids = ids = []
	while cursor[1] != 0:
	    try:
		ids,cursor = self._api.followers_ids(user_id=self.id, cursor=cursor[-1], **kargs)
	    except Exception,e:
		if str(e).find("Not authorized") >= 0:
		   return []
		else:
		    handle_exception(e)
	    all_ids += ids
	print "end all_follower_ids"
	return all_ids
    
    def find_max_friends(self, dst = None, length = 100):
	list = [self]
	cursor = (-1,-1)
	followers[dst.id] = []
	while cursor[1] != 0:
		ids,cursor = self._api.followers_ids(user_id=self.id, cursor=cursor[-1], **kargs) #@UndefinedVariable
		followers[dst.id] += ids

    def followers(self, **kargs):
        return self._api.followers(user_id=self.id, **kargs)

    def all_followers(self, **kargs):
	cursor = (-1,-1)
	all = []
	print "getting followers ",self.screen_name
	while cursor[1] != 0:
	    try:
		followers, cursor = self.followers(cursor=cursor[1], **kargs)
		all += followers
	    except Exception,e:
		handle_exception(e)
	return all

    def all_friends(self, **kargs):
        cursor = (-1,-1)
        all = []
        print "getting followers ",self.screen_name
        while cursor[1] != 0:
            try:
                followers, cursor = self.friends(cursor=cursor[1], **kargs)
                all += followers
            except Exception,e:
                handle_exception(e)
        return all
    
    def get_api(self):
	return self._api
	
    def follow(self):
        self._api.create_friendship(user_id=self.id)
        self.following = True

    def unfollow(self):
        self._api.destroy_friendship(user_id=self.id)
        self.following = False

    def lists_memberships(self, *args, **kargs):
        return self._api.lists_memberships(user=self.screen_name, *args, **kargs)

    def lists_subscriptions(self, *args, **kargs):
        return self._api.lists_subscriptions(user=self.screen_name, *args, **kargs)

    def lists(self, *args, **kargs):
        return self._api.lists(user=self.screen_name, *args, **kargs)

    def followers_ids(self, *args, **kargs):
        return self._api.followers_ids(user_id=self.id, *args, **kargs)


class DirectMessage(Model):

    @classmethod
    def parse(cls, api, json):
        dm = cls(api)
        for k, v in json.items():
            if k == 'sender' or k == 'recipient':
                setattr(dm, k, User.parse(api, v))
            elif k == 'created_at':
                setattr(dm, k, parse_datetime(v))
            else:
                setattr(dm, k, v)
        return dm

    def destroy(self):
        return self._api.destroy_direct_message(self.id)


class Friendship(Model):

    @classmethod
    def parse(cls, api, json):
        relationship = json['relationship']

        # parse source
        source = cls(api)
        for k, v in relationship['source'].items():
            setattr(source, k, v)

        # parse target
        target = cls(api)
        for k, v in relationship['target'].items():
            setattr(target, k, v)

        return source, target


class SavedSearch(Model):

    @classmethod
    def parse(cls, api, json):
        ss = cls(api)
        for k, v in json.items():
            if k == 'created_at':
                setattr(ss, k, parse_datetime(v))
            else:
                setattr(ss, k, v)
        return ss

    def destroy(self):
        return self._api.destroy_saved_search(self.id)


class SearchResult(Model):

    @classmethod
    def parse(cls, api, json):
        result = cls()
        for k, v in json.items():
            if k == 'created_at':
                setattr(result, k, parse_search_datetime(v))
            elif k == 'source':
                setattr(result, k, parse_html_value(unescape_html(v)))
            else:
                setattr(result, k, v)
        return result

    @classmethod
    def parse_list(cls, api, json_list, result_set=None):
        results = ResultSet()
        results.max_id = json_list.get('max_id')
        results.since_id = json_list.get('since_id')
        results.refresh_url = json_list.get('refresh_url')
        results.next_page = json_list.get('next_page')
        results.results_per_page = json_list.get('results_per_page')
        results.page = json_list.get('page')
        results.completed_in = json_list.get('completed_in')
        results.query = json_list.get('query')

        for obj in json_list['results']:
            results.append(cls.parse(api, obj))
        return results


class List(Model):

    @classmethod
    def parse(cls, api, json):
        lst = List(api)
        for k,v in json.items():
            if k == 'user':
                setattr(lst, k, User.parse(api, v))
            else:
                setattr(lst, k, v)
        return lst

    @classmethod
    def parse_list(cls, api, json_list, result_set=None):
        results = ResultSet()
        for obj in json_list['lists']:
            results.append(cls.parse(api, obj))
        return results

    def update(self, **kargs):
        return self._api.update_list(self.slug, **kargs)

    def destroy(self):
        return self._api.destroy_list(self.slug)

    def timeline(self, **kargs):
        return self._api.list_timeline(self.user.screen_name, self.slug, **kargs)

    def add_member(self, id):
        return self._api.add_list_member(self.slug, id)

    def remove_member(self, id):
        return self._api.remove_list_member(self.slug, id)

    def members(self, **kargs):
        return self._api.list_members(self.user.screen_name, self.slug, **kargs)

    def is_member(self, id):
        return self._api.is_list_member(self.user.screen_name, self.slug, id)

    def subscribe(self):
        return self._api.subscribe_list(self.user.screen_name, self.slug)

    def unsubscribe(self):
        return self._api.unsubscribe_list(self.user.screen_name, self.slug)

    def subscribers(self, **kargs):
        return self._api.list_subscribers(self.user.screen_name, self.slug, **kargs)

    def is_subscribed(self, id):
        return self._api.is_subscribed_list(self.user.screen_name, self.slug, id)


class JSONModel(Model):

    @classmethod
    def parse(cls, api, json):
        return json


class IDModel(Model):

    @classmethod
    def parse(cls, api, json):
        if isinstance(json, list):
            return json
        else:
            return json['ids']


class ModelFactory(object):
    """
    Used by parsers for creating instances
    of models. You may subclass this factory
    to add your own extended models.
    """

    status = Status
    user = User
    direct_message = DirectMessage
    friendship = Friendship
    saved_search = SavedSearch
    search_result = SearchResult
    list = List

    json = JSONModel
    ids = IDModel

