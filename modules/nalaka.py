#!/usr/bin/env python
# coding=utf-8

import urllib
import HTMLParser

import string
import re
import random

from ircbot import SingleServerIRCBot
from irclib import nm_to_n

kaenkky_url = 'http://www.kaenkky.com/?'
query_random = "p=k&id=-1"
query_kaupunginosa = "p=kht&nimi=&kaupunginosa=%s&rating=&elossa=2&submit=+Hae+ruokapaikat+"
query_keyword = "p=kht&nimi=%s&kaupunginosa=&rating=&elossa=1&submit=+Hae+ruokapaikat+"

kaupunginosat = [ "höyhtyä","kaakkuri","kaijonharju","kastelli","kaukovainio","keskusta","korvensuora","koskela","kuivasjärvi","limingantulli","maikkula","myllyoja","nuottasaari","pateniemi","puolivälinkangas","rajakylä","toppila","tuira","välivainio" ]

class kaenkky_parser(HTMLParser.HTMLParser):
    def __init__(self, verbose=0):
        self.output = ''
        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self,tag,attrs):
        if tag == 'meta':
            if ('name','description') in attrs:
                for a in attrs:
                    if a[0] == 'content':
                        self.output = string.join(string.split(a[1]),' ')
                        self.output = self.output.split('/')[-1]
                        self.output = string.join(self.output.split(),' ')
                
def setup(self):
    self.commands['näläkä'] = nalaka

def get_kaenkky(self,url,params=None):

    fd = urllib.urlopen(url,params)
    page = fd.read()
    fd.close()
    
    p = kaenkky_parser()
    p.feed(page)
    print page
    m = re.search('(Avoinna viel.*?)\<',page)

    if m: p.output += " - %s"%m.group(1)
    
    return p.output
    
def nalaka(self,e,c):

    line = e.arguments()[0]
    c = self.connection
    
    queryparams = { 'p':'k', 'id':-1 }

    kama = get_kaenkky(self,kaenkky_url,queryparams)


# testing
#queryparams = { 'p':'k', 'id':-1 }
#print get_kaenkky(None,"%sp=kh"%(kaenkky_url))
