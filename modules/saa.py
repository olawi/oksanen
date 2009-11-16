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
    "Pit��k� se yhten��n olla sit� s��t�kin utelemassa?",
    "En min� mik��n liikkuva s��asema ole?",
    "N�yt�nk� min� sinusta Juha F�hrilt�? H�h?",
    "RAUHOTTUKAAPA!",
    "Mik� ihme siin� on ettei ihmisi� muu kiinnosta?"
    ]

saa_orep = [
    "VTT:n Jari tuumailee ett� Oulussa on l�mmint� palttiarallaa",
    "Oulussa",
    "Teknillisen tutkimuskeskuksen ihmeellinen laitteisto kertoo ett� Oulusa",
    "Ai m�� vai? Oulussa on",
    "Teknologiakyl�n katolla ainaki on "
    ]

saa_mrep = [
    "Vitut min� siit� tied�n tai v�lit�n, mutta Oulussa on",
    "Ai jossain per�hiki�ll�? Mit� v�li�! Oulussa on",
    "Miss�? T��ll� on ainaki",
    "En kuule tied�. Mit� s� siell� teet? Oulussa on",
    "Otappa ihan itte kuule selv��. Oulussa on"
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
                self.buf += '�'
            if name == 'ouml':
                self.buf += '�'
            if name == 'aring':
                self.buf += '�'
            if name == 'Auml':
                self.buf += '�'
            if name == 'Ouml':
                self.buf += '�'
            if name == 'Aring':
                self.buf += '�'
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
        if tag == 'strong' and self.state == 1:
            self.buf += ' '
        #if tag == 'option': # fmi_locations printout
            # print "'%s',"%attrs[0][1]            

    def handle_endtag(self,tag):
        if tag == "p":
            if self.state == 1:
                self.content = self.buf
                self.state = 0
        if tag == 'strong' and self.state == 1:
            self.buf += ' ' 

def get_fmi(self,location):
    
    print("%s%s"%(fmi_url,location))
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

def ircb(s):
    return u'\u0002%s\u000f'%s

def setup(self):
    self.commands['s��'] = saa
    saa.timelast = time.time()
    
def saa(self,e,c):

    saa.timenow = time.time()
    line = e.arguments()[0]

    c = self.connection

    if len(line.split()[1:]) < 1:
        location = 'Oulu'
    else:
        location = string.lower("%s"%line.split()[1])

    location = re.sub('�','a',location)
    location = re.sub('�','o',location)
    location = re.sub('�','a',location)
    location = re.sub('�','o',location)
    location = string.capitalize(location)

    if location in fmi_locations:
        raw_output = get_fmi(self,location)
    else:
        c.privmsg(e.target(),"%s - fmi.fi ei l�yd� paikkakuntaa. Sori!"%location)
        return

    showall = False
    if len(line.split()[1:]) > 1:
        showall = True

    buf = string.join(raw_output.split(),' ')
    buf = re.sub('�','a',buf)
    buf = re.sub('�','o',buf)
    
    w_data = {}
    m = re.search('(\d+.\d+.\d+)\s+(\d+:\d+)',buf)
    buf = re.sub('.*?Suomen\s+aikaa','',buf)


    print buf
    if m:
        w_data['date'] = m.group(1)
        w_data['time'] = m.group(2)
        
    attrs = re.findall('(\w+\s?\w+)\s+?([\d,-]+)\s+([^\s\d]+?)\s*(\(\d+:\d+\))?[;:.]',buf)

    for a in attrs:
        w_data[string.lower(a[0])] = a[1:]

    print(w_data) 

    wignore = ['lampotila','time','date']
    output = ''

    if 'time' in w_data and 'lampotila' in w_data:
        output += u"%s: %s\u00B0%s"%(
            ircb(location),
            ircb(w_data['lampotila'][0]),
            w_data['lampotila'][1]
            )
        for k, v in w_data.iteritems():
            if re.search('tuulta',k):
                output += ", %s %s%s"%(k,v[0],v[1])
                wignore.append(k)
        output += ", mitattu klo %s"%w_data['time']
        
        if showall :
            for k, v in w_data.iteritems():
                if k in wignore:
                    continue
                if v[2]:
                    output += "; %s %s%s %s"%(k,v[0],v[1],v[2])
                else:
                    output += "; %s %s%s"%(k,v[0],v[1])
    else:
        c.privmsg(e.target(),"fmi:ll� jotain h�ss�kk��. T�ss� n�m� raakatiedot:")
        output = raw_output
        
    c.privmsg(e.target(),"%s"%(output.encode('latin-1')))
    saa.timelast = saa.timenow
    
