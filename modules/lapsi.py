#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n

import hashlib
import string

from girlnames import girlnames
from girlnames import dudenames

def setup(self):
    self.commands['lapsi'] = lapsi

def lapsi(self, e, c):
    nick = nm_to_n(e.source())

    line = e.arguments()[0]
    target = string.join(line.split()[1:], " ")

    if (target and len(target) > 0):
        m = hashlib.sha1()
        m.update(nick)
        m.update(target)
        digest = m.digest()
        score = 0
        for i in range(0,len(digest)-1):
            score += ord(digest[i])

        gname = girlnames[score%len(girlnames)]
        bname = dudenames[score%len(dudenames)]

        output = u"kun %s ja %s saavat lapsen, sen nimi tulee olemaan joko %s tai %s"%(nick,target,gname,bname)
        c.privmsg(e.target(),output.encode('ISO-8859-1'))
    
