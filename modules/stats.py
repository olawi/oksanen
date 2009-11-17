#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad
import string
from oksanen import hasSql
from time import strftime, localtime

def setup(self):
    self.pubhandlers.append(stats)
    stats.nicks = []

def stats(self, e, c):
    if hasSql:
        cursor = self.db.cursor()
        if stats.nicks == []:
            cursor.execute("""SELECT user FROM user""")
            for row in cursor.fetchall():
                stats.nicks.append(row[0])
            
        #snick = re.sub('[^a-zA-Z0-9]','',nm_to_n(e.source()))
        nick = nm_to_n(e.source())

        if not nick in stats.nicks:
            cursor.execute("INSERT INTO user (user) VALUES(%s);", [nick])
            stats.nicks.append(nick)
        
        line = e.arguments()[0]
        wordcount = len(line.split())
        currenthour = int(strftime("%H",localtime()))
        cursor.execute("UPDATE user SET said = said + 1, words = words + %s WHERE user = %s;", [wordcount,nick])
        cursor.execute("UPDATE hourstats SET said = said + 1, words = words + %s WHERE hour = %s;", [wordcount,currenthour])