#!/usr/bin/env python
# coding=utf-8

"""
OMG stands for Oksanen Module Generale
It is a general template to use as a module.
M-x replace-string <RET> OMG <RET> newmodule <RET>
"""

import string
import re

from irclib import nm_to_n
from ircutil import run_once

DEBUG = 1

"""precompiled regex for OMG_track"""
_OMG_REGEX = re.compile(r'^OMG\b')

def setup(self):
    """setup called by oksanen on startup"""

    self.repubhandlers.update({_OMG_REGEX : OMG_track})
    self.privcommands['OMG'] = OMG_privcmd
    self.pubcommands['OMG'] = OMG_pubcmd
    try :
        OMG.data = self.moduledata['OMG']
    except:
        OMG.data = {}

def terminate(self):
    """save data. called by oksanen.reset and .reload"""
    self.moduledata['OMG'] = OMG.data

def help(self):
    """return a help string"""
    s = "OMG help!"

def OMG(self, e, c):
    """module main"""
    pass

def OMG_track(self, e, c):
    """run _OMG_track in a thread"""
    run_once(0, _OMG_track, [self, e, c])

def _OMG_track(self, e, c):
    pass

def OMG_privcmd(self, e, c):
    """privcommand OMG"""
    pass

def OMG_pubcmd(self, e, c):
    """pubcommand OMG"""
    pass


