#!/usr/bin/env python
# coding=utf-8

import urllib
import htmllib
import formatter

import string

from ircbot import SingleServerIRCBot
from irclib import nm_to_n

saa_url = "http://weather.willab.fi/weather.html"

class parser(htmllib.HTMLParser):
    
    def __init__(self, verbose=0):
        self.state = 0
        self.output = []
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
            
def setup(self):
    self.commands['s��'] = saa

def saa(self,e,c):
    
    line = e.arguments()[0]
    
    fd = urllib.urlopen("%s"%saa_url)
    page = fd.read()
    fd.close
    
    p = parser()
    p.feed(page)
    
    c = self.connection
    
    if len(line.split()[1:]) < 1:
        c.privmsg(e.target(),"VTT:n Jari tuumailee ett� Oulussa on l�mmint� palttiarallaa %s"%p.output)
    else:
        c.privmsg(e.target(),"Vitut min� siit� tied�n tai v�lit�n, mutta Oulussa on %s"%p.output)

    
