import sys,random,math,time
sys.path.append("../lib/")

from tweepy import api, error
from tweepy.cache import FileCache,DBCache, DBFileCache
from tweepy.api import API
import tweepy
from tweepy.models import *
from tweeapi import *

def writeOut(filename, txt):
    f = open(filename, 'a');
    f.write(txt)
    f.close()


def readFile(fileName):
    f = open(fileName)
    lines = f.readlines()
    s = lines[0]
    s = s.replace("end: ", "")
    s = s.replace("start: ", "")
    s= s.replace("\n", "")
    s = s.replace(" ", "")
    l = s.split()
    username1,username2 = l[0],l[1];
    
    list = []
    for line in lines[1:]:

	list.append(line.replace("\n", ""))
    f.close()
    return list[-1],username2,list

def get_rand_depth(l):
    l2 = []
    for el in l:
	l2.append(math.exp(-2*el))
    summ = sum(l2)
    rnd = random.random()
    ret = 1
    ad = 0
    for el in l2:
	if el/summ+ad >= rnd:
	    #print "selected depth ",ret
	    return ret
	else:
	    ret += 1
	    ad += el/summ
    print "get_rand not be here ..."

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

def go_forward(depth=None):
    global forward,backward,forward_ds,backward_ds,forward_min,backward_min
    if not depth or depth==None: 
	depth = get_rand_depth(forward_ds)
    depth += forward_min
    #print "forward d=",depth
    for i in range(len(forward)):
	if forward[i]["cursor"] != 0 and len(forward[i]["path"])+1 == depth:
	    user = forward[i]["obj"]
	    ids,cursor = handle_func(user.get_api().friends_ids, user_id=user.id, cursor=forward[i]["cursor"])

	    if len(forward[i]["path"])+2-forward_min not in forward_ds: forward_ds.append(len(forward[i]["path"])+2-forward_min)
	    forward[i]["cursor"] = cursor[1]
	    forward[i]["friends"] += ids
	    
	    r1=0
	    r2=[]
	    for id in ids:
		for b in backward:
		    if id in b["followers"]:
			l = forward[i]["path"][:]
			l.reverse()
			#print l
			r1 = 1
			p = b["path"]+[b["obj"].screen_name,twitterApi.get_user(user_id=id).screen_name, user.screen_name]+l
			if len(p) < len(r2) or r2==[]:
			    r2=p[:]
	    return r1,r2
    for i in range(len(forward)):
	if forward[i]["cursor_obj"] != 0 and len(forward[i]["path"])+2 == depth:
	    user = forward[i]["obj"]
	    frs,cursor = handle_func(user.get_api().friends,user_id=user.id, cursor=forward[i]["cursor_obj"])
	    frs.sort()
	    frs.reverse()

	    forward[i]["cursor_obj"] = cursor[1]
	    for f in frs:
		if len(forward[i]["path"])+1 not in forward_ds: forward_ds.append( len(forward[i]["path"])+1 )
		forward.append({"obj":f, "cursor":-1, "cursor_obj":-1,"path":forward[i]["path"]+[user.screen_name], "friends":[] })
	    return 0,[]
    forward_min += 1
    forward_ds = forward_ds[:-1]

    return go_forward()
    print "SHOULD NOT BE HERE FORWARD"
    """ expand b
    user = forward[-1]["obj"]
    frs,cur = user.friends(cursor=-1)
    frs.sort()
    frs.reverse()
    elm={"obj":frs[0], "cursor":-1, "friends":[]}
    forward.append(elm)
    return 0,[]        """
 
