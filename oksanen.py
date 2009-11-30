#! /usr/bin/env python
# coding=utf-8
#
# Oksanen!
#

import os
try:
    import MySQLdb
    hasSql = True
except Exception, ex:
    hasSql = False


""" 
	Oksanen
	IRCBot
"""

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, nm_to_uh, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
import ircutil

import sys, imp
import thread
import threading
import traceback
import datetime
import re

home = os.getcwd()
sys.path.append("./modules")

DEBUG = 1

if hasSql: 
    G_SQL_PARAMS = {'charset':'utf8',
                    'use_unicode':True}
def debug(text):
    if DEBUG:
        print text

def is_admin(source):
    if nm_to_uh(source) in ["~antti@193.65.182.140",
                            "~ppietari@tuomi.oulu.fi",
                            "m7kejo00@rhea.oamk.fi"]:
        return True
    else:
        return False
    
class Oksanen(SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port, sqlparams):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.nickname = nickname
        self.timer = TimerManager()
        self.cron = Chronograph()
        self.setup()
        print "\033[33mself.modules : \033[m",self.modules
        print "\033[33mself.pubcommands : \033[m",self.pubcommands
        print "\033[33mself.repubhandlers : \033[m",self.repubhandlers
        print "\033[33mself.pubhandlers : \033[m",self.pubhandlers
        print "\033[33mself.joinhandlers : \033[m",self.joinhandlers
        print "\033[33mself.kickhandlers : \033[m",self.kickhandlers
        print "\033[33mself.parthandlers : \033[m",self.parthandlers
        print "\033[33mself.quithandlers : \033[m",self.quithandlers

        if hasSql:
            sql_login = dict(zip(['host', 'user', 'passwd', 'db'], sqlparams[:]))
            G_SQL_PARAMS.update(sql_login)
            self.db = MySQLdb.connect(**G_SQL_PARAMS)

        print "%s ready to roll! Joining %s in %s" % (self.nickname, self.channel, server)

    def setupTimer(self):
        """setup timer"""
        self.timer.stop()
        self.timer.add_operation(self.on_minute, 60)
    
    def setup(self):
        """setup is also called from self.reset()"""

        self.setupTimer()
        self.modules = []
        self.moduledata =  {}
        self.whoisinfo = {}
        self.cron.reset()

        self.reload()

    def reset(self):
        """reset clears all module data and buffers and resets modules
        after calling self.terminate() on modules.
        Also resets self.db connection
        """
        try:
            for module in self.modules:
                if hasattr(module, 'terminate'): 
                    module.terminate(self)
        except:
            print >> sys.stderr, "No running modules found, resetting.."

        self.reset_db()
        self.setup()        

    def reset_db(self):
        """closes and reconnects to DB"""
        if hasSql:
            try:
                self.db.close()
                self.db = None
            except Exception, ex:
                print >> sys.stderr, "\033[31mError\033[m (reset) on closing DB: %s"%ex
            try:
                self.db = MySQLdb.connect(**G_SQL_PARAMS)
            except Exception, ex:
                print >> sys.stderr, "\033[31mError\033[m (reset) on opening DB: %s"%ex
                
    def reload(self):
        """reload calls self.terminate on all modules and reloads them"""
        
        self.pubcommands = {}
        self.privcommands = {}
        self.pubhandlers = []
        self.repubhandlers = {}
        self.joinhandlers = []
        self.parthandlers = []
        self.quithandlers = []
        self.kickhandlers = []
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
            except Exception, ex: 
                print >> sys.stderr, "\033[31mError\033[m loading %s: %s (in oksanen.py)" % (name, ex)
            else:
                try:
                    if hasattr(module, 'setup'): 
                        module.setup(self)

                        self.modules.append(module)
                        modulenames.append(name)
                except Exception, ex:
                    print >> sys.stderr, "\033[31mError\033[m in setup" % name

        if modulenames: 
            print >> sys.stderr, '\033[33mRegistered modules:\033[m', ', '.join(modulenames)
        else: 
            print >> sys.stderr, "Warning: Couldn't find any modules"

    def on_minute(self):
        current_time = datetime.datetime.today()
        
        print "\033[34mon_minute: (%02d:%02d)\033[m" %(current_time.hour,current_time.minute)
        for event in self.cron.get_events(current_time):
            try:
                func = event['cmd']
                func(*event['args'], **event['kwargs'])
                """decrement counter"""
                self.cron.done(event)
            except Exception, ex:
                print "\033[31mERROR\033[m (on_minute): %s"%ex
                if DEBUG > 1: traceback.print_stack()
 

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

    def on_kick(self, c , e):
        for func in self.kickhandlers:
            try:
                func(self, e, c)
            except Exception, ex:
                print "\033[31mERROR\033[m (on_kick): %s"%ex
                if DEBUG > 1: traceback.print_stack()
                
    def on_quit(self, c , e):
        for func in self.quithandlers:
            try:
                func(self, e, c)
            except Exception, ex:
                print "\033[31mERROR\033[m (on_quit): %s"%ex
                if DEBUG > 1: traceback.print_stack()

    def on_topic(self, c, e):
        nick = nm_to_n(e.source())
        entry = ircutil.recode(e._arguments[0])
        if hasSql:
            try:
                cursor = self.db.cursor()
                cursor.execute("""INSERT INTO topic (entry, nick) VALUES (%s, %s)""", [entry, nick])
            except Exception, ex:
                print "\033[31mERROR\033[m (on_topic): %s"%ex
                if DEBUG > 1: traceback.print_stack()

    def on_privmsg(self, c, e):

        e._arguments[0] = ircutil.recode(e._arguments[0])
        self.do_command(e, e.arguments()[0])

    def on_pubmsg(self, c, e):

        e._arguments[0] = ircutil.recode(e._arguments[0])

        for regex in self.repubhandlers.keys():
            """repubhanlers is a dict with {regexp, function} as key, value.
            the function will not be called unless the regexp matches."""
            if re.search(regex, e.arguments()[0]):
                try:
                     self.repubhandlers[regex](self, e, c)
                except Exception, ex:
                    print "\033[31mERROR\033[m (on_pubmsg): %s"%ex
                    if DEBUG > 1: traceback.print_stack()
                    
        for func in self.pubhandlers:
            try:
                func(self, e, c)
            except Exception, ex:
                print "\033[31mERROR\033[m (on_pubmsg): %s"%ex
                if DEBUG > 1: traceback.print_stack()

        line = e.arguments()[0]

        if line.startswith("!"):
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
                func = self.pubcommands[cmd]
                ircutil.run_once(0, func, [self, e, c])
            except Exception, ex:
                print "\033[31mERROR\033[m (do_pubcommand): %s"%ex
                if DEBUG > 1: traceback.print_stack()

    def do_command(self, e, cmd):
        nick = nm_to_n(e.source())
        c = self.connection

        line = e.arguments()[0]

        """privcommands"""
        if line.startswith("!") and len(line) > 1:
            parts = line[1:].split()
            cmd = parts[0].lower()
            try:
                func = self.privcommands[cmd]
                ircutil.run_once(0, func, [self, e, c])
            except Exception, ex:
                print "\033[31mERROR\033[m (do_command): %s"%ex
                if DEBUG > 1: traceback.print_stack()

        """The rest is admin shit"""
        if not is_admin(e.source()):
            return
        
        if cmd == "reset":
            print >> sys.stderr, "cmd: RESET modules"
            self.reset()
            c.notice(nick, cmd)

        elif cmd == "reload":
            print >> sys.stderr, "cmd: RELOAD modules"
            self.reload()
            c.notice(nick, cmd)

        elif cmd == "reset_db":
            print >> sys.stderr, "cmd: RESET database"
            self.reset_db()
            c.notice(nick, cmd)
                        
        elif cmd.startswith("raw "):
            print >> sys.stderr, "cmd: %s"%cmd
            s = re.sub('^raw ','',cmd)
            try:
                c.send_raw(s)
            except Exception, ex:
                print "\033[31mERROR\033[m (do_command): %s"%ex
                if DEBUG > 1: traceback.print_stack()
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

        elif line.startswith("!") and len(line) > 1:
            """do pubcommands in private for admins"""
            parts = line[1:].split()
            cmd = parts[0].lower()
            try:
                func = self.pubcommands[cmd]
                """query source -> target"""
                e._target = e.source()
                ircutil.run_once(0, func, [self, e, c])
            except Exception, ex:
                print "\033[31mERROR\033[m (do_command): %s"%ex
                if DEBUG > 1: traceback.print_stack()

        else:
            c.notice(nick, "Wut, sir? : " + cmd)

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
                except Exception, ex:
                    print "\033[31mERROR\033[m (timer): %s"%ex
                    if DEBUG > 1: traceback.print_stack()
            else:
                return
            self.finished.set()

