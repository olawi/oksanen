#! /usr/bin/env python
# coding=utf-8
#
# Oksanen!
#

import os
try:
    import MySQLdb
    hasSql = True
except Exception, e:
    hasSql = False


"""A simple example bot.

This is an example bot that uses the SingleServerIRCBot class from
ircbot.py.  The bot enters a channel and listens for commands in
private messages and channel traffic.  Commands in channel messages
are given by prefixing the text by the bot name followed by a colon.
It also responds to DCC CHAT invitations and echos data sent in such
sessions.

The known commands are:

    stats -- Prints some channel information.

    disconnect -- Disconnect the bot.  The bot will try to reconnect
                  after 60 seconds.

    die -- Let the bot cease to exist.

    dcc -- Let the bot invite you to a DCC CHAT connection.
"""

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
import sys, imp

home = os.getcwd()

DEBUG=1

def debug(text):
    if DEBUG==1:
        print text

def is_admin(nick):
    if nick == "mossman":
        return True
    else:
        return False

class Oksanen(SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port, sqlparams):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.setup()
        print self.commands
        print self.pubhandlers

        self.nickname = nickname

        if hasSql:
            self.db = MySQLdb.connect(host=sqlparams[0], user=sqlparams[1], passwd=sqlparams[2], db = sqlparams[3])

    def setup(self):
        self.commands = {}
        self.pubhandlers = []

        filenames = []

        for fn in os.listdir(os.path.join(home, 'modules')): 
            if (fn[-2:] == "py"):
                filenames.append(os.path.join(home, 'modules', fn ))
        
        modules = []
        for filename in filenames: 
            name = os.path.basename(filename)[:-3]

            try: 
                module = imp.load_source(name, filename)
            except Exception, e: 
                print >> sys.stderr, "Error loading %s: %s (in oksanen.py)" % (name, e)
            else: 
                if hasattr(module, 'setup'): 
                    module.setup(self)

                modules.append(name)

        if modules: 
            print >> sys.stderr, 'Registered modules:', ', '.join(modules)
        else: 
            print >> sys.stderr, "Warning: Couldn't find any modules"

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments()[0])


    def on_pubmsg(self, c, e):
        for func in self.pubhandlers:
            try:
                func(self, e, c)
            except Exception, ex:
                print "ERROR: %s"%ex

        line = e.arguments()[0]
        a = line.split(":", 1)

        if line[0] == "!":
            self.do_pubcommand(e)
        return

    def on_dccmsg(self, c, e):
        c.privmsg("You said: " + e.arguments()[0])

    def on_dccchat(self, c, e):
        if len(e.arguments()) != 2:
            return
        args = e.arguments()[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, port)

    def do_pubcommand(self, e):
        nick = nm_to_n(e.source())
        c = self.connection
        
        line = e.arguments()[0]
        if line[0] == "!" and len(line)>1:
            parts = line[1:].split()
            cmd = parts[0].lower()
            try:
                func = self.commands[cmd]
                func(self, e, c)
            except Exception, e:
                print "ERROR: %s"%e

    def do_command(self, e, cmd):
        nick = nm_to_n(e.source())
        c = self.connection

        # for now
        if is_admin(nick) and cmd == "reload":
            self.setup()
            
        elif cmd == "stats":
            for chname, chobj in self.channels.items():
                c.notice(nick, "--- Channel statistics ---")
                c.notice(nick, "Channel: " + chname)
                users = chobj.users()
                users.sort()
                c.notice(nick, "Users: " + ", ".join(users))
                opers = chobj.opers()
                opers.sort()
                c.notice(nick, "Opers: " + ", ".join(opers))
                voiced = chobj.voiced()
                voiced.sort()
                c.notice(nick, "Voiced: " + ", ".join(voiced))
        else:
            c.notice(nick, "En tajua: " + cmd)

def main():
    import sys
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-s", "--server", dest="server",
                      help="server", default="irc6.datanet.ee")
    parser.add_option("-p", "--port", dest="port",
                      help="port", default="6667")
    parser.add_option("-n", "--nick", dest="nick",
                      help="nick", default="Oksanen")
    ( options, args ) = parser.parse_args()

    if len(args) != 1:
        print "Usage: oksanen -s server -p port -n nick channel"
        sys.exit(1)

    mysqlargs = []

    if hasSql:
        fd = open(".mysqlpw")
        for i in fd.readlines():
            mysqlargs.append(i.strip())
        fd.close()

    bot = Oksanen(args[0], options.nick, options.server, int(options.port), mysqlargs)
    bot.start()

if __name__ == "__main__":
    main()
