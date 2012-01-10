import sys
import traceback
sys.path.append("../lib/")

from tweeapi import APISingleton
from tweeapi.utils import EvalUser

if __name__ == "__main__":

    twitterApi = APISingleton.getInstance()

    users = twitterApi.search_users(q=sys.argv[1], per_page=200)
    results = []
    for u in users[:]:
        try:
            eUser = EvalUser.load(u)
            #eUser.save()
            results.append(eUser)
        except Exception,e:
            traceback.print_exc(sys.stdout)
            pass
    results.sort()
    results.reverse()
    for i in results:
        print i
