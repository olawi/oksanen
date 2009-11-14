#!/usr/bin/env python
# coding=utf-8

import random
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

celine_messages = [
    "HYI HELEVETTI!!!",
    "jos viel� kerran mainitset sen kanadalaisen lehm�n nimen t�ll� kanavalla, saat ovesta p��h�n!",
    "eik� se ole viel� menny perille ett� siit� sumutorvesta ei puhuta?",
    "voi jeesus mik� lehm� sekin on. Olisit sin�kin vaan hiljaa.",
    "selinen mik�..? EI NYT SAATANA!"
    ]

def setup(self):
    self.pubhandlers.append(celine)

def celine(self, e, c):
    nick = nm_to_n(e.source())

    line = e.arguments()[0]

    if line.lower().find('celine dion') != -1:
        c.privmsg(e.target(), "%s: %s"%(nick,random.choice(celine_messages)))
