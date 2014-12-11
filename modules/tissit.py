#!/usr/bin/env python
# coding=utf-8

import urllib2
import string
import re
import random
from irclib import nm_to_n

DEBUG = 1

tissit_url = 'http://%s.kiinnostaa.org/'
tissit_cmdlist = ['tissit', 'pillu', 'perse', 'pano', 'lesbot', 'suihinotto', 'softcore', 'vintage']

def setup(self):
    for cmd in tissit_cmdlist:
        self.pubcommands[cmd] = tissit
    try:
        tissit.urls = self.moduledata['tissit']
    except:
        tissit.urls = {}
        
def terminate(self):
    """save data"""
    self.moduledata['tissit'] = tissit.urls

def get_tissit_index(self, url, cmd):
    fd = urllib2.urlopen(url%cmd+'index.htm')
    data = fd.read()
    fd.close()
    subpages = re.findall(r'<a href=\"(\d+.htm)"',data)
    if DEBUG > 1:
        print subpages
    return subpages
    
def get_tissit(self, url, cmd, thumbs=False):

    # Get index and select a random subpage
    try:
        page = random.choice(tissit.urls[cmd])
        print "tissit: using cached urls for %s"%cmd
    except:
        print "tissit: retrieving index for %s"%(url%cmd)
        try:
            tissit.urls[cmd] = get_tissit_index(self, url, cmd)
            page = random.choice(tissit.urls[cmd])
            if DEBUG > 0: 
                print page
        except Exception, ex:
            print "\033[31mERROR\033[m (tissit): %s"%ex
            return "sori, ei tänään."

    try:
        if DEBUG > 0:
            print url%cmd + page
        fd = urllib2.urlopen(url%cmd + page)
    except:
        """links outdated?"""
        print "tissit: index for %s outdated, refreshing..."%(url%cmd)
        try:
            tissit.urls[cmd] = get_tissit_index(self, url, cmd)
            page = random.choice(tissit.urls[cmd])
        except Exception, ex:
            print "\033[31mERROR\033[m (tissit): %s"%ex
            return "sori, ei tänään."
    try:
        fd = urllib2.urlopen(url%cmd + page)
        data = fd.read()
        fd.close()
    except Exception, ex:
        print "\033[31mERROR\033[m (tissit): %s"%ex
        return "sori, ei tänään."
    
    # return url to image
    if thumbs:
        imlist = re.findall(r'<img [^>]*? src=\"[\w\:\/\.]*?(_thumb|thumb|kuvat)(\/[\d\w]+\.jpg)"',data)
    else:
        imlist = re.findall(r'<a href=\"[\w\:\/\.]*?(_src|kuvat|src)(\/[\d\w]+\.jpg)"',data)
    if imlist:
        if DEBUG > 1:
            print imlist
        img = ''.join(random.choice(imlist))
    else:
        img = 'index.htm'
        
    return url%cmd + img

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
        
    s = get_tissit(self, tissit_url, cmd, use_thumbs)
    c.privmsg(e.target(),"%s, %s"%(nick, s))


    
