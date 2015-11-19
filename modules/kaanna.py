#!/usr/bin/env python
# coding=utf-8

import urllib
import htmllib

import formatter
import re

from irclib import nm_to_n

kaanna_kielet = [ 
    "suomi",
    "englanti",
    "ruotsi",
    "viro",
    "venäjä",
    "ranska",
    "bulgaria",
    "katalaani",
    "tsekki",
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
    # ei toimi -> "slovakki",
    "somali",
    "turkki",
    "kiina"
    ]

kaanna_notsupported = ["venäjä", "bulgaria", "kreikka", "japani", "kiina"] 

kaanna_usage = "käytetään esim. että !käännä englanti-suomi fuck";

kaanna_url = "http://ilmainensanakirja.fi/"

class Parser(htmllib.HTMLParser):

    def __init__(self, verbose=0):
        self.state = 0
        self.output = "";
        f = formatter.NullFormatter()
        htmllib.HTMLParser.__init__(self, f, verbose)

    def start_div(self,attrs):
        if ("id", "cont") in attrs:
            self.state = 1
            return
        if ("class","word") in attrs:
            self.state = 2
            return

    def end_div(self):
        self.state = 0

    def start_h3(self,attrs):
        if self.state == 1:
            self.save_bgn()

    def end_h3(self):
        if self.state == 1:
            text = self.save_end()
            if len(text) > 0:
                self.output += "%s: "%text

    def start_a(self,attrs):
        if ("class", "morex") in attrs:
            self.state = 3
        if self.state == 2:
            self.save_bgn()

    def end_a(self):
        if self.state == 2:
            self.output += "%s, "%self.save_end()
        if self.state == 3:
            self.state = 2
            
    def start_small(self, attrs):
        if self.state == 2:
            self.output += "%s (" % self.save_end()
            self.save_bgn()
            
    def end_small(self):
        if self.state == 2:
            self.output += "%s)" % self.save_end()
            self.save_bgn()

def setup(self):
    self.pubcommands['käännä'] = kaanna
    self.pubcommands['kaanna'] = kaanna

def get_result(query):
    """ Fetches result using the parser, query must be preformatted:
        fromlang-tolang/word """
    fd = urllib.urlopen("%s%s"%(kaanna_url,query))
    page = fd.read()
    fd.close

    p = Parser()
    p.feed(page)

    ans = re.sub("\s*?&.*?;","",p.output)
    ans = re.sub("\,\s*$",".",ans)
    
    return ans

def kaanna(self,e,c):

    line = e.arguments()[0]

    args = line.split()[1:]
    if len(args) > 2:
        c.privmsg(e.target(),"%s, %s"%(nm_to_n(e.source()),kaanna_usage))
        return
    
    elif len(args) == 1:
        (lan1,lan2) = ('englanti','suomi')
        word = args[0]

    else:
        try:
            (lan1,lan2) = args[0].split('-')
            word = args[1]
            print "%s %s %s"%(lan1,lan2,word)
        except:
            c.privmsg(e.target(),"%s, %s"%(nm_to_n(e.source()),kaanna_usage))
            return

    if not (lan1 in kaanna_kielet and lan2 in kaanna_kielet) :
        c.privmsg(e.target(),"%s, sori vaan mutta en minä nyt ihan kaikkia kieliä osaa!"%nm_to_n(e.source()))
        return
    
    if (lan2 in kaanna_notsupported) :
        c.privmsg(e.target(),"%s, okei - toivottavasti sulla on utf-8 päällä:"%nm_to_n(e.source()))
                  
    query = "%s-%s/%s"%(lan1,lan2,word)
    
    answart = get_result(query)

    if len(answart) < 1 and len(args) < 2:
        """ Try the other way around in case of stupid user error """
        query = "%s-%s/%s"%(lan2,lan1,word)
        answart = get_result(query)

    c = self.connection

    if len(answart) > 0:
        c.privmsg(e.target(), answart)
    else:
        c.privmsg(e.target(), "Ei löydy käännöstä %s-%s sanalle '%s'." % (lan1, lan2, word))
    


