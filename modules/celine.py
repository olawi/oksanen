#!/usr/bin/env python
# coding=utf-8

import re
import random
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

celine_messages = [
    "HYI HELEVETTI!!!",
    "jos vielä kerran mainitset sen kanadalaisen lehmän nimen tällä kanavalla, saat ovesta päähän!",
    "eikö se ole vielä menny perille että siitä sumutorvesta ei puhuta?",
    "voi jeesus mikä lehmä sekin on. Olisit sinäkin vaan hiljaa.",
    "no ei nyt helevetti, tarviiko siitä naisesta vielä muistuttaa?",
    ]

CELINE_REGEXP = re.compile(r'c(.{1,2})line dion', re.I)

def setup(self):
    self.repubhandlers.update({CELINE_REGEXP : celine})

def celine(self, e, c):
    """only called if oksanen matches CELINE_REGEXP"""
    nick = nm_to_n(e.source())

    line = e.arguments()[0]
    if random.choice(range(100)) < 50:
        c.privmsg(e.target(), "%s: %s"%(nick,random.choice(celine_messages)))
