#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_u

from oksanen import hasSql

def setup(self):
    self.pubhandlers.append(check_question)
    self.privcommands['musavisa'] = musavisa
    self.privcommands['leffavisa'] = leffavisa
    leffavisa.question = ""
    leffavisa.answer = ""
    musavisa.question = ""
    musavisa.answer = ""

def musavisa(self,e,c):
    add_question(self,e,c,0)

def leffavisa(self,e,c):
    add_question(self,e,c,1)
    
def check_question(self,e,c):
    if (leffavisa.question != ""):
        if (e.arguments()[0].lower() == leffavisa.answer.lower()):
            cursor = self.db.cursor()
            nick = nm_to_n(e.source())
            sqlquery = """INSERT INTO gamescores (user,leffavisa) VALUES (%s,1) ON DUPLICATE KEY UPDATE leffavisa = leffavisa + 1;"""
            cursor.execute(sqlquery, [nick] )
            c.privmsg(e.target(), "%s, jee, oikein meni!" %(nick))
            leffavisa.question = ""
            leffavisa.answer = ""
            cursor.close()
            return
    if (musavisa.question != ""):
        if (e.arguments()[0].lower() == musavisa.answer.lower()):
            cursor = self.db.cursor()
            nick = nm_to_n(e.source())
            sqlquery = """INSERT INTO gamescores (user,musavisa) VALUES (%s,1) ON DUPLICATE KEY UPDATE musavisa = musavisa + 1;"""
            cursor.execute(sqlquery, [nick] )
            c.privmsg(e.target(), "%s, jee, oikein meni!" %(nick))
            musavisa.question = ""
            musavisa.answer = ""
            cursor.close()
            return
          
def add_question(self,e,c,type):
    nick = nm_to_n(e.source())
    line = string.join(line.split()[1:], " ")
    line = line.split("|")
    if (len(line) == 2 and len(line[0])>0 and len(line[1])>0):
        cursor = self.db.cursor()
        if (type == 0):
            sqlquery = """INSERT INTO musavisa (USER,QUESTION,ANSWER) VALUES (%s,%s,%s);"""
            cursor.execute(sqlquery, [nick,line[1],line[0]])
            musavisa.question = line[1]
            musavisa.answer = line[0]
            c.privmsg(self.channel, "Musavisa: %s" %(line[1]))
        else:
            sqlquery = """INSERT INTO leffavisa (USER,QUESTION,ANSWER) VALUES (%s,%s,%s);"""
            cursor.execute(sqlquery, [nick,line[1],line[0]])
            leffavisa.question = line[1]
            leffavisa.answer = line[0]
            c.privmsg(self.channel, "Leffavisa: %s" %(line[1]))
        cursor.close()
    else:
        print_usage(self,nick,c,type)
    
def print_usage(self,nick,c,type):
    if type == 0:
        c.privmsg(nick, "!musavisa vastaus|kysymys")
    else:
        c.privmsg(nick, "!leffavisa vastaus|kysymys")
