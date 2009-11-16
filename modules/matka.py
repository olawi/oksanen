#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2

import string
import re

from ircbot import SingleServerIRCBot
from irclib import nm_to_n

from matka_aliases import matka_aliases

tie_url = 'http://alk.tiehallinto.fi/cgi-bin/pq9.cgi'
tie_querystring = 'MIST�=%s&MIHIN=%s&NOPEUS=80'

def setup(self):
    self.commands['matka'] = matka

def matka(self,e,c):

    line = e.arguments()[0]

    params = line.split()[1:]

    if len(params) != 2:
        c.privmsg(e.target(),"k�ytet��n: !matka l�ht�paikka m��r�np��")
        return
    else:
        bgn = string.capitalize(params[0])
        end = string.capitalize(params[1])

    bgn = re.sub('^�','�',bgn)
    bgn = re.sub('^�','�',bgn)
    bgn = re.sub('^�','�',bgn)
    end = re.sub('^�','�',end)
    end = re.sub('^�','�',end)
    end = re.sub('^�','�',end)

    if bgn in matka_aliases:
        bgn = matka_aliases[bgn]
    if end in matka_aliases:
        end = matka_aliases[end]
        
    if bgn == end : c.privmsg(e.target(),"Yrit�tk� muka olla hauska?")

    req = urllib2.Request(tie_url,tie_querystring%(bgn,end))
    resp = urllib2.urlopen(req)
    page = resp.read()

    m = re.search('matka on (\d+)',page)

    dist = m.group(1)

    if dist != '0':
        c.privmsg(e.target(),"v�limatka %s - %s on %s km."%(bgn,end,dist))
    else:
        c.privmsg(e.target(),"Sori, nyt ei l�ytynyt tuollaisia paikkakuntia. Liek� olemassakaan..")

