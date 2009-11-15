#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

import random
import time

rulettiWAIT = 300

def setup(self):
    self.commands['ruletti'] = ruletti
    ruletti.shooters = {}
    ruletti.warnings = {}

def ruletti(self,e,c):

    nick = nm_to_n(e.source())

    print ruletti.shooters
    print time.time()

    if not nick in ruletti.shooters :
        ruletti.shooters[nick] = time.time()
    else:
        if (time.time() - ruletti.shooters[nick]) < rulettiWAIT :
            if not nick in ruletti.warnings or ruletti.warnings[nick] == 0 :
                c.privmsg(e.target(),"%s, odotahan viel�, muutkin haluavat kuolla."%nick)
                ruletti.warnings[nick] = 1
                return
            else:
                return
        else:
            ruletti.shooters[nick] = time.time()
            ruletti.warnings[nick] = 0
            

    r = random.randint(1,6)
    if  r == 1:
        c.privmsg(e.target(),"%s, *PAM*"%nick)
    else:
        c.privmsg(e.target(),"%s, *click*"%nick)

    
