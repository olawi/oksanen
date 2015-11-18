#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, is_channel

import string
import random
import array
from sanalista import wordgame_wordlist
from oksanen import hasSql

def setup(self):
    self.pubcommands['sana'] = kysysana
    self.pubhandlers.append(sanaChecker)
    sana.just_asked = False
    sana.current_word = ""
    sana.current_word_shuffle = ""
    sana.cron_id = self.cron.add_event({'count':1,'minute':[random.randint(0,59)]}, sana, self)

def terminate(self):
    """delete cron hook"""
    try:
        self.cron.delete_event(sana.cron_id)
    except:
        pass

def sana_shuffle(self, txt):
    out = ''.join(random.sample(txt, len(txt)))
    return out
		
def kysysana(self, e, c):
    """command !sana handler"""
    nick = nm_to_n(e.source())

    line = e.arguments()[0]
    new_word = string.join(line.split()[1:], " ")

    if (not is_channel(e.target()) and self.is_admin(e.source())):
        # for admins in /query
        if (len(new_word) > 0):
            sana.current_word = unicode(new_word, 'utf-8')
        else:
            sana.current_word = random.choice(wordgame_wordlist)
        sana.just_asked = False

    if (len(sana.current_word) > 0):
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

    sana.current_word_shuffle = sana_shuffle(self, sana.current_word)

    output = "Ratkaise sana: %s"%(sana.current_word_shuffle)
    if not sana.just_asked:
        c.privmsg(channel, output)
        print "in module sana sending: %s / %s " % (sana.current_word_shuffle, sana.current_word)
        sana.just_asked = True

def sanaChecker(self, e, c):
    sana.just_asked = False
    if len(sana.current_word) > 0:
        line = unicode(e.arguments()[0], 'utf-8')

        if line == sana.current_word:
            nick = nm_to_n(e.source())
            sana.current_word = ""
            cursor = self.db.cursor()
            sqlquery = """INSERT INTO gamescores (user,wordgame) VALUES (%s,1) ON DUPLICATE KEY UPDATE wordgame = wordgame + 1;"""
            cursor.execute(sqlquery, [nick] )
            cursor.close()
            cursor = self.db.cursor()
            cursor.execute("SET @rownum := 0;")
            sqlquery = """SELECT wordgame,rank FROM (SELECT @rownum := @rownum+1 AS rank, wordgame, user FROM gamescores ORDER BY wordgame DESC) AS derived_table WHERE user=%s;"""
            cursor.execute(sqlquery, [nick] )
            score, rank = cursor.fetchone()
            c.privmsg(e.target(), "%s, oikein meni! Sinulla on nyt %s pistettä. Sijalla %s" % (nick, score, rank))
            cursor.close()
