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

DEBUG = 2

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
            if name == 'deg':
                self.buf += '°'
            if name == 'nbsp':
                self.buf += ' '
               
    def handle_startendtag(self,tag,attrs):
        if tag == 'br' and self.state == 1:
            self.buf += ' '
        
    def handle_starttag(self,tag,attrs):
        if tag == 'table':
            for a in attrs:
                if a == ("class","observation-text"):
                    self.buf = ''
                    self.state = 1
        if tag == 'span':
            for a in attrs:
                if a == ("class","parameter-name-value"):
                    self.buf += ' '

    def handle_endtag(self,tag):
        if tag == "table":
            if self.state == 1:
                self.content = self.buf
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
                    self.wdata[self.current_location].append(s)
                
        self.state = 1
        self.sflag = 0

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

    if location == 'fmi':
        if len(line.split()[1:]) < 1:
            location = 'Oulu'
        else:
            location = string.lower("%s"%line.split()[2])

        location = re.sub('ä','a',location)
        location = re.sub('ö','o',location)
        location = re.sub('Ä','a',location)
        location = re.sub('Ö','o',location)
        location = string.capitalize(location)

        raw_output = get_fmi(self,location)

        buf = ircutil.recode(string.join(raw_output.split(),' '))
        print buf

        if len(raw_output) > 0:
            output = buf
        else:
            c.privmsg(e.target(),"Sori, paikkaa %s ei löydy."%location)
            return
        
        c.privmsg(e.target(),"%s: %s "%(location,output))
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
        '''try fmi and give up'''
        e._arguments = ["%s %s %s"%(line.split()[0],'fmi',location)]
        saa(self,e,c)
        return

    '''Get the weather data from corresponding page'''
    wall_data = get_tieh(self,sub_url)
    w_data =  wall_data[location_key]

    print w_data
    output = "%s: "%location_key
    output += "%s°C, "%w_data[1]
    output += "%sa"%w_data[3]
    if w_data[3] != 'Pouta':
        output += " sadetta"

    c.privmsg(e.target(),output)

    '''Somethn fkucked up if this does not match'''

    saa.timelast = saa.timenow
    
