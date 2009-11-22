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


""" 
	Oksanen
	IRCBot
"""

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
import ircutil

import sys, imp
import thread
import threading
import traceback

home = os.getcwd()
sys.path.append("./modules")

DEBUG = 1

def debug(text):
    if DEBUG:
        print text

def is_admin(nick):
    if nick in ["mossman", "Olawi", "Squib"]:
        return True
    else:
        return False

class Oksanen(SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port, sqlparams):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.timer = TimerManager()
        self.setup()
        print "Modules:",self.modules
        print "Commands:",self.commands
        print "Pub Handlers:",self.pubhandlers
        print "Join Handlers:",self.joinhandlers
        print "Part Handlers:",self.parthandlers
        print "Quit Handlers:",self.quithandlers

        self.nickname = nickname

        if hasSql:
            self.db = MySQLdb.connect(host=sqlparams[0], user=sqlparams[1], passwd=sqlparams[2], db = sqlparams[3], charset = "utf8", use_unicode = True)

    def setupTimer():
        """setup timer"""
        self.timer.stop()
        self.timer.add_operation(self.on_minute, 60)
    
    def setup(self):
        """setup is also called from self.reset()"""

        self.setupTimer()
        self.modules = []
        self.moduledata =  {}
        self.whoisinfo = {}

        self.reload()

    def reset(self):
        """reset clears all module data and buffers and resets modules
        after calling self.terminate() on modules"""
        try:
            for module in self.modules:
                if hasattr(module, 'terminate'): 
                    module.terminate(self)
        except:
            print >> sys.stderr, "No running modules found, resetting.."

        self.setup()
        
    def reload(self):
        """reload calls self.terminate on all modules and reloads them"""
        
        self.commands = {}
        self.pubhandlers = []
        self.joinhandlers = []
        self.parthandlers = []
        self.quithandlers = []
        self.whoiscallbacks = []

        """call self.terminate on modules, if any"""
        try:
            for module in self.modules:
                """some modules already loaded"""
                if hasattr(module, 'terminate'):
                    module.terminate(self)
        except:
            """No modules found"""
            print >> sys.stderr, "No currently running modules, reloading..."

        """(clear and re-)load modules"""
        self.modules = []
        filenames = []

        for fn in os.listdir(os.path.join(home, 'modules')): 
            if (fn[-2:] == "py"):
                filenames.append(os.path.join(home, 'modules', fn ))
        
        modulenames = []
        for filename in filenames: 
            name = os.path.basename(filename)[:-3]

            try: 
                module = imp.load_source(name, filename)
            except Exception, e: 
                print >> sys.stderr, "\033[31mError\033[m loading %s: %s (in oksanen.py)" % (name, e)
            else: 
                if hasattr(module, 'setup'): 
                    module.setup(self)

                self.modules.append(module)
                modulenames.append(name)

        if modulenames: 
            print >> sys.stderr, 'Registered modules:', ', '.join(modulenames)
        else: 
            print >> sys.stderr, "Warning: Couldn't find any modules"

    def on_minute(self):
        print "\033[34mTime goes... (minute)\033[m"
        if (time.localtime().tm_min == 0):
            self.on_hour()
    
    def on_hour(self):
        print "\033[34mTime flyes... (hour)\033[m"

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_join(self, c , e):
        for func in self.joinhandlers:
            try:
                func(self, e, c)
            except Exception, ex:
                print "\033[31mERROR\033[m (on_join): %s"%ex
                if DEBUG > 1: traceback.print_stack()

    def on_part(self, c , e):
        for func in self.parthandlers:
            try:
                func(self, e, c)
            except Exception, ex:
                print "\033[31mERROR\033[m (on_part): %s"%ex
                if DEBUG > 1: traceback.print_stack()
                
    def on_quit(self, c , e):
        for func in self.quithandlers:
            try:
                func(self, e, c)
            except Exception, ex:
                print "\033[31mERROR\033[m (on_quit): %s"%ex
                if DEBUG > 1: traceback.print_stack()
                
    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments()[0])

    def on_pubmsg(self, c, e):

        e._arguments[0] = ircutil.recode(e._arguments[0])

        for func in self.pubhandlers:
            try:
                func(self, e, c)
            except Exception, ex:
                print "\033[31mERROR\033[m (on_pubmsg): %s"%ex
                if DEBUG > 1: traceback.print_stack()

        line = e.arguments()[0]

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

    # WHOIS
    def on_whoisuser(self, c, e):
        self.whoisinfo['user'] = e.arguments()

    def on_whoischannels(self, c, e):
        self.whoisinfo['channels'] = e.arguments()

    def on_whoisserver(self, c ,e):
        self.whoisinfo['server'] = e.arguments()

    def on_whoisidle(self, c, e):
        self.whoisinfo['idle'] = e.arguments()

    def on_endofwhois(self, c, e):
        if self.whoiscallbacks :
            try:
                func = self.whoiscallbacks.pop()
                func(self,e,c)
            except Exception, ex:
                print "\033[31mERROR\033[m (on_endofwhois): %s"%ex
                if DEBUG > 1: traceback.print_stack()

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
                print "\033[31mERROR\033[m (do_pubcommand): %s"%e
                if DEBUG > 1: traceback.print_stack()

    def do_command(self, e, cmd):
        nick = nm_to_n(e.source())
        c = self.connection

        e._arguments[0] = ircutil.recode(e._arguments[0])
        line = e.arguments()[0]

        if is_admin(nick) and cmd == "reset":
            print >> sys.stderr, "cmd: RESET modules"
            self.reset()
            c.notice(nick, cmd)
            
        elif is_admin(nick) and cmd == "reload":
            print >> sys.stderr, "cmd: RELOAD modules"
            self.reload()
            c.notice(nick, cmd)
            
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

        elif is_admin(nick) and line[0] == "!" and len(line) > 1:
            parts = line[1:].split()
            cmd = parts[0].lower()
            try:
                func = self.commands[cmd]
                """query source -> target"""
                e._target = e.source()
                func(self, e, c)
            except Exception, e:
                print "\033[31mERROR\033[m (do_command): %s"%e
                if DEBUG > 1: traceback.print_stack()

        else:
            c.notice(nick, "En tajua: " + cmd)

class TimerOperation(threading._Timer):
    def __init__(self, *args, **kwargs):
        threading._Timer.__init__(self, *args, **kwargs)
        self.setDaemon(True)

    def run(self):
        while True:
            self.finished.clear()
            self.finished.wait(self.interval)
            if not self.finished.isSet():
                try:
                    self.function(*self.args, **self.kwargs)
                except Exception, e:
                    print "\033[31mERROR\033[m (timer): %s"%e
                    if DEBUG > 1: traceback.print_stack()
            else:
                return
            self.finished.set()

class TimerManager(object):

    ops = []

    def add_operation(self, operation, interval, args=[], kwargs={}):
        op = Operation(interval, operation, args, kwargs)
        self.ops.append(op)
        thread.start_new_thread(op.run, ())

    def stop(self):
        for op in self.ops:
            op.cancel()
        self.ops = []

class Chronograph(object):
    crontab = []
    
    def add_event(self,eventstring):
        crontab.append(split(eventstring))
        
    def delete_event(self,methodname):
        print "yeah"
        
    def reset(self):
        crontab = []
    
        
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
