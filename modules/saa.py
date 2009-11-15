#!/usr/bin/env python
# coding=utf-8

import urllib
import htmllib
import formatter

import HTMLParser

import string
import re
import time
import random

from ircbot import SingleServerIRCBot
from irclib import nm_to_n

fmi_locations = [ 'Alajarvi','Asikkala','Enontekio','Espoo','Foglo','Haapavesi','Hailuoto','Halsua','Hammarland','Hanko','Heinola','Helsinki','Hyvinkaa','Hameenlinna','Iisalmi','Ilomantsi','Inari','Inkoo','Joensuu','Jokioinen','Joutsa','Juuka','Juupajoki','Juva','Jyvaskyla','Jamsa','Kajaani','Kalajoki','Kankaanpaa','Kauhajoki','Kemi','Kemijarvi','Kemionsaari','Kilpisjarvi','Kirkkonummi','Kittila','Kokemaki','Kokkola','Korsnas','Kotka','Kouvola','Kristiinankaupunki','Kuhmo','Kumlinge','Kuopio','Kustavi','Kuusamo','Lahti','Lappeenranta','Lieksa','Lohja','Luhanka','Lansi-Turunmaa','Maaninka','Maarianhamina','Mikkeli','Multia','Muonio','Naantali','Nivala','Nurmes','Nurmijarvi','Oulu','Parikkala','Pelkosenniemi','Pello','Pernaja','Pietarsaari','Pori','Porvoo','Pudasjarvi','Punkaharju','Puumala','Pyhajarvi','Raahe','Raasepori','Ranua','Rauma','Rautavaara','Rovaniemi','Saariselka','Salla','Salo','Savonlinna','Savukoski','Seinajoki','Siikajoki','Sodankyla','Sotkamo','Suomussalmi','Taipalsaari','Taivalkoski','Tampere','Tohmajarvi','Tornio','Turku','Utsjoki','Uusikaupunki','Vaasa','Vantaa','Varkaus','Vihti','Viitasaari','Virolahti','Virrat','Ylitornio','Ylivieska','Ahtari']

willab_url = "http://weather.willab.fi/weather.html"
fmi_url = "http://www.fmi.fi/saa/paikalli.html?place="

saa_qrep = [
    "Pitääkö se yhtenään olla sitä säätäkin utelemassa?",
    "En minä mikään liikkuva sääasema ole?",
    "Näytänkö minä sinusta Juha Föhriltä? Häh?",
    "RAUHOTTUKAAPA!",
    "Mikä ihme siinä on ettei ihmisiä muu kiinnosta?"
    ]

saa_orep = [
    "VTT:n Jari tuumailee että Oulussa on lämmintä palttiarallaa",
    "Oulussa",
    "Teknillisen tutkimuskeskuksen ihmeellinen laitteisto kertoo että Oulusa",
    "Ai mää vai? Oulussa on",
    "Teknologiakylän katolla ainaki on "
    ]

saa_mrep = [
    "Vitut minä siitä tiedän tai välitän, mutta Oulussa on",
    "Ai jossain perähikiällä? Mitä väliä! Oulussa on",
    "Missä? Täällä on ainaki",
    "En kuule tiedä. Mitä sä siellä teet? Oulussa on",
    "Otappa ihan itte kuule selvää. Oulussa on"
    ]

class willab_parser(htmllib.HTMLParser):
    
    def __init__(self, verbose=0):
        self.state = 0
        self.output = []
        self.weatherdata = {}
        self.last_key = ''
        f = formatter.NullFormatter()
        htmllib.HTMLParser.__init__(self, f, verbose)
        
    def start_p(self,attrs):
        for i in attrs:
            if i == ("class","tempnow"):
                self.state = 1;
                self.save_bgn()
                
    def end_p(self):
        if self.state == 1:
            self.output = "%s"%self.save_end()
            self.state = 0;

    def start_th(self,attrs):
        self.save_bgn()
    def end_th(self):
        s = "%s"%self.save_end()
        self.last_key = re.sub('[^\w]','',string.lower(string.join(s.split(),'')))

    def start_td(self,attrs):
        self.save_bgn()
    def end_td(self):
        s = self.save_end()
        self.weatherdata[self.last_key] = "%s"%s

class fmi_parser(HTMLParser.HTMLParser):
    
    def __init__(self, verbose=0):
        self.state = 0
        self.content = ''
        self.buf = ''
        HTMLParser.HTMLParser.__init__(self)

    def handle_data(self,data):
        if self.state == 1:
            self.buf += r"%s"%data

    def handle_entityref(self, name):
        if self.state == 1:
            if name == 'auml':
                self.buf += 'ä'
            if name == 'ouml':
                self.buf += 'ö'
            if name == 'aring':
                self.buf += 'å'
            if name == 'Auml':
                self.buf += 'Ä'
            if name == 'Ouml':
                self.buf += 'Ö'
            if name == 'Aring':
                self.buf += 'Å'
            if name == 'nbsp':
                self.buf += ' '
                
    def handle_startendtag(self,tag,attrs):
        if tag == 'br' and self.state == 1:
            self.buf += ' '
        
    def handle_starttag(self,tag,attrs):
        if tag == 'p':
            for a in attrs:
                if a == ("class","observation-text"):
                    self.buf = ''
                    self.state = 1
        if tag == "strong" and self.state == 1:
            self.buf += ' '
        #if tag == 'option': # fmi_locations printout
            # print "'%s',"%attrs[0][1]            

    def handle_endtag(self,tag):
        if tag == "p":
            if self.state == 1:
                self.content = self.buf
                self.state = 0
        if tag == "strong" and self.state == 1:
            self.buf += ' ' 

def get_fmi(self,location):
    
    print "%s%s"%(fmi_url,location)
    fd = urllib.urlopen("%s%s"%(fmi_url,location))
    page = fd.read()
    fd.close
    
    p = fmi_parser()
    p.feed(page)
    
    return p.content

def get_willab(self):

    fd = urllib.urlopen("%s"%willab_url)
    page = fd.read()
    fd.close
    
    p = willab_parser()
    p.feed(page)

    p.weatherdata['tempnow'] = p.output    
    return p.weatherdata
    
def setup(self):
    self.commands['sää'] = saa
    saa.timelast = time.time()
    
def saa(self,e,c):

    saa.timenow = time.time()
    line = e.arguments()[0]

    c = self.connection

    if len(line.split()[1:]) < 1:
        location = 'Oulu'
    else:
        location = string.lower("%s"%line.split()[1])

    location = re.sub('ä','a',location)
    location = re.sub('ö','o',location)
    location = re.sub('Ä','a',location)
    location = re.sub('Ö','o',location)
    location = string.capitalize(location)

    if location in fmi_locations:
        output = get_fmi(self,location)
    else:
        output = "paikkakuntaa ei löydy fmi.fi. Sori!"
   
    c.privmsg(e.target(),"%s : %s"%(location,output))
    saa.timelast = saa.timenow