class TimerManager(object):

    ops = []

    def add_operation(self, operation, interval, args=[], kwargs={}):
        op = TimerOperation(interval, operation, args, kwargs)
        self.ops.append(op)
        thread.start_new_thread(op.run, ())

    def stop(self):
        for op in self.ops:
            op.cancel()
        self.ops = []

class Chronograph(object):
    """
    A Chronograph event added by add_event contains a dict corresponging to
    datetime.datetime data: attrs (year, month, day, hour, minute) + function
    datetime.weekday() are supported with tolerance of one minute. For
    better resolution, use your own timer.

    Example : add_event({'hour': 21, 'minute':[00,30]}, foo, arg1, arg2)
    will fire the function foo every day at approximately 21:00 and 21:30.

    If the input dictionary has an entry 'count', it will be decremented
    after every time the event is fired and the element removed when 'count'
    reaches zero.
    """
    crontab = []
    id = 0

    def add_event(self, timed, cmd, *args, **kwargs):
        cron_entry = {}        
        cron_entry['id'] = self.id
        cron_entry['timed'] = timed
        cron_entry['cmd'] = cmd
        cron_entry['args'] = args
        cron_entry['kwargs'] = kwargs
        if DEBUG:
            print "cron.add_event adding event #%d"%self.id
            print repr(cron_entry)
        self.crontab.append(cron_entry)
        self.id += 1
        return (self.id-1)

    def delete_event(self, idx):
        for event in self.crontab:
            if event['id'] == idx:
                if DEBUG:
                    print "cron.delete_event removing event #%d"%idx
                self.crontab.pop(self.crontab.index(event))
                if DEBUG > 1:
                    print repr(self.crontab)
                return True
        return False

    def get_events(self, checktime):
        commandlist = []
        
        for event in self.crontab:
            rejected = False
            for k in event['timed'].keys():
                if hasattr(checktime,k):
                    if not getattr(checktime,k) in event['timed'][k]:
                        rejected = True
                elif k == 'weekday' and checktime.weekday() not in event['timed'][k]:
                    rejected = True
            if not rejected:
                commandlist.append(event)
            
        return commandlist

    def done(self, event):
        """called always after the event has been fired successfully"""
        if 'count' in event['timed']:
            try:
                event['timed']['count'] -= 1
                if DEBUG:
                    print "cron.done: event #%d" % event['id']
                    print repr(event)
                if event['timed']['count'] < 1:
                    self.delete_event(event['id'])
            except Exception, ex:
                print "\033[31mERROR\033[m (cron.done): %s"%ex
                if DEBUG > 1: traceback.print_stack()
        else:
            """not much else so far"""
            if DEBUG:
                print "cron.done: event #%d" % event['id']
                print repr(event)
                
    def reset(self):
        self.crontab = []
        self.id = 0    
        
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
