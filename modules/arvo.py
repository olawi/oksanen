#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

import random

def setup(self):
    self.commands['arvo'] = arvo

def arvo(self, e, c):
    nick = nm_to_n(e.source())

    line = e.arguments()[0]
    them = line.split()[1:]

    c.privmsg(e.target(), "%s: meikä sanoo että %s"%(nick, them[random.randint(0,len(them)-1)]))
