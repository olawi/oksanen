#!/usr/bin/env python
# coding=utf-8

def setup(self):
    self.pubcommands['help'] = help

def help(self, e, c):
    """help"""
    out = 'komennot:'
    k = self.pubcommands.keys()
    k.sort()
    for s in k:
        out += " !%s"%s

    c.privmsg(e.target(),out)
