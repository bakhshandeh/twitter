from tweeapi import APISingleton
from db import DBSingleton
import pickle
import psycopg2.extras
from tweeapi.IR import getTFIDFArray, getSim
import traceback
import sys
import random
from tweepy.models import handle_exception

class EvalUser:

    def __init__(self, user, retweetFactor=None, impactFactor=None, mcFactor=None, TFIDFArray = None):
        self._api = APISingleton.getInstance()
        self.id = user.id
        self.screen_name = user.screen_name
        self.userObj = user
        self.retweetFactor = retweetFactor
        self.impactFactor = impactFactor
        self.mcFactor = mcFactor
        self.TFIDFArray = TFIDFArray
        self.similarity = None
        if retweetFactor == None:
            self.retweetFactor = self.__calcRetweetFactor()
            self.impactFactor = self.__calcImpactFactor()
            self.TFIDFArray = self._calcTFIDF()
    
    @classmethod
    def loadFromDB(cls,userId, userObj = None):
        cur = DBSingleton.getInstance().cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * from users where id=%s;",(userId, ))
        row = cur.fetchone()
        if row:
            return cls.loadFromDBRow(row)
        return cls.loadFromTwitter(userId, userObj)
    
    @classmethod
    def loadFromDBRow(cls, row):
        print "FROM USERS DB"
        userObj = pickle.loads(row["obj_data"])
        
        tfidf = None
        if row["tfidf"] and len(row["tfidf"]):
            tfidf = pickle.loads(row["tfidf"])
        return cls(userObj, row["retweet_factor"], row["impact_factor"], row["mc_factor"], tfidf)
    
    @classmethod
    def loadFromTwitter(cls, userId, userObj = None):
        if not userObj:
            userObj = APISingleton.getInstance().get_user(user_id=userId)
        ret = cls(userObj)
        ret.save()
        return ret
    
    def getUserObj(self):
        return self.userObj 
        
    def getImpactFactor(self):
        return self.impactFactor
    
    def getRetweetFactor(self):
        return self.retweetFactor
    
    def getTFIDFArray(self):
        if self.TFIDFArray:
            return self.TFIDFArray
        self.TFIDFArray = self._calcTFIDF()
        self.saveTFIDF()
        return self.TFIDFArray
    
        
    def __calcRetweetFactor(self):
        tweets = self._api.user_timeline(user_id=self.id, count=200, include_rts=1)
        retweets = len([i for i in tweets if  hasattr(i, "retweeted_status")])
        return retweets/len(tweets)
    
    def __calcImpactFactor(self):
        friends = self._api.friends_ids(user_id=self.id)
        friends_ids = friends[0]
        
        followers = self._api.followers_ids(user_id=self.id)
        followers_ids = followers[0]
        
        impact = 0
        if len(followers_ids):
            impact = len(list(set(followers_ids) & set(friends_ids)))/(len(followers_ids)+0.0000)
        return impact
    
    def _calcTFIDF(self):
        tweets = self._api.user_timeline(user_id=self.id, count=200, include_rts=1)
        tfidf = getTFIDFArray([t.text for t in tweets])
        return tfidf
    
    def saveTFIDF(self):
        if not self.TFIDFArray:
            return
        db = DBSingleton.getInstance()
        cursor = db.cursor()
        try:
            cursor.execute("update users set tfidf=%s where id=%s;" ,
                           (pickle.dumps(self.getTFIDFArray()), self.id))
            db.commit()
        except Exception,e:
            db.rollback()
            print e

    def __str__(self):
        return self.screen_name+" "+str(self.getRetweetFactor()) + " " + str(self.getImpactFactor())+" "+str(self.getSim(self.getTFIDFArray()))

    def __cmp__(self, other):
        slf = float(self.getRetweetFactor()*self.getImpactFactor()*self.getSim())
        othr = float(other.getRetweetFactor()*other.getImpactFactor()*other.getSim())
        if slf > othr:
            return 1
        if slf == othr:
            return 0
        return -1
    
    def save(self):
        print "SAVE"
        db = DBSingleton.getInstance()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT into users(id, screen_name, obj_data, retweet_factor, impact_factor, mc_factor, tfidf) "+
                "values(%s, %s, %s, %s, %s, %s, %s);", 
                (self.id, self.screen_name, pickle.dumps(self.userObj), self.retweetFactor, self.impactFactor, 0, pickle.dumps(self.TFIDFArray)))
            db.commit()
        except Exception,e:
            db.rollback()
            print e
            #traceback.print_exc(sys.stdout)
            
    def getData(self):
        dic = {}
        dic["screen_name"] = self.userObj.screen_name
        dic["id"] = self.userObj.id
        dic["description"] = self.userObj.description
        dic["profile_image_url"] = self.userObj.profile_image_url
        dic["retweet_factor"] = min(self.getRetweetFactor(),0.9)
        dic["impact_factor"] = self.getImpactFactor()
        dic["mc_factor"] = self.mcFactor
        dic["sim"] = self.getSim()
        return dic

    @classmethod
    def load(cls, user):
        return cls.loadFromDB(user.id, user)
    
    def getSim(self, TFIDFArray=None):
        if self.similarity == None:
            if TFIDFArray == None:
                TFIDFArray = self.getTFIDFArray()
            self.similarity = getSim(TFIDFArray, self.getTFIDFArray())
        return self.similarity
         
    
    def BFS(self, count, random_walk=False):
        #selfTweets = self._api.user_timeline(user_id=self.id, count=100, include_rts=1)
        #selfTFIDFArray = getTFIDFArray([t.text for t in selfTweets])
        
        friends = self._api.followers_ids(user_id=self.id)[0]
        count = min(count, len(friends))
        if random_walk:
            friends = random.sample(friends, count)
        else:
            friends = friends[:count]
        eUsers = []
        for frId in friends:
            try:
                eUser = EvalUser.loadFromDB(frId)
                #frTweets = self._api.user_timeline(user_id=frId, count=100, include_rts=1)
                #frTFIDFArray = getTFIDFArray([t.text for t in frTweets])
                
                if eUser.getSim(self.getTFIDFArray()) > 0.1:
                    eUsers.append(eUser)
            except Exception,e:
                handle_exception(e)
                print "ERROR: ",e
                pass
        return eUsers
            #print self, eUser, "sim: ", getSim(frTFIDFArray, selfTFIDFArray)
            
        
    
        