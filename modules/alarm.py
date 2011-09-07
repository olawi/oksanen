#!/usr/bin/env python
# coding=utf-8

"""
alarm.py - set up an alarm for a user to ring once 
"""

import string
import re

from irclib import nm_to_n
from ircutil import run_once

DEBUG = 1

def setup(self):
    """setup called by oksanen on startup"""

    self.pubcommands['alarm'] = alarm
    self.pubcommands['herätys'] = alarm
    try :
        alarm.data = self.moduledata['alarm']
    except:
        alarm.data = {}

def terminate(self):
    """save data. called by oksanen.reset and .reload"""
    self.moduledata['alarm'] = alarm.data

def help(self, e, c):
    """return a help string"""
    try:
        cmd = re.findall('^!([\wäöÄÖ]+)',e.arguments()[0])[0]
    except:
        cmd = 'herätys'
    s = "Käytetään esim: !%s 19:30 ota pizza uunista"%cmd
    c.privmsg(e.target(), s)

def alarm_callback(self, e, c, alarm_string='HERÄTYS!'):
    nick = nm_to_n(e.source())
    c.privmsg(e.target(), "%s, %s"%(nick,alarm_string))

def alarm(self, e, c):
    """ parse time and wakeup string """
    line = e.arguments()[0]
    params = line.split()[1:]
    nick = nm_to_n(e.source())

    if len(params):
        a_time = params[0]
    else:
        help(self, e, c)
        return

    m = re.search('(\d+)\:(\d+)', a_time)
    try:
        a_hour = int(m.group(1))
        a_mins = int(m.group(2))
    except Exception, ex:
        help(self, e, c)
        return

    if len(params) > 1:
        w_string = string.join(params[1:],' ')
    else:
        w_string = "herätys!"

    """ notify nick """
    c.notice(nick, "herätys asetettu %s:%s"%(a_hour,a_mins))

    """ set the alarm callback """
    tmp = self.cron.add_event({'count':1, 'hour':[a_hour], 'minute':[a_mins]}, alarm_callback, self, e, c, w_string)
