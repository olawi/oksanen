#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

import re
import random
from haddock import kiroukset

babble = [ r"%s, ei tänään, ei ehkä koskaan",
           r"%s: Vielä on 6 viikkoa porttikieltoa jäljellä",
           r"%s: Kerroppa omin sanoin miksi olet siinä etkä tuolla jonon perällä?",
           r"%s, hehe mikä variksenpelätin se sinäki olet",
           r"%s: Narikkamaksu on pakollinen",
           r"%s: Ei omia juomia. Ulos.",
           r"%s: Siellä sisällä on vain jotain saatanan lökäpöksyjä tänään. Ei kannata tulla." ]

def setup(self):
    s = r"\b%s" % self.nickname
    regex = re.compile(s, re.I)
    self.repubhandlers.update({regex : do_babble})

def do_babble(self, e, c):
    nick = nm_to_n(e.source())

    if random.choice(range(100)) < 75:
        if random.choice(range(100)) < 50:
            c.privmsg(e.target(), babble[random.randint(0, len(babble)-1)]%nick)
        else:
            k1 = random.choice(kiroukset)
            k2 = random.choice(kiroukset).capitalize()
            c.privmsg(e.target(), "%s, senkin %s! %s!" % (nick, k1, k2))
