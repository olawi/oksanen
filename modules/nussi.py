#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

from censor import censor

import random

nusphrases = [ r"%s, %s olis vailla!", 
               r"%s, irstailu alkakoon, kumppaninasi %s.",
               r"%s, %s on kuulemma kova panemaan!",
               r"%s, %s on puutteessa.",
               r"%s, mietippä nyt ihan itse että kenen kanssa tahtoisit? %s ei kyllä anna sulle.",
               r"%s, %s kaipais miurautusta!",
               r"%s, %s tahtoisi kosketella sinua intiimialueilta!",
               r"%s, %s saattaisi olla hellän rakastelun tarpeessa.",
               r"%s, %s tarvitsisi nyt rajua panoa!",
               r"%s, %s haluaisi nyt jotain pyllyynsä ja äkkiä!",
               r"%s, %s kuulemma pitää rajusta anaaliseksistä!",
               r"%s, %s himoitsee sinua salaa, mutta ei uskalla kertoa sitä.",
               r"%s, kaikkihan sen jo tietävät että %s on villeimpien fantasioidesi kohde!",
               r"%s ja %s ne yhteen soppii, huomenna PANNAAN.",
               r"kun %s ja %s rakastelevat, niin jumalatkin vaikenee.",
               r"on hankala kuvitella irstaampaa paria kuin %s ja %s.",
               r"%s, valitettavasti %s tuntee sinua kohtaan vain platonista rakkautta.",
               r"mitähän siitäkin tulisi jos %s ja %s nussisivat? Ei ainakaan kauniita lapsia.",
               r"%s ja %s, yrittäkää nyt pysyä housuissane ainakin kämpille asti.",
               r"%s, unohdappa nyt kerrankin estosi, sillä %s himoitsee sinua.",
               r"%s, jos voisin antaa pienen vinkin, %s on kiimainen tapaus.",
               r"%s, %s pitää sitomisleikeistä.",
               r"siitä on siveys kaukana kun %s ja %s hässivät.",
               r"%s, %s otti viime kertanne videolle ja pisti sen nettiin!",
               r"%s, %s onkin ollut pitkään märkien uniesi kohde, että toimeksi vaan!",
               r"kun %s ja %s nussivat niin paska haisee ja balalaikka soi!"]

runkphrases = [ r"%s: fap fap fap fap fap fap FAP *GNUT*!",
                r"Ei sinun kuule %s auta nyt kuin runkata, et löydä kaveria.",
                r"Meni kuule sinulla %s runkkaus_hommiksi nyt!"
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
