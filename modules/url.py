#!/usr/bin/env python
# coding=utf-8

import re
import string
import urllib
from sgmllib import SGMLParser

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

url_s = '(((https?|ftp):\\/\\/)|www\\.)(([0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+)|([a-zA-Z0-9\\-]+\\.)*[a-zA-Z0-9\\-]+\\.(com|net|org|info|biz|gov|name|edu|[a-zA-Z][a-zA-Z]))(:[0-9]+)?((\\/|\\?)[^ "]*[^,;\\.:">)])?'

# lyhyt w-puskuri
urlbuf = []

class parser(SGMLParser):
    def __init__(self, content_start_comment='', content_end_comment=''):
        SGMLParser.__init__(self)
        self.buf = ""
        self.title = ""
        
    def handle_data(self, data):
        self.buf += data

    def start_title(self,attrs):
        self.buf = ""

    def end_title(self):
        self.title = self.buf
        self.title = string.join(self.title.split(),' ')
        self.buf = ""

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

    try:
        fd = urllib.urlopen(uri)
    except:
        return
    
    page = fd.read()
    fd.close()

    p = parser()
    p.feed(page)

    if len(p.title) < 1:
        return
    
    if uri in urlbuf:
        return

    nick = nm_to_n(e.source())
    c.privmsg(e.target(), "%s - '%s'"%(nick,p.title))
    
    urlbuf.insert(0,uri)
    
    if len(urlbuf) > 8:
        del urlbuf[-1]
        
