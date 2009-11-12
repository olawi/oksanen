#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

import random

babble = [ r"%s: Ei tänään, ei ehkä koskaan",
           r"%s: Vielä on 6 viikkoa porttikieltoa jäljellä",
           r"%s: Kerroppa omin sanoin miksi olet siinä etkä tuolla jonon perällä?",
           r"%s: Hehe mikä variksenpelätin se sinäki olet",
           r"%s: Narikkamaksu on pakollinen",
           r"%s: Ei omia juomia. Ulos.",
           r"%s: Siellä sisällä on vain jotain saatanan lökäpöksyjä tänään. Ei kannata tulla." ]

def setup(self):
    self.pubhandlers.append(do_babble)

def do_babble(self, e, c):
    nick = nm_to_n(e.source())

    line = e.arguments()[0]
    if len(line) > 1 and line.lower().find(self.nickname.lower()) !=-1:
        c.privmsg(e.target(), babble[random.randint(0, len(babble)-1)]%nick)
