#!/usr/bin/env python
# coding=utf-8

import urllib
import htmllib

import formatter
import string
import re
import random

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

quotes = []

class parser(htmllib.HTMLParser):

    def __init__(self, verbose=0):
        self.state = 0
        self.output = []
        f = formatter.NullFormatter()
        htmllib.HTMLParser.__init__(self, f, verbose)

    def start_dt(self,attrs):
        for i in attrs:
            if i == ("class","quote"):
                self.state = 1;
                self.save_bgn()
            
    def end_dt(self):
        if self.state == 1:
            self.output.append("%s "%self.save_end())
        self.state = 0;
        
def setup(self):
    self.commands['quote'] = quote
    self.url = "http://www.quotationspage.com/search.php3?homesearch="

def quote(self,e,c):

    line = e.arguments()[0]

    query = string.join(line.split()[1:], "+")
    pg = 1;
    quotes = []

    while 1:
        fd = urllib.urlopen("%s%s&page=%d"%(self.url,query,pg))
        page = fd.read()
        fd.close

        p = parser()
        p.feed(page)

        if len(p.output) < 1:
            break

        pg = pg+1
        quotes.extend(p.output)

    c = self.connection

    if len(quotes) < 1:
        nick = nm_to_n(e.source())
        c.privmsg(e.target(), "%s, ei se kaveri ole koskaan sanonut mitään järkevää."%nick)
        return

    messu = re.sub("\[\d+\]\s?$","",random.choice(quotes))

    c.privmsg(e.target(), "%s"%messu)

