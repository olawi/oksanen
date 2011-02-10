#!/usr/bin/env python
# coding=utf-8

import urllib
import urllib2
import htmllib
import formatter

import HTMLParser

import string
import re
import time
import random

from ircbot import SingleServerIRCBot
from irclib import nm_to_n
import ircutil

DEBUG = 1

willab_url = "http://weather.willab.fi/weather.html"
fmi_url = "http://www.fmi.fi/saa/paikalli.html?place="
tieh_url = "http://alk.tiehallinto.fi/"

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

class fmi_parser2(htmllib.HTMLParser):

    def __init__(self, verbose=0):
        self.state = 0 
        self.wdata = []
        self.current = ['','']
        f = formatter.NullFormatter()
        htmllib.HTMLParser.__init__(self, f, verbose)

    def start_span(self,attrs):
         for a in attrs:
            if a == ('class', 'parameter-name'):
                self.state = 1
                self.save_bgn()
            elif a == ('class', 'parameter-value'):
                self.state = 2
                self.save_bgn()
            else:
                self.state = 0

    def end_span(self):
        if self.state == 1: 
            self.current[0] = ircutil.recode(self.save_end())
        elif self.state == 2:
            self.current[1] = ircutil.recode(self.save_end())
            self.wdata.append(self.current[:])
        self.state = 0

class tieh_parser(htmllib.HTMLParser):
    
    def __init__(self, verbose=0):
        self.state = 0 
        '''The HTML is ill-formatted so we need this'''
        self.sflag = 0 
        self.current_location = ''
        self.skip_data = 0
        self.wdata = {}
        f = formatter.NullFormatter()
        htmllib.HTMLParser.__init__(self, f, verbose)

    def start_tr(self,attrs):
        self.state = 0

    def start_td(self,attrs):
        self.sflag = 1
        self.save_bgn()
 
    def end_td(self):
        if self.sflag:
            s = self.save_end()

            if self.state == 0: 
                self.current_location = re.sub(r'Tie \d+ ','',s)
                self.current_location = ircutil.recode(self.current_location)
            else:
                if not self.current_location in self.wdata.keys():
                    self.wdata[self.current_location] = []
                if not self.skip_data:
                    self.wdata[self.current_location].append(ircutil.recode(s))
                
        self.state = 1
        self.sflag = 0

def get_fmi(self,location):
    
    print("%s%s"%(fmi_url,location))
    fd = urllib.urlopen("%s%s"%(fmi_url,location))
    page = fd.read()
    fd.close
    
    p = fmi_parser2()
    p.feed(page)

    print p.wdata
    
    return p.wdata

def get_willab(self):

    fd = urllib.urlopen("%s"%willab_url)
    page = fd.read()
    fd.close
    
    p = willab_parser()
    p.feed(page)

    p.weatherdata['tempnow'] = unicode(p.output,'ascii','ignore')
    return p.weatherdata

def get_tieh(self,url,skip=0):

    fd = urllib2.urlopen(tieh_url+url)
    page = fd.read()
    fd.close
    
    p = tieh_parser()
    p.skip_data = skip
    p.feed(page)
    return p.wdata

def get_tieh_urls(self):

    fd = urllib2.urlopen(tieh_url+'alk/tiesaa/tiesaa_kokomaa.html')
    data = fd.read()
    fd.close()
    subpages = re.findall(r'href=\"([\w\d\_\/]+.html)"',data)
    return subpages

def update_tieh_locations(self):

    saa.tieh_locations = {}
    for urli in get_tieh_urls(self):
        tmp_locations = get_tieh(self,urli,1)
        for k in tmp_locations.keys():
            tmp_locations[k] = urli
        saa.tieh_locations.update(tmp_locations)
        
def setup(self):
    self.pubcommands['sää'] = saa 
    self.pubcommands['saa'] = saa
    saa.timelast = time.time()
    saa.tieh_locations = {}

