#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

import random

nusphrases = [ r"%s: %s olis vailla!", 
               r"%s: paneskele vaikka %s:ta.",
               r"%s: %s on kuulemma kova panemaan!",
               r"%s: %s on puutteessa.",
               r"%s: %s kaipais miurautusta!"]

def setup(self):
    self.pubcommands['nussi'] = nussi

def nussi(self, e, c):
    """ NUSNUS """
    nick = nm_to_n(e.source())

    for chname, chobj in self.channels.items():
        if e.target() == chname:
            users = chobj.users()

            fuckee = users[random.randint(0,len(users)-1)]
            if fuckee == nick:
                c.privmsg(e.target(), "%s: fap fap fap fap fap fap FAP *GNUT*!"%nick)
            else:
                c.privmsg(e.target(), nusphrases[random.randint(0, len(nusphrases)-1)]%(nick, fuckee))
