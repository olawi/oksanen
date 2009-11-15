#!/usr/bin/env python
# coding=utf-8

import urllib
import urllib2

import string
import re

from ircbot import SingleServerIRCBot
from irclib import nm_to_n

tie_url = 'http://alk.tiehallinto.fi/cgi-bin/pq9.cgi'
tie_querystring = 'MISTÄ=%s&MIHIN=%s&NOPEUS=80'

def setup(self):
    self.commands['matka'] = matka

def matka(self,e,c):

    line = e.arguments()[0]
    
    m = re.search('([\wöäåÖÄÅ]+)\-([\wöäåÖÄÅ]+)',line)

    if not m:
        c.privmsg(e.target(),"käytetään: !matka lähtöpaikka-määränpää")
    else:
        bgn = string.capitalize(m.group(1))
        end = string.capitalize(m.group(2))

    bgn = re.sub('^ö','Ö',bgn)
    bgn = re.sub('^ä','Ä',bgn)
    bgn = re.sub('^å','Ä',bgn)
    end = re.sub('^ö','Ö',end)
    end = re.sub('^ä','Ä',end)
    end = re.sub('^å','Ä',end)

    if bgn == end : c.privmsg(e.target(),"Yritätkö muka olla hauska?")

    req = urllib2.Request(tie_url,tie_querystring%(bgn,end))
    resp = urllib2.urlopen(req)
    page = resp.read()

    m = re.search('matka on (\d+)',page)

    dist = m.group(1)

    if dist != '0':
        c.privmsg(e.target(),"Välimatka %s-%s on %s km."%(bgn,end,dist))
    else:
        c.privmsg(e.target(),"Sori, nyt ei löytynyt tuollaisia paikkakuntia. Liekö olemassakaan..")

