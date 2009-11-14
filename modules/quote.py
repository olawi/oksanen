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

quote_url = "http://www.quotationspage.com/search.php3?homesearch="
quote_nfm = [
    "ei se kaveri ole koskaan sanonut mit‰‰n j‰rkev‰‰",
    "en m‰ nyt kuule jaksa. Googlaa itte?",
    "kuka se semmonen muka on?",
    "koskaan kuullukkaan koko tyypist‰!",
    "ei mun tietokannassa nyt ihan jokaista ole joka on joskus jotakin suustaan p‰‰st‰nyt.",
    "valitettavasti nyt kuule en. Ei nimitt‰in lˆydy."
    ]

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

def quote(self,e,c):

    line = e.arguments()[0]

    query = string.join(line.split()[1:], "+")
    pg = 1;

    # Get the first page and see it there is more
    fd = urllib.urlopen("%s%s&page=%d"%(quote_url,query,pg))
    page = fd.read()
    fd.close

    m = re.search('age \d of (\d+)',page)

    if m:
        pg = random.randint(1,int(m.group(1)))
    
    if pg != 1:
        fd = urllib.urlopen("%s%s&page=%d"%(quote_url,query,pg))
        page = fd.read()
        fd.close
    
    p = parser()
    p.feed(page)
    
    if len(p.output) < 1:
        nick = nm_to_n(e.source())
        c.privmsg(e.target(), "%s, %s"%(nick,random.choice(quote_nfm)))
        return
    
    c = self.connection
    messu = re.sub("\[\d+\]\s?$","",random.choice(p.output))
    # messu += " (%s, page %d of %d)"%(query,pg,int(m.group(1)))
    c.privmsg(e.target(), "%s"%messu)

