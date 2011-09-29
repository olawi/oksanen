#!/usr/bin/env python
# coding=utf-8

"""
M-x replace-string <RET> bjair <RET> newmodule <RET>
"""
import urllib
import urllib2
import htmllib
import formatter

import HTMLParser

import string
import re

from irclib import nm_to_n
from ircutil import run_once
import ircutil

DEBUG = 1

bjair_url = "http://iphone.bjair.info/index.php"

class bjair_parser(htmllib.HTMLParser):

    def __init__(self, verbose=0):
        self.state = 0
        self.data = ''
        self.status = ''
        self.meaning = ''
        f = formatter.NullFormatter()
        htmllib.HTMLParser.__init__(self, f, verbose)
        
    def start_div(self,attrs):
        for i in attrs:
            if i == ('id','number'):
                self.state = 1
                self.save_bgn()
            elif i == ('id','status'):
                self.state = 2
                self.save_bgn()
            elif i == ('id','meaning'):
                self.state = 3
                self.save_bgn()
            else:
                self.state = 0

    def end_div(self):
        if self.state == 1:
            self.data = "%s"%self.save_end()
            self.state = 0
        elif self.state == 2:
            self.status = "%s"%self.save_end()
            self.state = 0
        elif self.state == 3:
            self.meaning = "%s"%self.save_end()
            self.state = 0
                

def setup(self):
    """setup called by oksanen on startup"""

    self.privcommands['bjair'] = bjair_privcmd
    self.pubcommands['bjair'] = bjair_pubcmd

def terminate(self):
    """save data. called by oksanen.reset and .reload"""
    pass

def help(self):
    """return a help string"""
    s = "bjair help!"

def bjair(self, e, c):
    """module main"""
    fd = urllib.urlopen(bjair_url)
    page = fd.read()
    fd.close

    p = bjair_parser()
    p.feed(page)

    print p.data
    print p.status
    print p.meaning

    m = re.search('\d+ ', p.data)
    if m:
        aqi = m.group(0)

    c.privmsg(e.target(),aqi)


def bjair_privcmd(self, e, c):
    """privcommand bjair"""
    bjair(self,e,c)

def bjair_pubcmd(self, e, c):
    """pubcommand bjair"""
    bjair(self,e,c)



