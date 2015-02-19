#!/usr/bin/env python
# coding=utf-8

import random
import time
import numpy

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad
from oksanen import hasSql

ruletti_wait = 5*60
ruletti_bantime = 1

def setup(self):
    self.pubcommands['ruletti'] = ruletti
    ruletti.shooters = {}
    ruletti.warnings = {}

def ruletti_unban(self, e, c):
    nick = nm_to_n(e.source())
    c.mode(e.target(), "-b %s"%e.source())
    c.invite(nick, e.target())
    c.privmsg(e.source(),"tuu takasi, kengät kuluu")
    
def ruletti(self, e, c):

    nick = nm_to_n(e.source())

    print ruletti.shooters
    print time.time()

    if not nick in ruletti.shooters :
        ruletti.shooters[nick] = time.time()
    else:
        if (time.time() - ruletti.shooters[nick]) < random.randint(60,ruletti_wait) :
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
    print e.source()

    if r == 1:
        c.kick(e.target(), nick, "*BANG*")
        c.mode(e.target(), "+b %s"%e.source())
        d_mins = numpy.round(numpy.random.standard_gamma(1)*30)
        t_kick = datetime.now() + timedelta (minutes = r_minutes)
        self.cron.add_event({'count':1, 'hour':[t_kick.hour], 'minute':[t_kick.mins]}, ruletti_unban, self, e, c)
    else:
        c.privmsg(e.target(),"%s, *click*"%nick)  
    
    if hasSql:
        cursor = self.db.cursor()
        if  r == 1:
            sqlquery = """INSERT INTO gamescores (user,ruletti,ruletti_bang) VALUES (%s,1,1) ON DUPLICATE KEY UPDATE ruletti = ruletti + 1,ruletti_bang = ruletti_bang + 1;"""
        else:
            sqlquery = """INSERT INTO gamescores (user,ruletti) VALUES (%s,1) ON DUPLICATE KEY UPDATE ruletti = ruletti + 1;"""
        cursor.execute(sqlquery, [nick] )
        cursor.close()
    
