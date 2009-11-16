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
        # Magic
        logentry = -1
        try:
            logentry = int(target)
            
        except Exception, ex:
            # Was not a number, go on
            pass

        cursor = self.db.cursor()

        if logentry == -1:
            command = """INSERT INTO log (USER, ENTRY) VALUES (%s, %s); """
        
            # Parametrized input should take care of SQL injection
        
            cursor.execute(command, [nick, target] )
        
            c.privmsg(e.target(), "Logissa on.")
        else:
            command = """SELECT USER, ENTRY FROM log WHERE `ID`=%s;"""

            cursor.execute(command, [ str(logentry) ] )
            for row in cursor.fetchall():
                s = "%s (Loggasi %s)"%(row[1], row[0])
                c.privmsg(e.target(), s.encode('latin-1'))
    else:
        c.privmsg(e.target(), "Interwebsissähän ne. http://rosvosektori.wipsl.com/numero/")

                
