import sys,random,math,time
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
	    

def go_forward(depth=None):
    global forward,backward,forward_ds,backward_ds,forward_min,backward_min, is_opt
    if not depth or depth==None: 
	depth = get_rand_depth(forward_ds)
    depth += forward_min
    print "forward d=",depth,forward_ds
    for i in range(len(forward)):
	if forward[i]["cursor"] != 0 and len(forward[i]["path"])+1 == depth:
	    user = forward[i]["obj"]
	    ids,cursor = handle_func(user.get_api().friends_ids, user_id=user.id, cursor=forward[i]["cursor"])

	    if len(forward[i]["path"])+2-forward_min not in forward_ds: 
		print "added to forward_ds_1",len(forward[i]["path"])+2-forward_min
		forward_ds.append(len(forward[i]["path"])+2-forward_min)
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
			p = b["path"]+[b["obj"].screen_name,str(id), user.screen_name]+l
			if len(p) < len(r2) or r2==[]:
			    r2=p[:]
	    return r1,r2
    for i in range(len(forward)):
	if forward[i]["cursor_obj"] != 0 and len(forward[i]["path"])+2 == depth:
	    user = forward[i]["obj"]
	    frs,cursor = handle_func(user.get_api().friends,user_id=user.id ,cursor=forward[i]["cursor_obj"])
	    frs.sort()
	    frs.reverse()

	    forward[i]["cursor_obj"] = cursor[1]
	    for f in frs:
		if len(forward[i]["path"])+1 not in forward_ds: 
		    print "addes to forward_ds_2",len(forward[i]["path"])+2 
		    forward_ds.append( len(forward[i]["path"])+1 )
		forward.append({"obj":f, "cursor":-1, "cursor_obj":-1,"path":forward[i]["path"]+[user.screen_name], "friends":[] })
	    return 0,[]
    forward_min += 1
    print "forward min changed ", forward_min, depth,forward_ds
    forward_ds = forward_ds[:-1]
    if is_opt:
	return -1,[]
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
    global forward,backward,forward_ds,backward_ds,forward_min,backward_min, is_opt
    if not depth: depth = get_rand_depth(backward_ds)
    depth+= backward_min
    print "user backward depth=",depth
    for i in range(len(backward)):
	if backward[i]["cursor"] != 0 and len(backward[i]["path"])+1 == depth:
	    user = backward[i]["obj"]
	    
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
			l += [f["obj"].screen_name, str(id), user.screen_name]
			l.reverse()
			
			r1=1
			p = backward[i]["path"]+l
			if len(p)<len(r2) or r2==[]:
			    r2 = p[:]
	    return r1,r2
    for i in range(len(backward)):
	if backward[i]["cursor_obj"] != 0 and len(backward[i]["path"])+2==depth:
	    user = backward[i]["obj"]
	    followers,cursor = handle_func(user.get_api().followers,user_id=user.id, cursor=backward[i]["cursor_obj"])
	    followers.sort()
	    followers.reverse()

	    backward[i]["cursor_obj"] = cursor[1]
	    for f in followers:
		if len(backward[i]["path"])+1 not in backward_ds: backward_ds.append( len(backward[i]["path"])+1 )
		backward.append({"obj":f, "cursor":-1, "cursor_obj":-1,"path":backward[i]["path"]+[user.screen_name], "followers":[] })
	    return 0,[]
    backward_ds = backward_ds[:-1]
    backward_min+=1
    print "backward min changed ", backward_min, depth,backward_ds
    if is_opt:
	return -1,[]
    return go_backward()
    print "SHOULD NOT BE HERE"

"""def get_open_nodes(l, depth, fr=1):
    count = 0
    
    friends = 0
    friends_count = 0
    for el in l:
	#print el["obj"].screen_name
	if len(el["path"]) == depth-1:
	    c= el["obj"].followers_count
	    
	    if fr: c= el["obj"].friends_count
	    count += c
	elif len(el["path"]) == depth:
	    friends += (fr==1 and el["obj"].friends_count or el["obj"].followers_count)
	    friends_count += 1
    return max(count, 1)*max(friends/friends_count, 1)
    
def get_open_nodes(l, min, fr=1):
    global max_step
    count = 0
    for el in l:
	if len(el["path"]) < min:
	    count += (fr==1 and (len(el["friends"]) or 1) ) or len(el["followers"])

    return count"""
