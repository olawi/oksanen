#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad
import string
from oksanen import hasSql
from time import strftime, localtime
import datetime

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

def timediff(first,second):
    first = strftime(first, "%Y-%m-%d %H:%M:%S")
    first = datetime.datetime(first[0],first[1],first[2],first[3],first[4],first[5])
    second = strftime(second, "%Y-%m-%d %H:%M:%S")
    second = datetime.datetime(second[0],second[1],second[2],second[3],second[4],second[5])
    
    timedelta = first-second

    output = ""
    if (timedelta.days > 0):
        if (timedelta.days > 1):
            output += "%s päivää ja " %(timedelta.days)
        else:
            output += "yhden päivän ja "

    m, s = divmod(timedelta.seconds, 60)
    h, m = divmod(m, 60)
    if (h > 0):
        output += "%s tuntia " %(h)
    if (m > 0):
        output += "%s minuuttia " %(m)

    output += "%s sekuntia " %(s)
    return output
        
def stats(self, e, c):
    if hasSql:

        cursor = self.db.cursor()
        if stats.nicks == []:
            load_nick_table(cursor)

        nick = nm_to_n(e.source())

        cursor.execute("SELECT joins, join_date, averagetime, NOW() from user WHERE user = %s;", [nick])
        joins, join_date, averagetime, time_now = cursor.fetchone()
        output = "%s oli kanavalla %s" %(nick,timediff(join_date,time_now))
        
        print output

        if not nick in stats.nicks:
            cursor.execute("INSERT INTO user (user) VALUES(%s);", [nick])
            stats.nicks.append(nick)
        
        line = e.arguments()[0]
        wordcount = len(line.split())
        currenthour = int(strftime("%H",localtime()))
        cursor.execute("UPDATE user SET said = said + 1, words = words + %s WHERE user = %s;", [wordcount,nick])
        cursor.execute("UPDATE hourstats SET said = said + 1, words = words + %s WHERE hour = %s;", [wordcount,currenthour])
        cursor.close()