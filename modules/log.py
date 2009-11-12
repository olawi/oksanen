#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad
import string

def setup(self):
    self.commands['log'] = log

def log(self, e, c):
    nick = nm_to_n(e.source())

    line = e.arguments()[0]
    target = string.join(line.split(" ")[1:], " ")
    if (target and len(target) > 0):
        cursor = self.db.cursor()
        
        command = """INSERT INTO log (USER, ENTRY) VALUES (%s, %s); """

        # Parametrized input should take care of SQL injection

        cursor.execute(command, [nick, target] )

        c.privmsg(e.target(), "Little Bobby tables <3")