def saa(self,e,c):

    saa.timenow = time.time()
    line = e.arguments()[0]

    showall = False
    if len(line.split()[1:]) > 1:
        showall = True

    if len(line.split()[1:]) < 1:
        location = 'Oulu'
    else:
        location = string.lower("%s"%line.split()[1])

    if location == 'willab':
        w_data = get_willab(self)
        output = ircutil.bold('Oulu')
        output += ", VTT:n katto, %s"%ircutil.bold(w_data['tempnow'])
        if showall:
            for k, v in w_data.iteritems():
                if not k == 'tempnow':
                    output += "; %s %s"%(k,unicode(v,'ascii','ignore'))
        c.privmsg(e.target(),output)
        saa.timelast = saa.timenow
        return

    flocation = re.sub('ä','a',location)
    flocation = re.sub('ö','o',location)
    flocation = re.sub('Ä','a',location)
    flocation = re.sub('Ö','o',location)
    flocation = string.capitalize(location)

    fmi_data = get_fmi(self,flocation)
    
    if fmi_data:
        output = fmi_data[0][1]
        if showall:
            for x in fmi_data[1:]:
                output += ", %s %s"%(x[0],x[1])
        else:
            for x in fmi_data:
                m = re.search('Tyyntä|tuulta',x[0])
                if m:
                    output += ", %s %s"%(x[0],x[1])

        c.privmsg(e.target(),"%s: %s "%(flocation,output))
        saa.timelast = saa.timenow
        return

    if location == 'minmax':
        '''Get all temperatures from tiehallinto...'''
        all_urls = get_tieh_urls(self)
        all_wdata = {}
        for urli in all_urls:
            w_data = get_tieh(self,urli)
            all_wdata.update(w_data)
            
        w_min = ['Helvetti', 666.0]
        w_max = ['Ryssän helvetti', -666.0]

        for s in all_wdata.keys():
            try:
                if float(all_wdata[s][1]) < float(w_min[1]):
                    w_min[0] = s
                    w_min[1] = all_wdata[s][1]
                if float(all_wdata[s][1]) > float(w_max[1]):
                    w_max[0] = s
                    w_max[1] = all_wdata[s][1]
            except:
                continue

        output = "min - %s: %s °C; "%(w_min[0],w_min[1])
        output += "max - %s: %s °C"%(w_max[0],w_max[1])
        c.privmsg(e.target(),output)
        saa.timelast = saa.timenow
        return

    '''defaults to tiehallinto'''

    if not saa.tieh_locations:
        update_tieh_locations(self)
        if DEBUG > 1:
            print saa.tieh_locations

    '''Match the query from locations'''
    sub_url = ''
    location_key = ''
    for s in saa.tieh_locations.keys():
        m = re.match(location, s, re.I)
        if m:
            print s
            location_key = s
            sub_url = saa.tieh_locations[s]
            break

    if not sub_url:
        for s in saa.tieh_locations.keys():
            m = re.search('\s%s'%location, s, re.I)
            if m:
                print s
                location_key = s
                sub_url = saa.tieh_locations[s]
                break

    if not sub_url:
        c.privmsg(e.target(),"Sori, ei löydy sen nimistä paikkaa.")
        saa.timelast = saa.timenow
        return

    '''Get the weather data from corresponding page'''
    wall_data = get_tieh(self,sub_url)
    w_data =  wall_data[location_key]

    print w_data
    output = "%s: "%location_key
    output += "%s °C"%w_data[1]
    if w_data[3]:
        output += ", %sa"%w_data[3]
        if w_data[3] != 'Pouta':
            output += " sadetta"
 
    if showall:
        output += ", tie: %s °C"%w_data[2]
        output += ", keli %s"%w_data[4]
        output += ", mitattu klo %s"%w_data[0]

    c.privmsg(e.target(),output)

    saa.timelast = saa.timenow
    
