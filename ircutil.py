#!/usr/bin/env python
# coding=utf-8
#
# Add here common functions related to
# text formatting etc. in IRC
#

import string,re

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

