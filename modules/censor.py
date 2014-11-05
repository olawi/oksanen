#!/usr/bin/env python
# coding=utf-8

"""
"""

import string
import re

from ircbot import SingleServerIRCBot
from irclib import nm_to_n
from ircutil import run_once

DEBUG = 1

def setup(self):
    """setup called by oksanen on startup"""
    self.privcommands['ignore'] = censor_privcmd

    """this module will not load without SQL"""
    censor.censored = get_censor_list(self)

def get_censor_list(self):
    clist = []
    cursor = self.db.query('SELECT user FROM users WHERE censor = 1')
    for row in cursor.fetchall():
        clist.append(row[0])
    cursor.close()
    return clist

def censor(s):
    """import this to censor in modules"""
    if s in censor.censored:
        x = len(s)
        s = s[0] + s[1:min(2,x-2)] + '*' * max(1,(x-3)) + s[max(2,x-1):x]
    return s
    
def censor_privcmd(self, e, c):
    """privcommand censor"""
    nick = nm_to_n(e.source())
    line = e.arguments()[0]
    args = line.split()

    cur = self.db.query('SELECT censor FROM users WHERE user = %s', [nick])
    result = cur.fetchone()
    cur.close()
    if result:
        state = bool(result[0])
    else:
        return
    
    if len(args) < 2:
        c.privmsg(e.source(), "Tällä hetkellä sinulla on ignore %s" % ('ON' if state else 'OFF'))
        c.privmsg(e.source(), "vaihda tilaa: !ignore ON|OFF")
    else:
        if args[1].lower() in ['on', '1', 'true']:
            state = 1
        elif args[1].lower() in ['off', '0', 'false']:
            state = 0
        else:
            state = not state
            
        cur = self.db.query('UPDATE users SET censor = %s WHERE user = %s', [int(state), nick])
        cur.close()

        censor.censored = get_censor_list(self)

        if state:
            s = "En mainitse enää turhaan sinun, minun kanavalaiseni, nimeä."
        else:
            s = "Avot! Pääset taas mukaan !nussimaan ja !orgioihin!"
            
        c.privmsg(e.source(), s)
        
