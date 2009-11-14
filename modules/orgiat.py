#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

import random

threesome = [ r"%s ja %s pistää %s:n vartaaseen", 
              r"%s tunkee straponia %s:n hanuriin ja %s heittää naamalle",
              r"%s, %s ja %s ei saa nyt mitään aikaan",
              r"%s, %s ja %s nussiivat",
              r"%s panee eestä ja %s pakee takaa, %s könnissä paikallaan makaa!" ]

fourway = [ r"On %s ottanut prestoja, ei tunne estoja, %s katsoo ja runkkaa kun %s ja %s heiluttaa punkkaa!",
            r"Luostarissa rytisee kun munkki %s saapuu paikalle moikkaamaan nunnia %s, %s ja %s" ]


def setup(self):
    self.commands['nussi'] = nussi

def nussi(self, e, c):
    """ NUSNUS """
    nick = nm_to_n(e.source())

    for chname, chobj in self.channels.items():
        if e.target() == chname:
            users = chobj.users()

            if random.randint(0,1) == 0:
                    c.privmsg(e.target(), threesome%(random.choice(users),random.choice(users),random.choice(users))
            else:
                    c.privmsg(e.target(), fourway%(random.choice(users),random.choice(users),random.choice(users),random.choice(users))
                
