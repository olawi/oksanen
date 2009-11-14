#!/usr/bin/env python
# coding=utf-8

import re
import string

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_u

from girlnames import girlnames

uustytto_lista = []

def setup(self):
    self.joinhandlers.append(uustytto)
    
def uustytto(self,e,c):
    
    nick = nm_to_n(e.source())

    self.whoiscallbacks.insert(0,uustytto_callback)
    c.send_raw("WHOIS %s"%nick)

def uustytto_callback(self,e,c):

    nick = self.whoisinfo['user'][0]
    snick = re.sub('[^a-zA-Z0-9]','',nick)
    
    realname = self.whoisinfo['user'][4]

    firstname = realname.split()[0]

    if string.lower(firstname) in girlnames :
        print " TYTTÖ! ----> %s"%realname
        if not snick in uustytto_lista:
            uustytto_lista.append(snick)
            print "uustytto.py : %s uustytto?"%nick
        else :
            print "uustyttö.py : %s wanhatyttö :("%nick
