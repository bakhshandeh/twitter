from tweeapi import APISingleton
from db import DBSingleton
import pickle
import psycopg2.extras

class EvalUser:

    def __init__(self, user, retweetFactor=None, impactFactor=None, mcFactor=None):
        self._api = APISingleton.getInstance()
        self.id = user.id
        self.screen_name = user.screen_name
        self.userObj = user
        self.retweetFactor = retweetFactor
        self.impactFactor = impactFactor
        self.mcFactor = mcFactor
        if retweetFactor == None:
            self.retweetFactor = self.__calcRetweetFactor()
            self.impactFactor = self.__calcImpactFactor()
    
    @classmethod
    def loadFromDB(cls,userId):
        cur = DBSingleton.getInstance().cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * from users where id=%s",(userId, ))
        row = cur.fetchone()
        if row:
            return cls.loadFromDBRow(row)
        return cls.loadFromTwitter(userId)
    
    @classmethod
    def loadFromDBRow(cls, row):
        userObj = pickle.loads(row["obj_data"])
        return cls(userObj, row["retweet_factor"], row["impact_factor"], row["mc_factor"])
    
    @classmethod
    def loadFromTwitter(cls, userId):
        userObj = APISingleton.getInstance().get_user(user_id=userId)
        ret = cls(userObj)
        ret.save()
        return ret
        
    def getImpactFactor(self):
        return self.impactFactor
    
    def getRetweetFactor(self):
        return self.retweetFactor
        
    def __calcRetweetFactor(self):
        tweets = self._api.user_timeline(user_id=self.id, count=100, include_rts=1)
        retweets = len([i for i in tweets if  hasattr(i, "retweeted_status")])
        return retweets/100.00
    
    def __calcImpactFactor(self):
        friends = self._api.friends_ids(user_id=self.id)
        friends_ids = friends[0]
        
        followers = self._api.followers_ids(user_id=self.id)
        followers_ids = followers[0]
        
        impact = len(list(set(followers_ids) & set(friends_ids)))/(len(followers_ids)+0.0000)
        return impact

    def __str__(self):
        return self.screen_name+" "+str(self.getRetweetFactor())+ " " + str(self.getImpactFactor())

    def __cmp__(self, other):
        slf = float(self.getRetweetFactor()*self.getImpactFactor())
        othr = float(other.getRetweetFactor()*other.getImpactFactor())
        if slf > othr:
            return 1
        if slf == othr:
            return 0
        return -1
    
    def save(self):
        db = DBSingleton.getInstance()
        cursor = db.cursor()
        cursor.execute("INSERT into users(id, screen_name, obj_data, retweet_factor, impact_factor, mc_factor) "+
                "values(%s, %s, %s, %s, %s, %s);", (self.id, self.screen_name, pickle.dumps(self.userObj), self.retweetFactor, self.impactFactor, 0))
        db.commit()

    
    @classmethod
    def load(cls, user):
        return cls.loadFromDB(user.id)
    
    
        