#!/usr/bin/env python
# coding=utf-8

import re
import string
import urllib
import htmllib
import formatter

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

spotify_url = 'http://spotify.url.fi/'
spotify_uri_re = '(http:\/\/open.spotify.com\/|spotify:)(album|artist|track)([:\/])([a-zA-Z0-9]+)\/?'

class parser(htmllib.HTMLParser):

    def __init__(self, verbose=0):
        self.state = 0
        self.dict = {};
        self.key = ''
        self.value = ''
        f = formatter.NullFormatter()
        htmllib.HTMLParser.__init__(self, f, verbose)

    # <p><span> key </span> value </p>
    def start_p(self,attrs):
        self.state = 1
        self.save_bgn()

    def end_p(self):
        if self.state == 2:
            self.value = self.save_end()
            # what is this mess anyway?
            self.value = re.sub('\[\d+\]\s?$','',self.value)
            self.dict[string.lower("%s"%self.key)] = self.value
            print "%s : %s"%(self.key,self.value)
        self.state = 0
        
    def start_span(self,attrs):
        # if this happens, we're on the wrong page, sir
        if self.state < 1:
            self.save_bgn()
        self.state = 2

    def end_span(self):
        # hox state not reset
        self.key = self.save_end()
        self.save_bgn()

def setup(self):
    self.pubhandlers.append(spotify)

def spotify(self, e, c):
    
    line = e.arguments()[0]
    
    sp_re = re.compile(spotify_uri_re)
    m = re.search(sp_re,line)
    
    if not m:
        return

    fd = urllib.urlopen("%s%s/%s"%(spotify_url,m.group(2),m.group(4)))
    page = fd.read()
    fd.close
    
    p = parser()
    p.feed(page)

    # exceptional cases here
    if re.match('slayer',string.lower(p.dict['artist'])):
        c.privmsg(e.target(), "\,,/(>_<)\,,/ ~!! SLAYER !!~ \,,/(>_<)\,,/")

    if re.search('c(.{1,2})line dion',string.lower(p.dict['artist'])):
        c.privmsg(e.target(), "EI NYT JUMALAUTA TUOMMOSTA KUUNNELLA! SEIS!")
        
    messu = ""
   
    if 'artist' in p.dict :
        messu += "%s"%p.dict['artist']
        
    if 'album' in p.dict :
        messu += " / %s"%p.dict['album']

    if 'track' in p.dict :
        messu += " / %s"%p.dict['track']

    if 'year' in p.dict :
        messu += " (%s)"%p.dict['year']

    c.privmsg(e.target(),"%s"%messu)
