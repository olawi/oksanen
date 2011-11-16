#!/usr/bin/env python
# coding=utf-8

"""
alarm.py - set up an alarm for a user to ring once 
"""

import string
import re
import random
from datetime import datetime, timedelta

from irclib import nm_to_n
from ircutil import run_once

DEBUG = 1

def setup(self):
    """setup called by oksanen on startup"""

    self.pubcommands['alarm'] = alarm
    self.pubcommands['herätys'] = alarm
    self.pubcommands['notetoself'] = alarm_random
    try :
        alarm.data = self.moduledata['alarm']
    except:
        alarm.data = {}
    """ notes do not survive resets """
    alarm.notes = []

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
    c.privmsg(e.target(), "%s, %s"%(nick, alarm_string))

def notetoself_callback(self, e, c, alarm_string):
    nick = nm_to_n(e.source())
    alarm.notes.remove(nick)   
    c.privmsg(e.target(), "%s, %s"%(nick, alarm_string))

def alarm_random(self, e, c):
    """ set a random alarm for the five days """
    a_rminutes = random.randint(1,60*24*5)

    """ check for existing alarms for nick and return or do alarm """
    line = e.arguments()[0]
    params = line.split()[1:]
    nick = nm_to_n(e.source())

    if len(params) > 0:
        w_string = string.join(params[0:],' ')
    else:
        c.privmsg(e.target(), "%s, mistähän sinua nyt oikein pitäisi muistuttaa?"%nick)
        return

    if nick in alarm.notes:
        c.privmsg(e.target(), "%s, en minä nyt joka asiasta ala sinua yhtenään muistuttamaan!"%(nick))
        return

    alarm.notes.append(nick)

    t_alarm = datetime.now() + timedelta (minutes = a_rminutes)

    self.cron.add_event({'count':1, 'day':[t_alarm.day], 'month':[t_alarm.month], 'hour':[t_alarm.hour], 'minute':[t_alarm.minute]}, notetoself_callback, self, e, c, w_string)

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
        try:
            d_mins = int(a_time)
            t_alarm = datetime.now() + timedelta (minutes = d_mins)
            a_hour = t_alarm.hour
            a_mins = t_alarm.minute
        except Exception, ex:
            help(self, e, c)
            return

    if len(params) > 1:
        w_string = string.join(params[1:],' ')
    else:
        w_string = "herätys!"

    """ notify nick """
    c.notice(nick, "herätys asetettu %02d:%02d"%(a_hour, a_mins))

    """ set the alarm callback """
    tmp = self.cron.add_event({'count':1, 'hour':[a_hour], 'minute':[a_mins]}, alarm_callback, self, e, c, w_string)
