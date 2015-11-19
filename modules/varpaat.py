#!/usr/bin/env python
# coding=utf-8

"""
Simple varpaat script for pefeet.tumblr.com
"""

import urllib2

DEBUG = 1

def setup(self):
    """setup called by oksanen on startup"""
    self.pubcommands['varpaat'] = varpaat_pubcmd

def terminate(self):
    """save data. called by oksanen.reset and .reload"""
    pass

def varpaat_pubcmd(self, e, c):
    """pubcommand varpaat"""
    #req = urllib2.Request(starturl, datagen, headers)
    req = 'http://pefeet.tumblr.com/random'
    res = urllib2.urlopen(req)
    finalurl = res.geturl()
    
    c.privmsg(e.target(), finalurl)
    





