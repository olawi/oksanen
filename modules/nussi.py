#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

from censor import censor

import random
import time
import math

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
               r"%s ja %s, yrittäkää nyt pysyä housuissanne ainakin kämpille asti.",
               r"%s, unohdappa nyt kerrankin estosi, sillä %s himoitsee sinua.",
               r"%s, jos voisin antaa pienen vinkin, %s on kiimainen tapaus.",
               r"%s, %s pitää sitomisleikeistä.",
               r"siitä on siveys kaukana kun %s ja %s hässivät.",
               r"%s, %s otti viime kertanne videolle ja pisti sen nettiin!",
               r"%s, %s onkin ollut pitkään märkien uniesi kohde, että toimeksi vaan!",
               r"%s ja %s, olette riettaudessanne kuin märkä lapanen.",
               r"kun %s ja %s suunnistavat toistensa sukuelimille, taivaat repeävät!",
               r"%s ja %s, edessänne on varsinainen yllätysten yö.",
               r"%s ja %s, eritteenne vuotakoon valtoimenaan kun käytte rakkauden työhön.",
               r"se on hellurei ja hellät tunteet kun %s ja %s rapastelevat.",
               r"kumpikohan sitoo kumman kun %s ja %s käyvät raakoihin rakkauden toimiin?",
               r"oletkos %s ajatellut että %s tahtoisi tulla syliisi?",
               r"siinä on paikat hellinä kun %s ja %s käyvät toimeen.",
               r"rakkaus on hellää, rakkaus on rajua, mutta kun %s ja %s nussivat niin siinä jo paikat hajuaa!",
               r"%s ja %s, jos teidän tuoksuanne voisi purkittaa niin se olisi jo poliisiasia.",
               r"%s ja %s, teidän lihallisuutenne on suorastaan rikollista!",
               r"jo muinaiset roomalaiset tiesivät että jonakin päivänä %s ja %s tulevat hässimään.",
               r"%s, we are the %s. You will be hässimiläted.",
               r"%s ja %s, olette kuin märät jänikset rakkautenne äärellä.",
               r"on pari asiaa joita ei soisi lapsien näkevän. Niistä hurjimpana kun %s ja %s käyvät toisiinsa kiinni.",
               r"nussi ketä haluat %s, mutta varo ettei %s saa tietää!",
               r"oletkos %s ajatellut että %s on sinusta kauhean mustasukkainen jos tuolla tavalla nussit ympäriinsä?",
               r"%s ja %s, rakkautenne on kuin suuri Jangtse-joki. Ei yhtä valtava, mutta haisee samalle.",
               r"se on nyt vaan sillä tavalla että %s ja %s menevät nussimaan ja tästä ei keskustella sen enempää.",
               r"%s, luulet että %s himoitsee sinua ja... olet oikeassa!",
               r"Kuuleppas %s. Haluat jonkun nimen? Sanon sulle että %s.",
               r"kun %s ja %s nussivat niin paska haisee ja balalaikka soi!"]

runkphrases = [ r"%s: fap fap fap fap fap fap FAP *GNUT*!",
                r"Ei sinun kuule %s auta nyt kuin runkata, et löydä kaveria.",
                r"Meni kuule sinulla %s runkkaus_hommiksi nyt!"
                ]

warnphrases = [ r"%s, rauhotuppa nyt vähäsen.",
                r"%s, nyt annat kyllä muittenkin !nussia.",
                r"%s, etkö saanut jo tarpeeksi? Nyt taisi olla sinun !nussimiset siinä joksikin aikaa.",
                r"%s, näytänkö minä sinusta joltain parittajalta? Pidähän taukoa.",
                r"%s, jos ei ehdotukset kelpaa niin yritähän itse tehdä omat päätöksesi. Nyt riitti hetkeksi."
                ]

"""tn_time is the time diff after which the prob of getting banned is zero"""
nussi_tn_time = 2*60
nussi_ban_time = 5*60

def setup(self):
    self.pubcommands['nussi'] = nussi
    nussi.warned = {}
    nussi.last = {}

def nussi(self, e, c):
    """ NUSNUS """
    nick = nm_to_n(e.source())

    if nick in nussi.last :
        """check if banned"""
        if nussi.warned[nick] == 1 and (time.time() - nussi.last[nick]) < nussi_ban_time :
            return
        else :
            nussi.warned[nick] = 0

        tdiff = time.time() - nussi.last[nick]
        nussi.last[nick] = time.time()
        """!nussi too soon and you might get banned"""
        ban_prob = 100*(1 - math.pow(tdiff/nussi_tn_time,0.5))
        print ban_prob
        if random.choice(range(100)) < ban_prob:
            if not nick in nussi.warned or nussi.warned[nick] == 0 :
                c.privmsg(e.target(), random.choice(warnphrases) % nick)
                nussi.warned[nick] = 1
                return
            else : 
                return
    else :
        nussi.last[nick] = time.time()
        nussi.warned[nick] = 0

    for chname, chobj in self.channels.items():
        if e.target().lower() == chname.lower():
            users = chobj.users()

            fuckee = random.choice(users)
            if fuckee == nick:
                c.privmsg(e.target(), random.choice(runkphrases) % nick)
            else:
                fuckee = censor(fuckee)
                c.privmsg(e.target(), random.choice(nusphrases) % (nick, fuckee))
