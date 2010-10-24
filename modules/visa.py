#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_u
import string
import ircutil
import random

from oksanen import hasSql

def setup(self):
    self.pubhandlers.append(check_question)
    self.privcommands['musavisa'] = musavisa
    self.privcommands['leffavisa'] = leffavisa
    self.pubcommands['musavisa'] = musavisa_print
    self.pubcommands['leffavisa'] = leffavisa_print
    leffavisa.question = ""
    leffavisa.answer = ""
    leffavisa.inquirer = ""
    musavisa.question = ""
    musavisa.answer = ""
    musavisa.inquirer = ""
    musavisa.cron_id = self.cron.add_event({'count':1,'minute':[random.randint(0,59)]}, ask_question, self)

def ask_question(self):
    c = self.connection
    channel = self.channel
    musavisa.cron_id = self.cron.add_event({'count':1,'hour':[random.randint(0,23)],'minute':[random.randint(0,59)]}, ask_question, self)
    cursor = self.db.cursor()
    sqlquery = """SELECT * FROM musavisa ORDER BY RAND() LIMIT 1;"""
    cursor.execute(sqlquery, [] )
    id, user, question, answer, date = cursor.fetchone()
    musavisa.question = question
    musavisa.answer = answer
    musavisa.inquirer = user
    c.privmsg(channel, "Musavisa: %s (kysyi: %s)" %(question,user))
    cursor.close()

def terminate(self):
    """delete cron hook"""
    try:
        self.cron.delete_event(musavisa.cron_id)
    except:
        pass
	
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
            cursor.close()
            cursor = self.db.cursor()
            cursor.execute("SET @rownum := 0;")
            sqlquery = """SELECT leffavisa,rank FROM (SELECT @rownum := @rownum+1 AS rank, leffavisa, user FROM gamescores ORDER BY leffavisa DESC) AS derived_table WHERE user=%s;"""
            cursor.execute(sqlquery, [nick])
            row = cursor.fetchone()
            print sqlquery
            print row[0],row[1]
            c.privmsg(e.target(), "%s, oikein meni! Sinulla on nyt %s pistettä. Leffavisassa sijalla %s" % (nick, row[0], row[1]))
            cursor.close()
            leffavisa.question = ""
            return
    if (musavisa.question != "" and musavisa.inquirer != nick):
        if (e.arguments()[0].lower() == musavisa.answer.lower()):
            cursor = self.db.cursor()
            sqlquery = """INSERT INTO gamescores (user,musavisa) VALUES (%s,1) ON DUPLICATE KEY UPDATE musavisa = musavisa + 1;"""
            cursor.execute(sqlquery, [nick] )
            cursor.close()
            cursor = self.db.cursor()
            cursor.execute("SET @rownum := 0;")
            sqlquery = """SELECT musavisa,rank FROM (SELECT @rownum := @rownum+1 AS rank, musavisa, user FROM gamescores ORDER BY musavisa DESC) AS derived_table WHERE user=%s;"""
            cursor.execute(sqlquery, [nick])
            row = cursor.fetchone()
            c.privmsg(e.target(), "%s, oikein meni! Sinulla on nyt %s pistettä. Musavisassa sijalla %s" % (nick, row[0], row[1]))
            cursor.close()
            musavisa.question = ""
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
            c.privmsg(nick, "Kysymys nakattu kanavalle!")
        else:
            sqlquery = """INSERT INTO leffavisa (USER,QUESTION,ANSWER) VALUES (%s,%s,%s);"""
            cursor.execute(sqlquery, [nick,line[1],line[0]])
            leffavisa.question = line[1]
            leffavisa.answer = line[0]
            leffavisa.inquirer = nick
            c.privmsg(self.channel, "Leffavisa: %s" %(line[1]))
            c.privmsg(nick, "Kysymys nakattu kanavalle!")
        cursor.close()
    else:
        print_usage(self,nick,c,type)

def print_usage(self,nick,c,type):
    if type == 0:
        c.privmsg(nick, "!musavisa vastaus|kysymys")
    else:
        c.privmsg(nick, "!leffavisa vastaus|kysymys")
