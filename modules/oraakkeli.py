#!/usr/bin/env python
# coding=utf-8

import urllib
import htmllib
import string
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad
import ircutil

oraakkeli_url = "http://www.lintukoto.net/viihde/oraakkeli/index.php?html=0&kysymys="

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
    query = ircutil.recode(query,'latin-1')
    
    fd = urllib.urlopen("%s%s"%(oraakkeli_url,query))
    reply = fd.read()
    fd.close
    
    c = self.connection
    c.privmsg(e.target(), "%s, %s"%(nick,reply))


