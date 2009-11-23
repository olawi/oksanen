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
                c.privmsg(e.target(),"%s, odotahan vielä, muutkin haluavat kuolla."%nick)
                ruletti.warnings[nick] = 1
                return
            else:
                return
        else:
            ruletti.shooters[nick] = time.time()
            ruletti.warnings[nick] = 0
            

    r = random.randint(1,6)
    cursor = self.db.cursor()
    if  r == 1:
        sqlquery = """INSERT INTO gamescores (user,ruletti,ruletti_bang) VALUES (%s,1,1) ON DUPLICATE KEY UPDATE ruletti = ruletti + 1,ruletti_bang = ruletti_bang + 1;"""
        c.kick(e.target(),nick,"*BANG*")
    else:
        sqlquery = """INSERT INTO gamescores (user,ruletti) VALUES (%s,1) ON DUPLICATE KEY UPDATE ruletti = ruletti + 1;"""
        c.privmsg(e.target(),"%s, *click*"%nick)
    cursor.execute(sqlquery, [nick] )
    cursor.close()
    
