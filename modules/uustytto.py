#!/usr/bin/env python
# coding=utf-8

import re
import string

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_u

from girlnames import girlnames

uustytto_lista = []

def setup(self):
    self.joinhandlers.append(uustytto)

def getlist(self):
    cursor = self.db.cursor()
    cursor.execute("""SELECT name FROM uustytto""")
    for row in cursor.fetchall():
        uustytto_lista.append(row[0])

def uustytto(self,e,c):
    
    nick = nm_to_n(e.source())

    self.whoiscallbacks.insert(0,uustytto_callback)
    c.send_raw("WHOIS %s"%nick)

def uustytto_callback(self,e,c):
    if uustytto_lista == []:
        getlist(self);

    nick = self.whoisinfo['user'][0]
    snick = re.sub('[^a-zA-Z0-9]','',nick)
    
    realname = self.whoisinfo['user'][4]

    firstname = realname.split()[0]

    if string.lower(firstname) in girlnames :
        print " TYTTÖ! ----> %s"%realname
        if not snick in uustytto_lista:
            cursor = self.db.cursor()
            sqlquery = """INSERT INTO uustytto (NAME) VALUES (%s); """
            cursor.execute(sqlquery, [snick] )
            uustytto_lista.append(snick)
            c.privmsg(e.target(), "UUSTYTTÖ <3")
        else:
            # wanhatyttö
