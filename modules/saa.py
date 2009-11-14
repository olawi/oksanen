#!/usr/bin/env python
# coding=utf-8

import urllib
import htmllib
import formatter

import string
import re
import time
import random

from ircbot import SingleServerIRCBot
from irclib import nm_to_n

saa_url = "http://weather.willab.fi/weather.html"

saa_qrep = [
    "Pit‰‰kˆ se yhten‰‰n olla sit‰ s‰‰t‰kin utelemassa?",
    "En min‰ mik‰‰n liikkuva s‰‰asema ole?",
    "N‰yt‰nkˆ min‰ sinusta Juha Fˆhrilt‰? H‰h?",
    "RAUHOTTUKAAPA!",
    "Mik‰ ihme siin‰ on ettei ihmisi‰ muu kiinnosta?"
    ]

saa_orep = [
    "VTT:n Jari tuumailee ett‰ Oulussa on l‰mmint‰ palttiarallaa",
    "Oulussa",
    "Teknillisen tutkimuskeskuksen ihmeellinen laitteisto kertoo ett‰ Oulusa",
    "Ai m‰‰ vai? Oulussa on",
    "Teknologiakyl‰n katolla ainaki on "
    ]

saa_mrep = [
    "Vitut min‰ siit‰ tied‰n tai v‰lit‰n, mutta Oulussa on",
    "Ai jossain per‰hiki‰ll‰? Mit‰ v‰li‰! Oulussa on",
    "Miss‰? T‰‰ll‰ on ainaki",
    "En kuule tied‰. Mit‰ s‰ siell‰ teet? Oulussa on",
    "Otappa ihan itte kuule selv‰‰. Oulussa on"
    ]

class parser(htmllib.HTMLParser):
    
    def __init__(self, verbose=0):
        self.state = 0
        self.output = []
        self.weatherdata = {}
        self.last_key = ''
        f = formatter.NullFormatter()
        htmllib.HTMLParser.__init__(self, f, verbose)
        
    def start_p(self,attrs):
        for i in attrs:
            if i == ("class","tempnow"):
                self.state = 1;
                self.save_bgn()
                
    def end_p(self):
        if self.state == 1:
            self.output = "%s"%self.save_end()
            self.state = 0;

    def start_th(self,attrs):
        self.save_bgn()
    def end_th(self):
        s = "%s"%self.save_end()
        self.last_key = re.sub('[^\w]','',string.lower(string.join(s.split(),'')))

    def start_td(self,attrs):
        self.save_bgn()
    def end_td(self):
        s = self.save_end()
        self.weatherdata[self.last_key] = "%s"%s

            
def setup(self):
    self.commands['s‰‰'] = saa
    saa.timelast = time.time()
    
def saa(self,e,c):

    saa.timenow = time.time()
    
    line = e.arguments()[0]
    
    fd = urllib.urlopen("%s"%saa_url)
    page = fd.read()
    fd.close
    
    p = parser()
    p.feed(page)
    
    c = self.connection

    if len(line.split()[1:]) < 1:
        messu = random.choice(saa_orep)
    else:
        messu = random.choice(saa_mrep)

    if (saa.timenow - saa.timelast) < 5:
        messu = random.choice(saa_qrep)

    wmessu = "%s, tuntuu ett‰ olis %s. "%(p.output,p.weatherdata['windchill'])

    c.privmsg(e.target(),"%s %s"%(messu,wmessu)) 

    print p.weatherdata

    saa.timelast = saa.timenow
