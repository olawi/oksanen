#!/usr/bin/env python
# coding=utf-8

import urllib
import htmllib

import formatter
import string
import re
import sys

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

kaanna_kielet = [ 
    "suomi",
    "englanti",
    "ruotsi",
    "viro",
    "ranska",
    "bulgaria",
    "katalaani",
    "tanska",
    "saksa",
    "kreikka",
    "espanja",
    "unkari",
    "islanti",
    "italia",
    "japani",
    "liettua",
    "latvia",
    "hollanti",
    "norja",
    "puola",
    "portugali",
    "romani",
    "slovakki",
    "somali",
    "turkki",
    "kiina"
    ]

kaanna_usage = "käytetään esim. että !käännä englanti-suomi dictionary ";

kaanna_url = "http://ilmainensanakirja.fi/sanakirja_"

class parser(htmllib.HTMLParser):

    def __init__(self, verbose=0):
        self.state = 0
        self.output = "";
        f = formatter.NullFormatter()
        htmllib.HTMLParser.__init__(self, f, verbose)

    def start_div(self,attrs):
        for i in attrs:
            if i==("id", "contentText"):
                self.state = 1
                return

    def end_div(self):
        self.state = 0

    def start_table(self,attrs):
        for i in attrs:
            if i==("id", "searchResultsTable"):
                self.state = 2
                return

    def end_table(self):
        self.state = 0

    def start_h2(self,attrs):
        if self.state == 1:
            self.save_bgn()

    def end_h2(self):
        if self.state == 1:
            self.output += "%s: "%self.save_end()

    def start_a(self,attrs):
        if self.state == 2:
            self.save_bgn()

    def end_a(self):
        if self.state == 2:
            self.output += "%s, "%self.save_end()

def setup(self):
    self.commands['käännä'] = kaanna

def kaanna(self,e,c):

    line = e.arguments()[0]

    args = line.split()[1:]
    if len(args) > 2:
        c.privmsg(e.target(),"%s, %s"%(nm_to_n(e.source()),kaanna_usage))
        return
    
    elif len(args) == 1:
        (lan1,lan2) = ('englanti','suomi')
        query = args[0]

    else:
        try:
            (lan1,lan2) = args[0].split('-')
            query = args[1]
            print "%s %s %s"%(lan1,lan2,query)
        except:
            c.privmsg(e.target(),"%s, %s"%(nm_to_n(e.source()),kaanna_usage))
            return

    print "%s %s %s"%(lan1,lan2,query)
    if not (lan1 in kaanna_kielet and lan2 in kaanna_kielet):
        c.privmsg(e.target(),"%s, sori vaan mutta en minä nyt ihan kaikkia kieliä osaa!"%nm_to_n(e.source()))
        return

    # Merkistöt kuosiin urlia varten
    query = unicode(query,'ISO-8859-1','ignore')
    query = query.encode('UTF-8')

    fd = urllib.urlopen("%s%s-%s/%s"%(kaanna_url,lan1,lan2,query))
    page = fd.read()
    fd.close

    p = parser()
    p.feed(page)

    c = self.connection
    answart = re.sub(",\s?$",".",p.output)
    c.privmsg(e.target(), "%s"%answart)


