#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2

import string
import re

from ircbot import SingleServerIRCBot
from irclib import nm_to_n
import ircutil

from matka_aliases import matka_aliases

tie_url = 'http://alk.tiehallinto.fi/cgi-bin/pq9.cgi'
tie_querystring = 'MISTÄ=%s&MIHIN=%s&NOPEUS=80'

def setup(self):
    self.commands['matka'] = matka

def matka(self,e,c):

    line = e.arguments()[0]

    params = line.split()[1:]

    if len(params) != 2:
        c.privmsg(e.target(),"käytetään: !matka lähtöpaikka määränpää")
        return
    else:
        bgn = string.capitalize(params[0])
        end = string.capitalize(params[1])

    bgn = re.sub('^ä','Ä',bgn)
    bgn = re.sub('^ö','Ö',bgn)
    bgn = re.sub('^å','Å',bgn)
    end = re.sub('^ä','Ä',end)
    end = re.sub('^ö','Ö',end)
    end = re.sub('^å','Å',end)

    if bgn in matka_aliases:
        bgn = matka_aliases[bgn]
    if end in matka_aliases:
        end = matka_aliases[end]
        
    if bgn == end : c.privmsg(e.target(),"Yritätkö muka olla hauska?")

    query = ircutil.recode(tie_querystring%(bgn,end),'latin-1')

    req = urllib2.Request(tie_url,query)
    resp = urllib2.urlopen(req)
    page = resp.read()

    m = re.search('matka on (\d+)',page)

    dist = m.group(1)

    if dist != '0':
        c.privmsg(e.target(),"välimatka %s - %s on %s km."%(bgn,end,dist))
    else:
        c.privmsg(e.target(),"Sori, tiehallinto ei löydä tuollaisia paikkoja.")

