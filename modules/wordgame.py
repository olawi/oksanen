#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

import random
from wordgame_wordlist import wordgame_wordlist

current_word = ""
current_word_shuffle = ""

def setup(self):
    self.commands['sana'] = sana
    self.pubhandlers.append(sanaChecker)
    
def sana(self, e, c):
    nick = nm_to_n(e.source())
    if current_word != "":
        c.privmsg(e.target(), "%s: ratkaise ensin tämä: %s"%(nick, current_word_shuffle))
        return
    else:
        current_word = random.choice(wordgame_wordlist)
        character_list = list(current_word)
        random.shuffle(character_list)
        current_word_shuffle = "".join(character_list)
        c.privmsg(e.target(), "%s: sanapelin sana: %s"%(nick, current_word_shuffle))

def sanaChecker(self, e, c):
    line = e.arguments()[0]
    if line == current_word:
        nick = nm_to_n(e.source())
        c.privmsg(e.target(), "%s: Oikein meni! Onnittelut"%(nick))
        current_word = ""