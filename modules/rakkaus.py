#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

import hashlib
import string

def setup(self):
    self.pubcommands['rakkaus'] = rakkaus
    self.pubcommands['love'] = rakkaus

def rakkaus(self, e, c):
    nick = nm_to_n(e.source())

    line = e.arguments()[0]
    target = string.join(line.split()[1:], " ")
    if (target and len(target) > 0):
        m = hashlib.sha1()
        m.update(nick)
        m.update(target)
        digest = m.digest()
        score = 0
        for i in range(0,len(digest)-1):
            score += ord(digest[i])

        c.privmsg(e.target(), "%s <3 %s: %d%%"%(nick, target, score % 101))
