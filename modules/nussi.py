#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

import random

nusphrases = [ r"%s: %s olis vailla!", 
               r"%s: körmyyttele vaikka %s:ta",
               r"%s: %s on kuulemma kova panemaan!",
               r"%s: %s on puutteessa" ]

def nussi(self, e, c):
    """ NUSNUS """
    nick = nm_to_n(e.source())
    c = self.connection

    for chname, chobj in self.channels.items():
        if e.target() == chname:
            users = chobj.users()

            fuckee = users[random.randint(0,len(users)-1)]

            c.privmsg(e.target(), nusphrases[random.randint(0, len(nusphrases)-1)]%(nick, fuckee))

nussi.commands = ['nussi']
