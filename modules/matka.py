#!/usr/bin/env python
# coding=utf-8

import urllib
import urllib2

import string
import re

from ircbot import SingleServerIRCBot
from irclib import nm_to_n

tie_url = 'http://alk.tiehallinto.fi/cgi-bin/pq9.cgi'
tie_querystring = 'MIST�=%s&MIHIN=%s&NOPEUS=80'

def setup(self):
    self.commands['matka'] = matka

def matka(self,e,c):

    line = e.arguments()[0]
    
    m = re.search('([\w������]+)\-([\w������]+)',line)

    if not m:
        c.privmsg(e.target(),"k�ytet��n: !matka l�ht�paikka-m��r�np��")
    else:
        bgn = string.capitalize(m.group(1))
        end = string.capitalize(m.group(2))

    bgn = re.sub('^�','�',bgn)
    bgn = re.sub('^�','�',bgn)
    bgn = re.sub('^�','�',bgn)
    end = re.sub('^�','�',end)
    end = re.sub('^�','�',end)
    end = re.sub('^�','�',end)

    if bgn == end : c.privmsg(e.target(),"Yrit�tk� muka olla hauska?")

    req = urllib2.Request(tie_url,tie_querystring%(bgn,end))
    resp = urllib2.urlopen(req)
    page = resp.read()

    m = re.search('matka on (\d+)',page)

    dist = m.group(1)

    if dist != '0':
        c.privmsg(e.target(),"V�limatka %s-%s on %s km."%(bgn,end,dist))
    else:
        c.privmsg(e.target(),"Sori, nyt ei l�ytynyt tuollaisia paikkakuntia. Liek� olemassakaan..")

