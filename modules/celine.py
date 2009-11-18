#!/usr/bin/env python
# coding=utf-8

import random
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

celine_messages = [
    "HYI HELEVETTI!!!",
    "jos vielä kerran mainitset sen kanadalaisen lehmän nimen tällä kanavalla, saat ovesta päähän!",
    "eikö se ole vielä menny perille että siitä sumutorvesta ei puhuta?",
    "voi jeesus mikä lehmä sekin on. Olisit sinäkin vaan hiljaa.",
    "selinen mikäää..? EI NYT SAATANA!"
    ]

def setup(self):
    self.pubhandlers.append(celine)

def celine(self, e, c):
    nick = nm_to_n(e.source())

    line = e.arguments()[0]

    if line.lower().find('celine dion') != -1:
        c.privmsg(e.target(), "%s: %s"%(nick,random.choice(celine_messages)))