def go_backward(depth=None):
    global forward,backward,forward_ds,backward_ds,forward_min,backward_min
    if not depth: depth = get_rand_depth(backward_ds)
    depth+= backward_min
    #print "backward d=",depth
    for i in range(len(backward)):
	if backward[i]["cursor"] != 0 and len(backward[i]["path"])+1 == depth:
	    user = backward[i]["obj"]
	    #print "Expanding user with user_id=",user.id
	    ids,cursor = handle_func(user.get_api().followers_ids, user_id=user.id, cursor=backward[i]["cursor"])

	    if len(backward[i]["path"])+2-forward_min not in backward_ds: backward_ds.append(len(backward[i]["path"])+2-forward_min)
	    backward[i]["cursor"] = cursor[1]
	    backward[i]["followers"]+=ids
	    
	    r1=0
	    r2=[]
	    for id in ids:
		l=[]
		for f in forward:
		    if id in f["friends"]:
			#print user.screen_name,user.get_api().get_user(user_id=id).screen_name,f["obj"].screen_name,backward[i]["path"]
			#print f["obj"].screen_name,f["path"]
			l = f["path"][:]
			l += [f["obj"].screen_name, twitterApi.get_user(user_id=id).screen_name, user.screen_name]
			l.reverse()
			
			r1=1
			p = backward[i]["path"]+l
			if len(p)<len(r2) or r2==[]:
			    r2 = p[:]
	    return r1,r2
    for i in range(len(backward)):
	if backward[i]["cursor_obj"] != 0 and len(backward[i]["path"])+2==depth:
	    user = backward[i]["obj"]
	    followers,cursor = handle_func(user.get_api().followers, user_id=user.id, cursor=backward[i]["cursor_obj"])
	    followers.sort()
	    followers.reverse()

	    backward[i]["cursor_obj"] = cursor[1]
	    for f in followers:
		if len(backward[i]["path"])+1 not in backward_ds: backward_ds.append( len(backward[i]["path"])+1 )
		backward.append({"obj":f, "cursor":-1, "cursor_obj":-1,"path":backward[i]["path"]+[user.screen_name], "followers":[] })
	    return 0,[]
    backward_ds = backward_ds[:-1]
    backward_min+=1

    return go_backward()
    print "SHOULD NOT BE HERE"
    
    
forward = []
forward_ds = backward_ds = [1]
forward_min = backward_min = 0
backward = []
if __name__ == "__main__":
    twitterApi = APISingleton.getInstance()
    while 1:
        try:
            #outfile = sys.argv[1]
            #auth = tweepy.BasicAuthHandler('reza_shz', 'mehdireza') 
            #auth = tweepy.OAuthHandler("xg2hLKvf1nxw1TUALvx5xA", "MkX0lDUik0mJuc6nxserddbQDWd7ZTErQN6Tf0OhOM")
            #auth.set_access_token("174566652-MOGbxytlmUHIN5tEMgl5rgqWdWaIQXYZ6XPyYKl1", "yem38OfoUbsoPZvOVr3k0n3X7JSUDYD8oxAKXvrJw6k")

            """twitterApi = API(auth_handler=auth,
                    host='api.twitter.com', search_host='search.twitter.com',
                     cache=DBFileCache(DBCache(timeout=-1), FileCache("cache", timeout=-1), timeout = -1), secure=False, api_root='/1', search_root='',
                    retry_count=0, retry_delay=0, retry_errors=None,
                    parser=None)"""
            
                        
            username1, username2 = sys.argv[1],sys.argv[2]
            user1 = twitterApi.get_user(username1) #@UndefinedVariable
            user2 = twitterApi.get_user(username2) #@UndefinedVariable
            
            
            forward = []
	    forward_ds = [1]
	    backward_ds = [1]
	    forward_min = backward_min = 0
	    backward = []
            
            forward.append({"obj":user1, "cursor":-1, "friends":[], "cursor_obj":-1, "path":[]})
            backward.append({"obj":user2, "cursor":-1, "cursor_obj":-1,"path":[], "followers":[] })
            reqs = 0
            while 1:
		fin, path = go_backward()
		reqs +=1
		if fin: break
		fin,path = go_forward()
		#print "hi2 ....."
		reqs += 1
		if fin: break
	    path.reverse()
	    
	    
	    profiles = len(backward)+len(forward)
	    expands = len([i for i in forward if i["cursor"]!=-1]) + len([i for i in backward if i["cursor"]!=-1])
	    generations = sum([len(i["friends"]) for i in forward]) + sum([len(i["followers"]) for i in backward])
	    
	    print "Length of the path: ",len(path)-1
	    print "Number of expanded users: ",expands+1
	    print "Total number of visited friends: ", generations
	    print "Number of requests sent to Twitter: ",reqs+2
	    print ",".join(path)
	    
	    print "_"*40+",".join([username1, username2, str(len(path)-1), str(profiles),str(expands),str(generations), str(reqs+2)])
            sys.exit(0)

        except error.TweepError,e:
	    if str(e).find("hour") == -1:
	        print "ENDED: ",sys.argv, str(e),username1,username2
                error.toLog("BAD EXCEPTION: "+str(e))
                import sys
                sys.exit(0)
            handle_exception(e)
            print str(e)
#	        raise e

