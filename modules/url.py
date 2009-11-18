#!/usr/bin/env python
# coding=utf-8

import re
import string

from urllib import FancyURLopener
from sgmllib import SGMLParser

from oksanen import hasSql
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad
from ircutil import recode

url_s = '(((https?|ftp):\\/\\/)|www\\.)(([0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+)|([a-zA-Z0-9\\-]+\\.)*[a-zA-Z0-9\\-]+\\.(com|net|org|info|biz|gov|name|edu|[a-zA-Z][a-zA-Z]))(:[0-9]+)?((\\/|\\?)[^ "]*[^,;\\.:">)])?'

class parser(SGMLParser):
    def __init__(self, content_start_comment='', content_end_comment=''):
        SGMLParser.__init__(self)
        self.buf = ""
        self.output = ""
        self.entitydefs.update({'auml':'ä','ouml':'ö','aring':'å','Auml':'Ä','Ouml':'Ö','Aring':'Å','nbsp':' ',})
        
    def handle_data(self, data):
        self.buf += data

    def start_title(self,attrs):
        self.buf = ""

    def end_title(self):
        self.output = self.buf
        self.output = string.join(self.output.split(),' ')
        self.buf = ""

class opener(FancyURLopener):
    version = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.246.0 Safari/532.5'

def setup(self):
    self.pubhandlers.append(urlhandler)

def urlhandler(self, e, c):

    line = e.arguments()[0]
    
    url_re = re.compile(url_s)
    m = re.search(url_re,line)
    
    if not m:
        return

    uri = m.group(0)
    
    if re.match('www.',uri):
        uri = re.sub('^www.','http://www.',uri)

    opr = opener()

    try:
        fd = opr.open(uri)
    except:
        print "url.py: FAIL opening %s"%uri
        return
    
    nick = nm_to_n(e.source())
    page = fd.read(1024)
    fd.close()

    p = parser()
    p.feed(page)

    pagetitle = recode(p.output)

    if hasSql:
        cursor = self.db.cursor()
        
        cursor.execute("""SELECT USER, DATE FROM url WHERE URI = %s;""", [uri])
        for row in cursor.fetchall():
            if nick != row[0]:
                c.privmsg(e.target(), "%s - Wanha! Ensimmäisenä mainitsi %s %s"%(nick,row[0],row[1]))
                return #wanha
            
        command = """INSERT INTO url (USER, URI, TITLE) VALUES (%s, %s, %s); """
        cursor.execute(command, [nick, uri, pagetitle] )
            
    if len(pagetitle) < 1:
        return
    else:
        c.privmsg(e.target(), "%s - '%s'"%(nick,pagetitle))
        
