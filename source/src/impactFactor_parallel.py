import sys
sys.path.append("../lib/")

from tweeapi.utils import EvalUser
import traceback
from tweeapi import APISingleton
import Queue, threading


class EvalThread(threading.Thread):
    
    def __init__(self, queue):
        self.queue = queue
        threading.Thread.__init__(self)
    
    def run(self):
        global results
        while True:
            user = self.queue.get()
            try:
                results.append(EvalUser.load(user))
            except Exception:
                traceback.print_exc(sys.stderr)
            self.queue.task_done()

if __name__ == "__main__":

    twitterApi = APISingleton.getInstance()
    users = twitterApi.search_users(q=sys.argv[1], per_page=200)
    results = []
    queue = Queue.Queue()
    for i in range(20):
        t = EvalThread(queue)
        t.setDaemon(True)
        t.start()
    
    for u in users:
        queue.put(u)
        queue.join()
    
    results.sort()
    results.reverse()
    for i in results:
        print i
