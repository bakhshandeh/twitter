# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

class TweepError(Exception):
    """Tweepy exception"""

    def __init__(self, reason, response=None):
        self.reason = str(reason)
        self.response = response

    def __str__(self):
        return self.reason

    def torStr(self):
	return self.reason

class toLog:
    def __init__(self, txt, file="log.txt"):
	f = open(file, "a")
	f.write(txt + "\n")
	f.close()
