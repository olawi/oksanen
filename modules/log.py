#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad
import string

def setup(self):
    self.pubcommands['log'] = log
    log.url = "http://oksanen.servebeer.com/logs"
    log.cron_id = self.cron.add_event({'minute':[1]}, checklogscores, self)
	
def terminate(self):
    """delete cron hook"""
    try:
        self.cron.delete_event(log.cron_id)
    except:
        pass
	
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
		
        if (target == "top"):
            command = """SELECT id, score FROM logs ORDER BY score DESC LIMIT 5;"""
            cursor.execute(command, [] )
            s = "Top logitukset: "
            for row in cursor.fetchall():
                s += "%s (%s), "%(row[0], row[1])
            s += " ja loput netissä."
            c.privmsg(e.target(), s)
        elif (logentry == -1):
            command = """INSERT INTO logs (USER, ENTRY) VALUES (%s, %s); """
        
            # Parametrized input should take care of SQL injection
        
            cursor.execute(command, [nick, target] )
        
            #c.privmsg(e.target(), "Logissa on. Äänestä osoitteessa: "+log.url)
            c.privmsg(e.target(), "Logissa on.")
        else:
            command = """SELECT user, entry, score FROM logs WHERE `ID`=%s;"""

            cursor.execute(command, [ str(logentry) ] )
            for row in cursor.fetchall():
                nscr = str(int(row[2])+1)
                s = u"%s (Loggasi %s, pisteitä %s)"%(row[1], row[0], nscr)
                c.privmsg(e.target(), s)
                command = """UPDATE logs SET score = %s WHERE `ID`=%s"""
                cursor.execute(command, [nscr, str(logentry)])
    else:
        c.privmsg(e.target(), "Interwebsissähän ne. "+log.url)

def checklogscores(self):
    c = self.connection
    cursor = self.db.cursor()
    command = """SELECT id,score,newscore FROM logs WHERE newscore > 0;"""
    cursor.execute(command, [] )
    output = "Pisteitä ovat saaneet logit: "
    count = 0
    for row in cursor.fetchall():
        if count != 0:
            output += ", "
        count = count + 1
        output += "%s (%s+%s)"%(row[0], row[1]-row[2], row[2])
    if count > 0:
        c.privmsg(self.channel, output)
    command = """UPDATE logs SET newscore = 0 WHERE newscore > 0;"""
    cursor.execute(command, [] )
