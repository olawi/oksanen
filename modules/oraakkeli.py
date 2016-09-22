#!/usr/bin/env python
# coding=utf-8

from urllib import FancyURLopener
import htmllib
import string
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad
import ircutil

oraakkeli_url = "http://www.lintukoto.net/viihde/oraakkeli/index.php?html=0&kysymys="

class opener(FancyURLopener):
    version = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.246.0 Safari/532.5'

def setup(self):
    self.pubcommands['?'] = oraakkeli
    
def oraakkeli(self,e,c):

    line = e.arguments()[0]
    nick = nm_to_n(e.source())
    
    query = string.join(line.split()[1:], " ")
    
    if not len(query):
        c.privmsg(e.target(), "%s, mitä vittua nää yrität?"%(nick))
        return

    # lintukoto expects latin-1
    #query = ircutil.recode(query,'latin-1')
    
    opr = opener()
    
    uri = "%s%s"%(oraakkeli_url,query)

    try:
        fd = opr.open(uri)
    except:
        print "url.py: FAIL opening %s"%uri
        c.privmsg(e.target(), "Sori, oraakkeli on nyt lomalla?")
        return
    
    reply = fd.read()
    fd.close
    
    if reply.startswith('<'):
        reply = "nyt en kuule jouda vastaamaan."
    
    c = self.connection
    c.privmsg(e.target(), "%s, %s"%(nick,reply))


