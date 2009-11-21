#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad
import string
from oksanen import hasSql
from time import strftime, localtime

def load_nick_table(cursor):
    cursor.execute("SELECT user FROM user")
    for row in cursor.fetchall():
        stats.nicks.append(row[0])

def setup(self):
    self.pubhandlers.append(stats)
    self.joinhandlers.append(stats_join)
    self.joinhandlers.append(stats_part)
    stats.nicks = []

def stats_join(self,e,c):
    if hasSql:
        cursor = self.db.cursor()
        if stats.nicks == []:
            load_nick_table(cursor)

        nick = nm_to_n(e.source())

        if not nick in stats.nicks:
            cursor.execute("INSERT INTO user (user) VALUES(%s);", [nick])
            stats.nicks.append(nick)

        cursor.execute("UPDATE user SET joins = joins + 1, join_date = NOW() WHERE user = %s;", [nick])
        cursor.close()

def stats_part(self,e,c):
    if hasSql:
        cursor = self.db.cursor()
        if stats.nicks == []:
            load_nick_table(cursor)

        nick = nm_to_n(e.source())

        if not nick in stats.nicks:
            return

        cursor.execute("SELECT joins, join_date, averagetime, NOW() from user WHERE user = %s;", [nick])
        joins, join_date, averagetime, time = cursor.fetchone()
            
        cursor.execute("UPDATE user SET parts = parts + 1, part_date = NOW() WHERE user = %s;", [nick])

        cursor.close()        

def stats(self, e, c):
    if hasSql:

        cursor = self.db.cursor()
        if stats.nicks == []:
            load_nick_table(cursor)

        nick = nm_to_n(e.source())

        cursor.execute("SELECT joins, join_date, averagetime, NOW() from user WHERE user = %s;", [nick])
        joins, join_date, averagetime, time = cursor.fetchone()
        print joins, join_date, averagetime, time

        if not nick in stats.nicks:
            cursor.execute("INSERT INTO user (user) VALUES(%s);", [nick])
            stats.nicks.append(nick)
        
        line = e.arguments()[0]
        wordcount = len(line.split())
        currenthour = int(strftime("%H",localtime()))
        cursor.execute("UPDATE user SET said = said + 1, words = words + %s WHERE user = %s;", [wordcount,nick])
        cursor.execute("UPDATE hourstats SET said = said + 1, words = words + %s WHERE hour = %s;", [wordcount,currenthour])
        cursor.close()