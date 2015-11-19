#!/usr/bin/env python
# coding=utf-8

"""
Simple varpaat script for pefeet.tumblr.com
"""

import urllib2
import htmllib
import formatter
import random

from irclib import nm_to_n

DEBUG = 1

class Parser(htmllib.HTMLParser):

    def __init__(self, verbose=0):
        self.urls = [];
        f = formatter.NullFormatter()
        htmllib.HTMLParser.__init__(self, f, verbose)
        
    def start_meta(self, attrs):
        if ("property", "og:image") in attrs:
            for attr in attrs:
                if attr[0] == "content":
                    self.urls.append(attr[1])
        
def setup(self):
    """setup called by oksanen on startup"""
    self.pubcommands['varpaat'] = varpaat_pubcmd

def terminate(self):
    """save data. called by oksanen.reset and .reload"""
    pass

def varpaat_pubcmd(self, e, c):
    """pubcommand varpaat"""
    
    nick = nm_to_n(e.source())
    
    req = 'http://pefeet.tumblr.com/random'
    res = urllib2.urlopen(req)
    finalurl = res.geturl()
    
    page = res.read()
    p = Parser()
    p.feed(page)

    if len(p.urls) > 0:
        msg = "%s, " % nick
        msg += random.choice(p.urls)
    else:
        msg = "Sori %s, joudut haistelemaan omiasi" % nick
    
    c.privmsg(e.target(), msg)
    





