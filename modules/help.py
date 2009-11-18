#!/usr/bin/env python
# coding=utf-8

from recode import recode

def setup(self):
    self.commands['help'] = help

def help(self, e, c):
    """help"""
    out = 'komennot:'
    k = self.commands.keys()
    k.sort()
    for s in k:
        out += " !%s"%s

    c.privmsg(e.target(),out)
