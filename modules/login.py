#!/usr/bin/env python
# coding=utf-8

"""
login for admins to login. 
Reads admin password from a file not in version control
"""

from irclib import nm_to_n

DEBUG = 1

pwfile = '.apasswd'

def setup(self):
    """setup called by oksanen on startup"""

    self.privcommands['login'] = login_privcmd
    try :
        login.admins = self.moduledata['login']
    except:
        login.admins = []
        self.moduledata['login'] = login.admins
        
def terminate(self):
    """save data. called by oksanen.reset and .reload"""
    self.moduledata['login'] = login.admins

def login(self, e, c):
    """module main"""
    pass

def login_privcmd(self, e, c):
    """privcommand login"""

    nick = nm_to_n(e.source())
    line = e.arguments()[0]
    passwd = line.split()[1]
    
    """ read password from the file every time for a login req """
    fd = open(pwfile, 'r')
    for fline in fd:
        pwstring = fline.rstrip()
    fd.close()

    print "login request from %s : %s" % (nick, passwd)

    if passwd == pwstring:
        if not e.source() in login.admins:
            login.admins.append(e.source())
            print "Adding nickmask %s to admins" % (e.source())
        else:
            print "%s already in admin list." % (e.source())
        c.notice(nick,"Greetings, master.")
    else:
        print "\033[31mWARNING\033[m : failed login attempt from %s" % (e.source())
     