def get_open_nodes(l, depth, fr=1):
    count = 0
    
    friends = 0
    friends_count = 0
    for el in l:
	#print el["obj"].screen_name
	if len(el["path"]) == depth-1:
	    c= el["obj"].followers_count
	    
	    if fr: c= el["obj"].friends_count
	    count += c
	elif len(el["path"]) == depth:
	    friends += (fr==1 and el["obj"].friends_count or el["obj"].followers_count)
	    friends_count += 1
    return max(count, 1)*max(friends/(friends_count+1), 1)


	    
def do_min():
    global is_opt,max_step,reqs
    is_opt =1
    #print forward_min,backward_min
    f = get_open_nodes(forward, forward_min, 1)
    b = get_open_nodes(backward, backward_min, 0)
    #print f,b
    
    q = 0

    while max_step-forward_min-backward_min > 0:
	#print q
	if f < b:
	    fin,path = go_forward(1)
	else: 
	    fin,path = go_backward(1)
	if fin != -1: q += 1
	if reqs+q >= 1000: return 0,path,q
	
	if fin == -1:
	    return 0,[],q
	elif fin == 1:
	    max_step = min(max_step, len(path)-2)
	    print "path ",path
    return 1,path,q
forward = []
forward_ds =[1] 
backward_ds = [1]
forward_min = backward_min = 0
backward = []
is_opt  = 0
max_step = 6
if __name__ == "__main__":
    while 1:
        try:
            #outfile = sys.argv[1]
            #auth = tweepy.BasicAuthHandler('reza_shz', 'mehdireza') 
            auth = tweepy.OAuthHandler("xg2hLKvf1nxw1TUALvx5xA", "MkX0lDUik0mJuc6nxserddbQDWd7ZTErQN6Tf0OhOM")
            auth.set_access_token("174566652-MOGbxytlmUHIN5tEMgl5rgqWdWaIQXYZ6XPyYKl1", "yem38OfoUbsoPZvOVr3k0n3X7JSUDYD8oxAKXvrJw6k")
            twitterApi = API(auth_handler=auth,
                    host='api.twitter.com', search_host='search.twitter.com',
                     cache=FileCache("cache", timeout = -1), secure=False, api_root='/1', search_root='',
                    retry_count=0, retry_delay=0, retry_errors=None,
                    parser=None)
                        
            username1 = sys.argv[1]
            username2 = sys.argv[2]
            user1 = twitterApi.get_user(username1) #@UndefinedVariable
            user2 = twitterApi.get_user(username2) #@UndefinedVariable
            
            
            forward = []
	    forward_ds = [1]
	    backward_ds = [1]
	    forward_min = backward_min = 0
	    backward = []
	    is_opt = 0
            
            forward.append({"obj":user1, "cursor":-1, "friends":[], "cursor_obj":-1, "path":[]})
            backward.append({"obj":user2, "cursor":-1, "cursor_obj":-1,"path":[], "followers":[] })
            reqs = 0
            while 1:
		fin, path = go_backward()
		reqs +=1
		if fin: break
		fin,path = go_forward()
		reqs += 1
		if fin: break
	    frs = len(backward)+len(forward)
	    print "####"+",".join([username1, username2, str(len(path)-1), str(frs), str(reqs+2)])
	    
	    max_step = len(path)-2
	    print max_step,forward_min,backward_min
	    while max_step-forward_min-backward_min > 0:
		fin, path2, req = do_min()
		reqs += req
		#if fin: print path2,reqs
		if fin: 
		    max_step = min(max_step, len(path2)-2)
		    print "path2 ", path2
		if fin and len(path2) < len(path): path = path2
		print max_step,forward_min,backward_min
		if reqs >= 1000:
		    reqs=-2
		    break
		
	    
	    print path
	    profiles = len(backward)+len(forward)
	    expands = len([i for i in forward if i["cursor"]!=-1]) + len([i for i in backward if i["cursor"]!=-1])
	    generations = sum([len(i["friends"]) for i in forward]) + sum([len(i["followers"]) for i in backward])
	    print "_"*40+",".join([username1, username2, str(len(path)-1), str(profiles),str(expands),str(generations), str(reqs+2)])
            sys.exit(0)

        except error.TweepError,e:
	    if str(e).find("hour") == -1:
	        print "ENDED: ",sys.argv, str(e),username1,username2
                error.toLog("BAD EXCEPTION: "+str(e))
            handle_exception(e)
            print str(e)
#	        raise e

