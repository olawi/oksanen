#!/usr/bin/env python
# coding=utf-8

import urllib
import htmllib
import formatter

import requests
import json

import datetime
import string
import re
import time
import ircutil

DEBUG = 1

willab_url = "http://weather.willab.fi/weather.html"
openweather_url = "http://api.openweathermap.org/data/2.5/weather?q="
openweather_id = '8ae66f0928735e53127b2e285736d576'

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

def wind_string(self, value):
    windnames = [u'pohjois', u'koillis', u'itä', u'kaakkois', u'etelä', u'lounais', u'länsi', u'luoteis']
    idx = int(round(value/45.0) % 8) 
    return windnames[idx]    

def get_willab(self):

    fd = urllib.urlopen("%s"%willab_url)
    page = fd.read()
    fd.close
    
    p = willab_parser()
    p.feed(page)

    p.weatherdata['tempnow'] = unicode(p.output,'ascii','ignore')
    return p.weatherdata

def get_openweather(self, location):

    mode = 'json'
    lang = 'fi'
    units = 'metric'
    id = openweather_id
    
    reply = requests.get("%s%s&mode=%s&lang=%s&units=%s&APPID=%s" % (openweather_url, location, mode, lang, units, id))
    print reply.text
    
    data = json.loads(reply.text)
    return data

def setup(self):
    self.pubcommands['sää'] = saa 
    self.pubcommands['saa'] = saa
    saa.timelast = time.time()

def saa(self,e,c):

    saa.timenow = time.time()
    line = e.arguments()[0]

    showall = False
    if len(line.split()[1:]) > 1:
        showall = True

    if len(line.split()[1:]) < 1:
        location = 'willab'
    else:
        location = string.lower("%s"%line.split()[1])

    if location == 'willab':
        # Use willab
        w_data = get_willab(self)
        output = ircutil.bold('Oulu')
        output += u", VTT:n katto, %s" % ircutil.bold(w_data['tempnow'])
        if showall:
            for k, v in w_data.iteritems():
                if not k == 'tempnow':
                    output += "; %s %s" % (k,unicode(v,'ascii','ignore'))

    else:
        # Use openweahermap.org
        w_data = get_openweather(self, location)
        output = ircutil.bold(w_data['name'])
        if w_data['sys']['country'] != 'FI':
            output += ", %s" % w_data['sys']['country']
        output += u", %s °C" % ircutil.bold(round(w_data['main']['temp'],1))
        try:
            output += u", %stuulta %s m/s" % (wind_string(self, w_data['wind']['deg']), ircutil.bold(round(w_data['wind']['speed'],1)))
        except:
            # not all stations provide direction
            output += u", tuulta %s m/s" % ircutil.bold(round(w_data['wind']['speed'],1))
            
        output += u", %s." % w_data['weather'][0]['description']

        if showall:
            try:
                output += u" Ilmankosteus %s %%" % w_data['main']['humidity']
                output += u", ilmanpaine %s hPa" % w_data['main']['pressure']
            except:
                pass
            try:
                nousu = datetime.datetime.fromtimestamp(w_data['sys']['sunrise']).strftime('%H:%M')
                lasku = datetime.datetime.fromtimestamp(w_data['sys']['sunset']).strftime('%H:%M')
                output += u". Aurinko nousee %s ja laskee %s" % (nousu, lasku)
            except:
                pass
        
    c.privmsg(e.target(), output)
    saa.timelast = saa.timenow
