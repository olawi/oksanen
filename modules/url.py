#!/usr/bin/env python
# coding=utf-8

import re
import string

from urllib import FancyURLopener
from sgmllib import SGMLParser

from oksanen import hasSql
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad
from ircutil import recode, run_once
from censor import censor

url_re = re.compile(r'(((https?|ftp):\/\/)|www\.)(([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)|([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.(com|net|org|info|biz|gov|name|edu|[a-zA-Z][a-zA-Z]))(:[0-9]+)?((\/|\?)[^ "]*[^,;\.:">)])?')

spotify_uri_re = re.compile(r'(spotify:)(album|artist|track)([:\/])([a-zA-Z0-9]+)\/?')

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
    self.repubhandlers.update({ url_re : urlhandler})
    self.repubhandlers.update({ spotify_uri_re : spotify_uri})
    self.pubcommands['url'] = urlshow
    urlshow.url = "(eipäs olekkaan vielä!)"

def urlshow(self, e, c):
    c.privmsg(e.target(), "Net on netissä: %s"%(urlshow.url))

def spotify_uri(self, e, c):
    line = e.arguments()[0]
    m = re.search(spotify_uri_re,line)
    if m:
        s_url = "http://open.spotify.com/%s/%s"%(m.group(2),m.group(4))
        run_once(0, _urlhandler, [self, e, c, s_url])
    else:
        return

def urlhandler(self, e, c):
    run_once(0, _urlhandler, [self, e, c])
    
def _urlhandler(self, e, c, line = ''):

    if not line:
        line = e.arguments()[0]

    m = re.search(url_re,line)
    
    if not m:
        return

    uri = m.group(0)
    
    if uri.startswith('www.'):
        uri = re.sub('^www.','http://www.',uri)

    opr = opener()

    try:
        fd = opr.open(uri)
    except:
        print "url.py: FAIL opening %s"%uri
        return
    
    nick = nm_to_n(e.source())
    page = fd.read()
    fd.close()

    if fd.headers.gettype() == 'text/html':
        p = parser()
        try :
            p.feed(page)
            pagetitle = recode(p.output)
        except:
            print "url.py: parseri kosahti, jatketaan..."
            pagetitle = ''
# Commented this out, seems to cause crashes
#    elif fd.headers.getmaintype() == 'image':
        # IF there were anything useful in the headers..
#        pagetitle = fd.headers.gettype()
    else:
        pagetitle = ''
            
    if hasSql:
        cursor = self.db.query("SELECT USER, DATE FROM url WHERE URI = %s;", [uri])
        for row in cursor.fetchall():
            if nick != row[0]:
                d = row[1]
                dstr = "%s.%s.%s %02d:%02d"%(d.day, d.month, d.year, d.hour, d.minute)
                wsayer = censor(row[0])
                c.privmsg(e.target(), "W! - '%s' - (%s %s)"%(pagetitle, wsayer, dstr))
                return 
            else:
                """repeat the whole title, It has possibly been changed"""
                c.privmsg(e.target(), "(%s)"%pagetitle)
                return

        qstr = "INSERT INTO url (USER, URI, TITLE) VALUES (%s, %s, %s); "
        cursor.execute(qstr, [nick, uri, pagetitle])
        cursor.close()
            
    if len(pagetitle) < 1:
        return
    else:
        c.privmsg(e.target(), "%s - '%s'"%(nick,pagetitle))
        
