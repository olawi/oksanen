#!/usr/bin/env python
# coding=utf-8

import urllib2
import string
import re
import random
from irclib import nm_to_n

tissit_url = 'http://%s.kiinnostaa.org/'

def setup(self):
    self.commands['tissit'] = tissit
    self.commands['pillu'] = tissit
    self.commands['perse'] = tissit
    self.commands['pano'] = tissit
    self.commands['lesbot'] = tissit
    self.commands['suihinotto'] = tissit

def get_tissit(self, url, thumbs=False):

    # Get index
    fd = urllib2.urlopen(url+'index.htm')
    data = fd.read()
    fd.close()

    subpages = re.findall(r'<a href=\"(\d+.htm)"',data)
    
    # randomize and get subpage
    page = random.choice(subpages)

    fd = urllib2.urlopen(url+page)
    data = fd.read()
    fd.close()
    
    # return url to image
    if thumbs:
        imlist = re.findall(r'<img [^>]*? src=\"(thumb\/[\d\w]+.jpg)"',data)
    else:
        imlist = re.findall(r'<a href=\"(src\/[\d\w]+.jpg)"',data)
    if imlist:
        img = random.choice(imlist)
    else:
        img = 'index.htm'
    return url + img

def tissit(self, e, c):
    
    nick = nm_to_n(e.source())

    #Parse command
    try:
        cmd = re.findall('^!(\w+)',e.arguments()[0])[0]
    except:
        print "We shouldn't be here..."
        cmd = 'tissit'

    if len(string.split(e.arguments()[0])) > 1:
        use_thumbs = True
    else:
        use_thumbs = False
        
    s = get_tissit(self, tissit_url%cmd, use_thumbs)
    c.privmsg(e.target(),"%s, %s"%(nick, s))


    
