#!/usr/bin/env python
# coding=utf-8
#
# Add here common functions related to
# text formatting etc. in IRC
#

import string,re
import threading

DEBUG = 1

def bold(s):
    return u'\u0002%s\u000f'%s

def ul(s):
    return u'\u001F%s\u000f'%s

def it(s):
    return u'\u0016%s\u000f'%s

def wordwrap(text, length_max, trim_whitespace=True):
    """Wrap long lines by word boundaries"""
    rarray = []

    """nothing to do"""
    if len(text) < (length_max):
        rarray.append(text)
        return rarray

    i = 0
    """Find whitespace indexes"""
    for m in re.finditer('(\s*)([^\s+]*)',text):
        """ group 1 is the leading whitespace, group 2 the text """
        if (m.end()- i) > (length_max):
            rarray.append(text[i:m.start()])

            if trim_whitespace:
                i = m.start(2)
            else:
                i = m.start(1)

    if i != len(text):
        rarray.append(text[i:])

    return rarray

"""if all else fails"""
recode_fallback = 'CP1252'

def recode(text, encoding='utf-8',enlist=[]):

    if not enlist:
        enlist = ['ascii', 'utf-8', 'iso-8859-15', 'iso-8859-1', recode_fallback]
    else:
        enlist.append(recode_fallback)
        
    out = u''

    for enc in enlist:
        try: 
            out = text.decode(enc)
            if DEBUG > 1:
                print "in recode success: %s"%enc
            break
        except Exception, ex:
            if DEBUG > 1:
                print "in recode fail: %s: %s"%(enc,ex)

    if DEBUG > 1:
        print repr(out)

    """raaka peli"""
    if not out: out = text

    if DEBUG > 1:
        try:
            print out.encode('utf-8')
        except Exception, ex:
            print "in recode print :%s"%ex

    try:
        text = out.encode(encoding)
    except:
        print "in recode: %s"%ex

    if DEBUG > 1:
        print repr(text)

    return text

def run_once(time, func, args=[], kwargs={}):
    """Run the given function once after time seconds"""
    try:
        t = threading.Timer(time, func, args, kwargs)
        t.start()
    except Exception, ex:
        print "\033[31mERROR\033[m (ircutil.run_once): %s"%ex
