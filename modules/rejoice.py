#!/usr/bin/env python
# coding=utf-8

"""
rejoice - rejoin in a minute if kicked and notify the kicker
"""

import string
import re
import random

from haddock import kiroukset
from irclib import nm_to_n
from ircutil import run_once

DEBUG = 1

def setup(self):
    """setup called by oksanen on startup"""
    self.kickhandlers.append(rejoice)
    try :
        rejoice.kickedme = self.moduledata['rejoice']
    except:
        rejoice.kickedme = {}

def terminate(self):
    """save data. called by oksanen.reset and .reload"""
    self.moduledata['rejoice'] = rejoice.kickedme

def rejoice(self, e, c):
    """called from on_kick"""
    nick = e.arguments()[0]
    channel = e.target()
    whokicked = nm_to_n(e.source())

    if nick == c.get_nickname():
        """kicked me"""
        if nick in rejoice.kickedme:
            rejoice.kickedme[nick] += 1
        else:
            rejoice.kickedme[nick] = 1
        """schedule rejoin"""
        self.cron.add_event({'count':1}, rejoice_rejoin, self, c, channel, whokicked)
    else:
        """goodbye"""        
        if random.choice(range(100)) < 50 :
            if random.choice(range(100)) < 50:
                c.privmsg(channel, "heihei %s"%(nick))
            else:
                c.privmsg(channel, "no jopas %s nyt on pahalla päällä"%(whokicked))
            
def rejoice_rejoin(self, c, channel, whokicked):

    c.join(channel)
    prkl = random.choice(kiroukset)
    run_once(5, c.privmsg, [channel, "%s, senkin %s!"%(whokicked, prkl)])
    
