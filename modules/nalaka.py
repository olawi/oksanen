#!/usr/bin/env python
# coding=utf-8

import urllib
import HTMLParser

import string
import re
import random

from ircbot import SingleServerIRCBot
from irclib import nm_to_n
from ircutil import bold, recode

kaenkky_url = 'http://www.kaenkky.com/txt/'
                
def setup(self):
    self.commands['näläkä'] = nalaka

def get_kaenkky(self,query):

    fd = urllib.urlopen(kaenkky_url+query)
    page = fd.read()
    fd.close()

    lines = string.split(page,'\n')
    results = []

    for l in lines:
        print l
        m = re.findall(r'([^;]*?);',l)
        if m :
            results.append(m)

    return results
    
def nalaka(self,e,c):

    line = e.arguments()[0]
    query = string.join(line.split()[1:],' ')

    if query:
        query = "?s=%s"%query

    kama = get_kaenkky(self,recode(query,'latin-1'))

    outstr = ""
    try :
        for k in kama:
            outstr += "%s - %s: %s, avoinna: %s " % (bold(k[1]),k[2],k[4],k[7])
        c.privmsg(e.target(),outstr)
    except:
        c.privmsg(e.target(),"Nyt ei kuule löytynyt mitään.")
        
# from www.kaenkky.com :
#
# palautuvat kentät / rivi (eroteltuna puolipisteellä):
# 0  id (voit käyttää linkitykseen: www.kaenkky.com/?p=k&id=[id])
# 1  nimi
# 2  lyhyesti
# 3  aliakset
# 4  yhteystiedot
# 5  puhelinnumero
# 6  kategoria
# 7  aukioloajat tänään
# 8  hintataso
# 9  visa electron (1 kyllä, 0 ei, -1 ei tietoa)
# 10 kanta-asiakaspassi (1 kyllä, 0 ei, -1 ei tietoa)
# 11 lounassetelit (1 kyllä, 0 ei, -1 ei tietoa)
# 12 panoulu kuuluu (1 kyllä, 0 ei, -1 ei tietoa)
# 13 avoinna juuri nyt (1 kyllä, 0 ei)
# 14 kuva #1 nimi (jos ei kuvaa, niin ei_kuvaa.jpg) (url http://kaenkky.com/kuvat/kaenkkylae/[nimi])
# 15 kuva #2 nimi (jos ei kuvaa, niin ei_kuvaa.jpg) (url http://kaenkky.com/kuvat//kaenkkylae/[nimi])
# 16 kotiinkuljetus (1 kyllä, 0 ei, -1 ei tietoa)

