#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

import random
from wordgame_wordlist import wordgame_wordlist
from oksanen import hasSql

def setup(self):
    self.cron.add_event({'minute':[25]}, sana, self)
    self.pubcommands['sana'] = kysysana
    self.pubhandlers.append(sanaChecker)
    sana.current_word = ""
    sana.current_word_shuffle = ""
    
def kysysana(self, e, c):
    if len(sana.current_word) != 0:
        c.privmsg(e.target(), "%s: Ratkaise tämä: %s"%(nick,sana.current_word_shuffle))
    else:
        c.privmsg(e.target(), "%s: Sanapeli ei ole nyt käynnissä. Malta hetki."%(nick))
    
def sana(self):
    c = self.connection
    channel = self.channel
    if len(sana.current_word) != 0:
        c.privmsg(channel, "Ratkaise tämä: %s"%(sana.current_word_shuffle))
        return
    else:
        sana.current_word = random.choice(wordgame_wordlist)
        #print "bgn !sana: %s"%sana.current_word
        character_list = list(sana.current_word)
        random.shuffle(character_list)
        sana.current_word_shuffle = "".join(character_list)
        c.privmsg(channel, "Ratkaise tämä: %s"%(sana.current_word_shuffle))

def sanaChecker(self, e, c):
    if len(sana.current_word) != 0:
        line = e.arguments()[0]
        if line == sana.current_word:
            nick = nm_to_n(e.source())
            c.privmsg(e.target(), "%s: Oikein meni!"%(nick))
            sana.current_word = ""
            cursor = self.db.cursor()
            sqlquery = """INSERT INTO gamescores (user,wordgame) VALUES (%s,1) ON DUPLICATE KEY UPDATE wordgame = wordgame + 1;"""
            cursor.execute(sqlquery, [nick] )
            cursor.close()
