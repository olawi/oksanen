#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

def setup(self):
    self.pubhandlers.append(urlhandler)

def urlhandler(self, e, c):
    nick = nm_to_n(e.source())

    line = e.arguments()[0]

#    c.privmsg(e.target(), "%s sez %s"%(nick, line))