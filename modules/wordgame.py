#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

import random
from wordgame_wordlist import wordgame_wordlist
#import wordgame_wordlist

def setup(self):
    self.commands['sana'] = sana
    self.pubhandlers.append(sanaChecker)
    sana.current_word = ""
    sana.current_word_shuffle = ""
    
def sana(self, e, c):
    nick = nm_to_n(e.source())
    if len(sana.current_word) == 0:
        c.privmsg(e.target(), "%s: ratkaise ensin tämä: %s"%(nick, sana.current_word_shuffle))
        return
    else:
        sana.current_word = random.choice(sana_wordlist)
        character_list = list(sana.current_word)
        random.shuffle(character_list)
        sana.current_word_shuffle = "".join(character_list)
        c.privmsg(e.target(), "%s: sanapelin sana: %s"%(nick, sana.current_word_shuffle))

def sanaChecker(self, e, c):
    line = e.arguments()[0]
    if len(sana.current_word) != 0:
        if line == sana.current_word:
            nick = nm_to_n(e.source())
            c.privmsg(e.target(), "%s: Oikein meni! Onnittelut"%(nick))
            sana.current_word = ""
