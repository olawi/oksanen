#!/usr/bin/env python
# coding=utf-8

import re
import string
from ircbot import SingleServerIRCBot, Channel
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

uustytto_lista = []

def setup(self):
    self.joinhandlers.append(uustytto)
    
def uustytto(self,e,c):
    
    nick = nm_to_n(e.source())

    snick = re.sub('[^a-zA-Z0-9]','',nick)

    # DEBUG - just printouts so far
    if not snick in uustytto_lista:
        uustytto_lista.append(snick)
        print "uustytto.py : %s uustytto?"%nick
    else:
        print "uustytto.py : %s wanhatytto."%nick
    
