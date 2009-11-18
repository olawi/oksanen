#!/usr/bin/env python
# coding=utf-8

import re
import string
import time
import datetime
import ircutil

from irclib import nm_to_n

konni_re = r'korks|tölks|\bsnuu|\bolus?(en|tta|el)|kal(i|j)+a?(a|lle|n)|\bbaari|\bnuq|\bnukku|\böitä|\blähd?en|\bmen?en'

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
    t = datetime.datetime.now()
    
    konni.konniset[nick] = [t,line]

    """remove entries > 8h"""
    ke = konni.konniset.keys()
    for k in ke:
        if (t.day-konni.konniset[k][0].day) > 1:
            del konni.konniset[k]

    print konni.konniset
                   
def konni(self,e,c):
    """ilmoittaa viimeisimmän matchin nickin perusteella"""

    line = e.arguments()[0]
    who = string.join(line.split()[1:], " ")

    if who in konni.konniset:
        data = konni.konniset[who]
        c.privmsg(e.target(),"%02d:%02d <%s> %s"%(data[0].hour,data[0].minute,who,data[1]))
    else:
        c.privmsg(e.target(),"eipä ole %s:ta kuulunut viime aikoina"%who)
