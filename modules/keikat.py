#!/usr/bin/python
# coding=utf-8

import urllib
import htmllib

import formatter
import string
import sys
from optparse import OptionParser
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

class Writer():
    def __init__(self, city):
        self.output = r"Keikat %s: " %city
        self.curdate = "foo"
        self.count = 0

    def addevent(self, event="Unknown", date=None, place=None, href=None, price=None):
        if self.count < 5:
            self.count += 1
        else:
            return

        if self.curdate != date:
            self.output += "%s - " %date
            self.curdate = date
        self.output += "%s"%event
        if place:
            self.output += " - %s"%place
        if price:
            self.output += " - %s e"%price 
        if self.count != 5:
            self.output += " | "  

class Parser(htmllib.HTMLParser):
    def __init__(self, writer, verbose=0):
        self.writer=writer
        self.state = 0
        self.anchors = {}
        f = formatter.NullFormatter()
        htmllib.HTMLParser.__init__(self, f, verbose)

    def start_div(self, attrs):
        if self.state == 0:
            for i in attrs:
                if i==("class", "toplinks"):
                    self.state = 1
                    return
        if self.state == 1:
            self.state = 2
            self.save_bgn()

    def end_div(self):
        if self.state != 2:
            return
        desc = self.save_end()
        self.state = 1

    def start_br(self, attrs):
        if self.state == 2:
            self.date = self.save_end()
            self.state = 3
            return
        if self.state == 5:
            self.save_bgn()
            self.state = 6
            return
        if self.state == 6:
            s = self.save_end().split(", ")
            self.place = s[0]
            if (len(s)>1):
                self.price = s[1].split(" ")[0]
            else:
                self.price = None
            self.writer.addevent(self.event, date=self.date, place=self.place,
                                 href=self.href, price=self.price)

            self.state = 1

    def end_a(self):
        if self.state == 4:
            self.event = self.save_end()
            self.state = 5

    def start_a(self, attrs):
        if self.state == 3:
            for i in attrs:
                if i[0] == "href":
                    self.href = i[1]
            self.save_bgn()
            self.state = 4

class meteli:
    citydict = { "oulu": 283,
                 "helsinki": 70,
                 "joensuu": 98,
                 "jyvaskyla" : 109,
                 "jyväskyla" : 109,
                 "kotka" : 173,
                 "kouvola": 174,
                 "kuopio": 183,
                 "lahti": 199,
                 "pori": 314,
                 "seinajoki": 369,
                 "seinäjoki": 369,
                 "tampere": 400,
                 "turku": 411
                 }

    def __init__(self, city):
        self.cityid=self.resolve(city)
        print self.cityid
        if self.cityid != None:
            self.city=city
            self.fd=urllib.urlopen("http://meteli.mobi/paikka/%d"%self.cityid)
            self.page = self.fd.read()
            self.fd.close()

    def resolve(self, city):
        return self.citydict[string.lower(city)]

    def toIRC(self):
        w=Writer(self.city)
        p=Parser(w)
        p.feed(self.page)
        p.close()
        return w.output

def keikat(self, e, c):

    nick = nm_to_n(e.source())
    c = self.connection

    line = e.arguments()[0]
    target = "".join(line.split()[1:])
    if (target and len(target) > 0):
        finder = meteli(target)
    else:
        finder = meteli("oulu")
    if finder.cityid:
        stuff = finder.toIRC()
        c.privmsg(e.target(), stuff)
    else:
        c.privmsg(e.target(), "%s: Mikäs hiton mettä tuo on??"%nick)

keikat.commands = ['keikat']
