#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

from censor import censor

import random

nusphrases = [ r"%s: %s olis vailla!", 
               r"%s: nussimiskaverisi olkoon %s.",
               r"%s: %s on kuulemma kova panemaan!",
               r"%s: %s on puutteessa.",
               r"No mietippä nyt %s ihan itse että kenen kanssa tahtoisit? %s ei kyllä anna sulle.",
               r"%s: %s kaipais miurautusta!"]

runkphrases = [ r"%s: fap fap fap fap fap fap FAP *GNUT*!",
                r"Ei sinun kuule %s auta nyt kuin runkata, et löydä kaveria.",
                r"Meni kuule sinulla runkkaus _hommiksi nyt!"
                ]

def setup(self):
    self.pubcommands['nussi'] = nussi

def nussi(self, e, c):
    """ NUSNUS """
    nick = nm_to_n(e.source())

    for chname, chobj in self.channels.items():
        if e.target().lower() == chname.lower():
            users = chobj.users()

            fuckee = random.choice(users)
            if fuckee == nick:
                c.privmsg(e.target(), random.choice(runkphrases) % nick)
            else:
                fuckee = censor(fuckee)
                c.privmsg(e.target(), random.choice(nusphrases) % (nick, fuckee))
