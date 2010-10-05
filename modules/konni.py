#!/usr/bin/env python
# coding=utf-8

import re
import string
import random
from datetime import datetime, timedelta
import ircutil

from irclib import nm_to_n

DEBUG = 1

konni_re = r'[^!]\bk(ö|ä)nn(i|ä)|korks|tölks|reub|\briipa?s|\bsnuu|\bolus?(en|t+a|el)|\bkal(i|j)+a?|\bbaari'
nukku_re = r'\bnuq|\bnuk(s|k)u|\böitä|\böö+t'
menox_re = r'\blähd?(en|tis|e?tään)|\bmen(in|en|is|nää|o(x|ks))|\bmeen'
total_re = re.compile(r'%s|%s|%s'%(konni_re,nukku_re,menox_re))

def setup(self):

    self.repubhandlers.update({total_re : konni_track})
    self.pubcommands['könniset'] = konni
    self.pubcommands['ryyppyseura'] = konni
    try :
        konni.konniset = self.moduledata['konni']
    except:
        konni.konniset = {}

def terminate(self):
    """save data"""
    self.moduledata['konni'] = konni.konniset
    
def konni_track(self, e, c):
    """seuraa regexpin mukaan"""
    """hox: no need to compile the regexps, they are cached anyway"""

    line = e.arguments()[0]
    
    nick = nm_to_n(e.source())
    now = datetime.now()
    
    konni.konniset[nick] = [now,line]

    """remove old data"""
    ke = konni.konniset.keys()
    for k in ke:
        if (now - konni.konniset[k][0]) > timedelta (hours = 18):
            del konni.konniset[k]

    print "konni updated : %s"%konni.konniset[nick]
    
def konni(self, e, c):
    """ilmoittaa viimeisimmän matchin nickin perusteella"""

    line = e.arguments()[0]
    who = string.join(line.split()[1:], " ")
    
    now = datetime.now()
    nlist = []

    if len(who) < 1:
        if DEBUG :
            print repr(konni.konniset)
        """random line from the past eight hours"""
        for k, v in konni.konniset.iteritems():
            if (now - v[0]) < timedelta (hours = 8):
                """for random, only konni counts"""
                if re.search(konni_re,v[1],re.I):
                    nlist.append(k)
                    
        if len(nlist) > 0:
            who = random.choice(nlist)
        else:
            c.privmsg(e.target(),"eipä kyllä kukaan taida tehdä mitään jännää...")
            return

    if who in konni.konniset:
        data = konni.konniset[who]
        c.privmsg(e.target(),"%02d:%02d <%s> %s"%(data[0].hour,data[0].minute,who,data[1]))
        return
    
    """try to match in all of data[1]"""
    nlist = []
    for k, v in konni.konniset.iteritems():
        if re.search(who,v[1],re.I):
            nlist.append(k)
            
    if len(nlist) > 0:
        who = random.choice(nlist)
        data = konni.konniset[who]
        c.privmsg(e.target(),"%02d:%02d <%s> %s"%(data[0].hour,data[0].minute,who,data[1]))   
    else:
        c.privmsg(e.target(),"enpä hoksaa mitä %s puuhailee."%who)
