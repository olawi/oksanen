#!/usr/bin/env python
# coding=utf-8

from lxml import html
import requests

from irclib import nm_to_n

kaanna_usage = "käytetään esim. että !käännä englanti-suomi fuck";

kaanna_url = "http://fi.bab.la/sanakirja"

def setup(self):
    self.pubcommands['käännä'] = kaanna
    self.pubcommands['kaanna'] = kaanna

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

    query = "%s-%s/%s"%(lan1,lan2,word)
    
    page = requests.get('%s/%s' % (kaanna_url,query))
    tree = html.fromstring(page.content)
    results = tree.xpath('//*[@id="main"]/div[1]/div[1]/div[1]/div[1]/p[1]/a/text()')
    
    reply = ', '.join(results)
    
    c = self.connection

    if len(results) > 0:
        c.privmsg(e.target(), "%s-%s käännös sanalle '%s': %s" % (lan1, lan2, word, reply))
    else:
        c.privmsg(e.target(), "Ei löydy käännöstä %s-%s sanalle '%s'." % (lan1, lan2, word))
    


