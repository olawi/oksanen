#!/usr/bin/env python
# coding=utf-8

import re
import string
import random
from datetime import datetime, timedelta
import ircutil

from irclib import nm_to_n

konni_re = r'korks|tölks|[^!]\bkönni|\bsnuu|\bolus?(en|tta|el)|kal(i|j)+a?(a|lle|n)|\bbaari|\bnuq|\bnukku|\böitä|\blähd?[en|tis]|\bmen?e+n'

def setup(self):
    self.pubhandlers.append(konni_track)
    self.commands['könniset'] = konni
    konni.konniset = {}

def konni_track(self,e,c):
    """seuraa regexpin mukaan"""

    line = ircutil.recode(e.arguments()[0])
    m = re.search(konni_re,line,re.I|re.U)
    
    if not m:
        return
 
    nick = nm_to_n(e.source())
    now = datetime.now()
    
    konni.konniset[nick] = [now,line]

    """liian vanhat pois"""
    ke = konni.konniset.keys()
    for k in ke:
        if (now - konni.konniset[k][0]) > timedelta (hours = 8):
            del konni.konniset[k]

    print konni.konniset
                   
def konni(self,e,c):
    """ilmoittaa viimeisimmän matchin nickin perusteella"""

    line = e.arguments()[0]
    who = string.join(line.split()[1:], " ")

    now = datetime.now()

    if len(who) < 1:
        nl = []
        """random line from the past four hours"""
        for k, v in konni.konniset.iteritems():
            print now
            print v[0]
            if (now - v[0]) < timedelta (hours = 3):
                nl.append(k)
                print nl
        if len(nl) > 0:
            who = random.choice(nl)
        else:
            c.privmsg(e.target(),"eipä kyllä kukaan taida tehdä mitään jännää...")
            return

    if who in konni.konniset:
        data = konni.konniset[who]
        c.privmsg(e.target(),"%02d:%02d <%s> %s"%(data[0].hour,data[0].minute,who,data[1]))
    else:
        c.privmsg(e.target(),"eipä ole %s:ta kuulunut viime aikoina"%who)
