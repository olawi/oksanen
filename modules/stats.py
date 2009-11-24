#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad
import string
from oksanen import hasSql
from time import strftime, localtime
import datetime

def seconds_to_string(seconds):
    elementcount = 0
    output = ""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if (h > 0):
        elementcount += 1
        if (h > 1):
            output += "%s tuntia " %(h)
        else:
            output += "yhden tunnin "
    if (m > 0):
        if (elementcount > 0 and s == 0):
            output += "ja "
        elementcount += 1
        if (m > 1):
            output += "%s minuuttia " %(m)
        else:
            output += "yhden minuutin "
    
    if (elementcount > 0):
        output += "ja "
    
    if (s > 1):
        output += "%s sekuntia" %(s)
    else:
        output += "sekunnin"
    
    return output

def timediff(first,second): 
    timedelta = second-first
    output = ""
    if (timedelta.days > 0):
        if (timedelta.days > 1):
            output += "%s p‰iv‰‰ ja " %(timedelta.days)
        else:
            output += "yhden p‰iv‰n ja "

    output += seconds_to_string(timedelta.seconds)

    return output

def load_nick_table(cursor):
    cursor.execute("SELECT user FROM user")
    for row in cursor.fetchall():
        stats.nicks.append(row[0])

def setup(self):
    self.pubhandlers.append(stats)
    self.joinhandlers.append(stats_join)
    self.parthandlers.append(stats_part)
    self.quithandlers.append(stats_part)
    stats.nicks = []
    stats.channel = self.channel

def stats_join(self,e,c):
    if hasSql:
        cursor = self.db.cursor()
        if stats.nicks == []:
            load_nick_table(cursor)

        nick = nm_to_n(e.source())

        if not nick in stats.nicks:
            cursor.execute("INSERT INTO user (user,firstseen) VALUES(%s,NOW());", [nick])
            stats.nicks.append(nick)
        else:
            cursor.execute("SELECT said, joins, join_date, averagetime, part_date from user WHERE user = %s;", [nick])
            said, joins, join_date, averagetime, part_date = cursor.fetchone()
            if (joins > 1):
                output = "Tervetuloa %s! Olit viimeksi kanavalla %s" %(nick,timediff(join_date,part_date))
                output += " - keskim‰‰rin olet ollut %s" %(seconds_to_string(averagetime))
                output += " | %s rivi‰ per kerta." %(said/joins)
                c.privmsg(nick, output)
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
        joins, join_date, averagetime, time_now = cursor.fetchone()

        timedelta = time_now-join_date
        timeonchannel = timedelta.seconds + (timedelta.days*86400)
        averagetime = (((joins-1)*averagetime)+timeonchannel)/joins
        
        cursor.execute("UPDATE user SET averagetime = %s, parts = parts + 1, part_date = NOW() WHERE user = %s;", [averagetime,nick])

        cursor.close()        

def stats(self, e, c):
    if hasSql:

        cursor = self.db.cursor()
        if stats.nicks == []:
            load_nick_table(cursor)

        nick = nm_to_n(e.source())

        if not nick in stats.nicks:
            cursor.execute("INSERT INTO user (user,joins,firstseen) VALUES(%s,1,NOW());", [nick])
            stats.nicks.append(nick)
        
        line = e.arguments()[0]
        wordcount = len(line.split())
        currenthour = int(strftime("%H",localtime()))
        cursor.execute("UPDATE user SET said = said + 1, words = words + %s WHERE user = %s;", [wordcount,nick])
        cursor.execute("UPDATE hourstats SET said = said + 1, words = words + %s WHERE hour = %s;", [wordcount,currenthour])
        cursor.close()
