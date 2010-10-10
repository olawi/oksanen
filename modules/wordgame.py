#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

import random
from wordgame_wordlist import wordgame_wordlist
from oksanen import hasSql, is_admin

def setup(self):
    self.pubcommands['sana'] = kysysana
    self.pubhandlers.append(sanaChecker)
    sana.current_word = ""
    sana.current_word_shuffle = ""
    sana.cron_id = self.cron.add_event({'count':1,'minute':[random.randint(0,59)]}, sana, self)

def terminate(self):
    """delete cron hook"""
    try:
        self.cron.delete_event(sana.cron_id)
    except:
        pass
		
def kysysana(self, e, c):
    nick = nm_to_n(e.source())
    if ((len(sana.current_word) > 0) or is_admin(e.source())):
        if is_admin(e.source()):
            self.cron.delete_event(sana.cron_id)
        sana(self)
    else:
        c.privmsg(e.target(), "%s: Sanapeli ei ole nyt käynnissä. Malta hetki."%(nick))
    
def sana(self):
    c = self.connection
    channel = self.channel
    sana.cron_id = self.cron.add_event({'count':1,'minute':[random.randint(0,59)]}, sana, self)
    if len(sana.current_word) < 1:
        sana.current_word = random.choice(wordgame_wordlist)
    character_list = list(sana.current_word)
    random.shuffle(character_list)
    sana.current_word_shuffle = "".join(character_list)
    c.privmsg(channel, "Ratkaise tämä: %s"%(sana.current_word_shuffle))
    print "in module sana sending: %s / %s " % (sana.current_word_shuffle, sana.current_word)

def sanaChecker(self, e, c):
    if len(sana.current_word) != 0:
        line = e.arguments()[0]
        if line == sana.current_word:
            nick = nm_to_n(e.source())
            sana.current_word = ""
            cursor = self.db.cursor()
            sqlquery = """INSERT INTO gamescores (user,wordgame) VALUES (%s,1) ON DUPLICATE KEY UPDATE wordgame = wordgame + 1;"""
            cursor.execute(sqlquery, [nick] )
            cursor.close()
            cursor = self.db.cursor()
			sqlquery = """SET @rownum := 0;SELECT wordgame,rank FROM (SELECT @rownum := @rownum+1 AS rank, wordgame, user FROM gamescores ORDER BY wordgame DESC) AS derived_table WHERE user='%s';"""
            #sqlquery = """SELECT wordgame FROM gamescores WHERE `user`=%s;"""
            cursor.execute(sqlquery, [nick] )
            score, rank = cursor.fetchone()
            c.privmsg(e.target(), "%s, oikein meni! Sinulla on nyt %s pistettä. Sijalla %s" % (nick, score, rank))
            cursor.close()
