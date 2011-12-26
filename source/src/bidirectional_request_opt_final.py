import sys,random,time
sys.path.append("../lib/")

from tweepy import api, error
from tweepy.cache import FileCache
from tweepy.api import API
import tweepy
from tweepy.models import *

def writeOut(filename, txt):
    f = open(filename, 'a');
    f.write(txt)
    f.close()
    
def has_node(list):
    for i in list:
	if i["cursor"] != 0:
	    return 1
    
    for i in range(len(list)-1):
	if list[i]["path"] == [] and list[i]["cursor_obj"] != 0:
	    return 1
	if len(list[i]["path"]) == len(list[i+1]["path"]) and list[i]["cursor_obj"]==0 and list[i+1]["cursor_obj"]!=0:
	    return 1
	if len(list[i]["path"]) == len(list[i+1]["path"]) and list[i]["cursor_obj"]!=-1 and list[i+1]["cursor_obj"]==-1:
	    return 1
	if len(list[i]["path"]) == len(list[i+1]["path"])-1 and (list[i]["cursor_obj"]!=-1 and list[i]["cursor_obj"]!=0):
	    return 1
	
	
    return 0

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

def go_forward():
    global forward,backward
    for i in range(len(forward)):
	if forward[i]["cursor"] != 0:
	    user = forward[i]["obj"]
	    print "get FRIENDS of ",user.screen_name,user.friends_count,len(forward[i]["path"])
	    ids,cursor = handle_func(user.get_api().friends_ids, user_id=user.id, cursor=forward[i]["cursor"])
	    
	    forward[i]["cursor"] = cursor[1]
	    forward[i]["friends"] += ids
	    
	    for id in ids:
		for b in backward:
		    if id in b["followers"]:
			l = forward[i]["path"][:]
			l.reverse()
			print l
			return 1,b["path"]+[b["obj"].screen_name,str(id), user.screen_name]+l
	    return 0,[]
    for i in range(len(forward)):
	if forward[i]["cursor_obj"] != 0:
	    user = forward[i]["obj"]
	    frs,cursor = handle_func(user.get_api().friends, user_id=user.id, cursor=forward[i]["cursor_obj"])

	    forward[i]["cursor_obj"] = cursor[1]
	    for f in frs:
		forward.append({"obj":f, "cursor":-1, "cursor_obj":-1,"path":forward[i]["path"]+[user.screen_name], "friends":[] })
	    return 0,[]
    print "SHOULD NOT BE HERE FORWARD"
    """ expand b
    user = forward[-1]["obj"]
    frs,cur = user.friends(cursor=-1)
    frs.sort()
    frs.reverse()
    elm={"obj":frs[0], "cursor":-1, "friends":[]}
    forward.append(elm)
    return 0,[]        """
 
def go_backward():
    global forward,backward
    for i in range(len(backward)):
	if backward[i]["cursor"] != 0:
	    user = backward[i]["obj"]
	    print "get followers of ",user.screen_name,user.followers_count,len(backward[i]["path"])
	    ids,cursor = handle_func(user.get_api().followers_ids, user_id=user.id, cursor=backward[i]["cursor"])
	    
	    backward[i]["cursor"] = cursor[1]
	    backward[i]["followers"]+=ids
	    
	    for id in ids:
		l=[]
		for f in forward:
		    if id in f["friends"]:
			#print user.screen_name,user.get_api().get_user(user_id=id).screen_name,f["obj"].screen_name,backward[i]["path"]
			#print f["obj"].screen_name,f["path"]
			l = f["path"][:]
			l += [f["obj"].screen_name, str(id), user.screen_name]
			l.reverse()
			return 1,backward[i]["path"]+l
	    return 0,[]
    for i in range(len(backward)):
	if backward[i]["cursor_obj"] != 0:
	    user = backward[i]["obj"]
	    followers,cursor = handle_func(user.get_api().followers, user_id=user.id, cursor=backward[i]["cursor_obj"])

	    backward[i]["cursor_obj"] = cursor[1]
	    for f in followers:
		backward.append({"obj":f, "cursor":-1, "cursor_obj":-1,"path":backward[i]["path"]+[user.screen_name], "followers":[] })
	    return 0,[]
    print "SHOULD NOT BE HERE"
    
    
forward = []
backward = []
if __name__ == "__main__":
    while 1:
        try:
    	    forward = []
    	    backward = []
            #outfile = sys.argv[1]
            #auth = tweepy.BasicAuthHandler('reza_shz', 'mehdireza') 
            auth = tweepy.OAuthHandler("xg2hLKvf1nxw1TUALvx5xA", "MkX0lDUik0mJuc6nxserddbQDWd7ZTErQN6Tf0OhOM")
            auth.set_access_token("174566652-MOGbxytlmUHIN5tEMgl5rgqWdWaIQXYZ6XPyYKl1", "yem38OfoUbsoPZvOVr3k0n3X7JSUDYD8oxAKXvrJw6k")
            twitterApi = API(auth_handler=auth,
                    host='api.twitter.com', search_host='search.twitter.com',
                     cache=FileCache("cache", timeout = -1), secure=False, api_root='/1', search_root='',
                    retry_count=0, retry_delay=0, retry_errors=None,
                    parser=None)
                        
            #username1, username2,listUsernames = readFile(outfile)
            user1 = twitterApi.get_user(sys.argv[1]) #@UndefinedVariable
            user2 = twitterApi.get_user(sys.argv[2]) #@UndefinedVariable
            
            forward.append({"obj":user1, "cursor":-1, "friends":[], "cursor_obj":-1, "path":[]})
            backward.append({"obj":user2, "cursor":-1, "cursor_obj":-1,"path":[], "followers":[] })
            reqs = 0
            while 1:
        	fin, path = go_backward()
		reqs +=1;print reqs
		if fin: print path;reqs=-2;break
        	while has_node(backward):
		    fin, path = go_backward()
		    reqs +=1;print reqs
		    if fin or reqs >= 1000: print path;break
		if fin: break
		if reqs >= 1000: reqs=-2;break
		    
		fin,path = go_forward()
		reqs += 1
		if fin: print path;break
		if reqs >= 1000: reqs=-2;break
		while has_node(forward):
		    fin,path = go_forward()
		    reqs += 1;print reqs
		    if fin or reqs >= 1000: print path;break 
		if fin: break
		if reqs >= 1000:
		    reqs = -2
		    break
	    
	    profiles = len(backward)+len(forward)
    	    expands = len([i for i in forward if i["cursor"]!=-1]) + len([i for i in backward if i["cursor"]!=-1])
    	    generations = sum([len(i["friends"]) for i in forward]) + sum([len(i["followers"]) for i in backward])
    	    print "_"*40+",".join([sys.argv[1], sys.argv[2], str(len(path)-1), str(profiles),str(expands),str(generations), str(reqs+2)])
    	    sys.exit(0)

        except error.TweepError,e:
	    if str(e).find("hour") == -1:
	        print "ENDED: ", str(e),sys.argv
                error.toLog("BAD EXCEPTION: "+str(e))
	    print e