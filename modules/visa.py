#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_u
import string
import ircutil

from oksanen import hasSql

def setup(self):
    self.pubhandlers.append(check_question)
    self.privcommands['musavisa'] = musavisa
    self.privcommands['leffavisa'] = leffavisa
    self.commands['musakysymys'] = musavisa_print
    self.commands['leffakysymys'] = leffavisa_print
    leffavisa.question = ""
    leffavisa.answer = ""
    leffavisa.inquirer = ""
    musavisa.question = ""
    musavisa.answer = ""
    musavisa.inquirer = ""

def musavisa(self,e,c):
    add_question(self,e,c,0)

def leffavisa(self,e,c):
    add_question(self,e,c,1)
    
def musavisa_print(self,e,c):
    if (musavisa.question != ""):
        c.privmsg(e.target(), "Musavisa: %s" %(musavisa.question))
    else:
        c.privmsg(e.target(), "Musavisa ei ole juuri nyt käynnissä. Lisää uusi kysymys: /msg Oksanen !musavisa vastaus|kysymys")
        
def leffavisa_print(self,e,c):
    if (leffavisa.question != ""):
        c.privmsg(e.target(), "Leffavisa: %s" %(leffavisa.question))
    else:
        c.privmsg(e.target(), "Leffavisa ei ole juuri nyt käynnissä. Lisää uusi kysymys: /msg Oksanen !leffavisa vastaus|kysymys")
    
def check_question(self,e,c):
    nick = nm_to_n(e.source())
    if (leffavisa.question != "" and leffavisa.inquirer != nick):
        if (e.arguments()[0].lower() == leffavisa.answer.lower()):
            cursor = self.db.cursor()
            sqlquery = """INSERT INTO gamescores (user,leffavisa) VALUES (%s,1) ON DUPLICATE KEY UPDATE leffavisa = leffavisa + 1;"""
            cursor.execute(sqlquery, [nick] )
            c.privmsg(e.target(), "%s, jee, oikein meni!" %(nick))
            leffavisa.question = ""
            cursor.close()
            return
    if (musavisa.question != "" and musavisa.inquirer != nick):
        if (e.arguments()[0].lower() == musavisa.answer.lower()):
            cursor = self.db.cursor()
            sqlquery = """INSERT INTO gamescores (user,musavisa) VALUES (%s,1) ON DUPLICATE KEY UPDATE musavisa = musavisa + 1;"""
            cursor.execute(sqlquery, [nick] )
            c.privmsg(e.target(), "%s, jee, oikein meni!" %(nick))
            musavisa.question = ""
            cursor.close()
            return
          
def add_question(self,e,c,type):
    nick = nm_to_n(e.source())
    if (type == 0 and musavisa.question != ""):
        c.privmsg(nick, "Ratkaise ensin kyssäri:%s" %(musavisa.question))
        return
    elif (type == 1 and leffavisa.question != ""):
        c.privmsg(nick, "Ratkaise ensin kyssäri:%s" %(leffavisa.question))
        return

    line = e.arguments()[0]
    line = ircutil.recode(string.join(line.split()[1:], " "))
    line = line.split("|")
    if (len(line) == 2 and len(line[0])>0 and len(line[1])>0):
        cursor = self.db.cursor()
        if (type == 0):
            sqlquery = """INSERT INTO musavisa (USER,QUESTION,ANSWER) VALUES (%s,%s,%s);"""
            cursor.execute(sqlquery, [nick,line[1],line[0]])
            musavisa.question = line[1]
            musavisa.answer = line[0]
            musavisa.inquirer = nick
            c.privmsg(self.channel, "Musavisa: %s" %(line[1]))
        else:
            sqlquery = """INSERT INTO leffavisa (USER,QUESTION,ANSWER) VALUES (%s,%s,%s);"""
            cursor.execute(sqlquery, [nick,line[1],line[0]])
            leffavisa.question = line[1]
            leffavisa.answer = line[0]
            leffavisa.inquirer = nick
            c.privmsg(self.channel, "Leffavisa: %s" %(line[1]))
        cursor.close()
    else:
        print_usage(self,nick,c,type)
    
def print_usage(self,nick,c,type):
    if type == 0:
        c.privmsg(nick, "!musavisa vastaus|kysymys")
    else:
        c.privmsg(nick, "!leffavisa vastaus|kysymys")
