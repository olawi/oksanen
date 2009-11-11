#! /usr/bin/env python
# coding=utf-8
#
# Oksanen!
#

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

DEBUG=1

def debug(text):
    if DEBUG==1:
        print text

class Oksanen(SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments()[0])

    def on_pubmsg(self, c, e):
        a = e.arguments()[0].split(":", 1)
        if e.arguments()[0][0] == "!":
            self.do_pubcommand(e)
        elif len(a) > 1 and irc_lower(a[0]) == irc_lower(self.connection.get_nickname()):
            self.do_command(e, a[1].strip())
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
        if line[0] == "!":
            parts = line[1:].split()
# Make modular
            if parts[0].lower() == "nussi":
                c.privmsg(e.target(), r"%s: Joojoo eläpä rupia"%nick)


    def do_command(self, e, cmd):
        nick = nm_to_n(e.source())
        c = self.connection

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
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
        elif cmd == "dcc":
            dcc = self.dcc_listen()
            c.ctcp("DCC", nick, "CHAT chat %s %d" % (
                ip_quad_to_numstr(dcc.localaddress),
                dcc.localport))
        else:
            c.notice(nick, "Not understood: " + cmd)

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

        
    bot = Oksanen(args[0], options.nick, options.server, int(options.port))
    bot.start()

if __name__ == "__main__":
    main()
