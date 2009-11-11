#!/usr/bin/env python
# coding=utf-8

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad

def logo(self, e, c):
    nick = nm_to_n(e.source())
    c = self.connection

    line = e.arguments()[0]
    target = "".join(line.split()[1:])
    print target
    if target == "lehma" or target == "lehmä":
        c.privmsg(e.target(), "         (__)")
        c.privmsg(e.target(), "         (oo)")
        c.privmsg(e.target(), "  /-------\\/")
        c.privmsg(e.target(), " / |     ||"  )
        c.privmsg(e.target(), "*  ||----||")
        c.privmsg(e.target(), "   ^^    ^^")


logo.commands = ['logo']
