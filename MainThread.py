import os, sys
from dfly_server import DragonflyThread
from Actions import Key, Text, Camel, Underscore, Hyphen, Speak, SelectWindow
from DragonflyNode import ConnectedEvent
from WindowEventWatcher import WindowEventWatcher, FocusChangeEvent, WindowListEvent
from Window import Window
from wordUtils import extractWords, buildSelectMapping
import EventLoop
import re
import time
from Events import GrammarEvent

from rules.Rule import registerRule, registeredRules
from rules.SeriesMappingRule import SeriesMappingRule
from rules.MappingRule import MappingRule
from rules.Elements import Integer, Dictation

badWindows = {
    "Desktop",
    ".*Edge Panel.*",
    "gnome-screensaver",
    "Panel",
    "$^", # empty string
}

def filterWindows(w):
    # filter out known bad names
    for bad in badWindows:
        if re.search(bad, w.name) is not None:
            return False

    # filter out windows that don't have
    # icons set. typically these only exist
    # as an artifact of dealing with X
    if not w.hasIcon:
        return False

    return True

spokenWindowRules = set()
def spokenWindowRule(f):
    global spokenWindowRules
    spokenWindowRules.add(f)
    return f

@spokenWindowRule
def weechat(w):
    if "terminal" in w.wmclass.lower() and "weechat" in w.name:
        return ["we", "chat"]
    return []
    
# so write rules for specific window types
# and then fall back to generic word search
# grammar only when the windows aren't special
# cased?

class RestartEvent(object): pass
class ExitEvent(object): pass

class TimerEntry(object):
    def __init__(self, nextExpiration, callback, seconds):
        self.nextExpiration = nextExpiration
        self.callback = callback
        self.seconds = seconds

class MainThread(object):
    def __init__(self):
        # this needs to run before any user modes are imported
        self.timers = []
        EventLoop.event_loop = self        

        self.dfly = DragonflyThread(('', 23133), self)
        self.win = WindowEventWatcher(self, filterWindows)
        self.run = True
        
        self.events = []

    def subscribeTimer(self, seconds, cb):
        self.timers.append(TimerEntry(time.time() + seconds, cb, seconds))

    def timeout(self):
        if self.timers:
            nextTimer = min(self.timers, key=lambda x: x.nextExpiration)
            nextExpiration = nextTimer.nextExpiration
        else:
            # without a timeout, ctrl-c doesn't work because.. python
            ONEYEAR = 365 * 24 * 60 * 60
            nextExpiration = time.time() + ONEYEAR 
        return max(nextExpiration - time.time(), 0)

    def dispatchTimers(self):
        now = time.time()
        for t in self.timers:
            if now >= t.nextExpiration:
                t.nextExpiration = now + t.seconds
                t.callback()
    
    def determineRules(self, window):
        for r in registeredRules():
            if r.activeForWindow(window):
                self.dfly.loadGrammar(r)
            else:
                self.dfly.unloadGrammar(r)

    def loadRule(self):
        self.dfly.loadGrammar(WindowRule)

    def put(self, p):
        self.events += [p]

    def __call__(self):
        class MainRule(SeriesMappingRule):
            mapping = { "restart mandimus" : (lambda x: self.put(RestartEvent())),
                        "completely exit mandimus" : (lambda x: self.put(ExitEvent())) }

        try:
            while self.run:
                time.sleep(self.timeout())
                
                self.dispatchTimers()

                try:
                    ev = self.events.pop()
                except IndexError:
                    continue

                if isinstance(ev, ConnectedEvent):
                    self.dfly.loadGrammar(MainRule)

                    # so that rules apply for whatever is focused on startup
                    self.determineRules(Window(winId=Window.FOCUSED))
                elif isinstance(ev, RestartEvent):
                    self.restart()
                elif isinstance(ev, ExitEvent):
                    self.stop()
                    return
                elif isinstance(ev, FocusChangeEvent):
                    self.determineRules(ev.window)
                elif isinstance(ev, WindowListEvent):
                    self.handleWindowList(ev)
                elif isinstance(ev, GrammarEvent):
                    self.handleGrammarEvent(ev)
        except KeyboardInterrupt:
            self.stop()
            sys.exit()

    def handleGrammarEvent(self, ev):
        if ev.load:
            self.dfly.loadGrammar(ev.grammar)
        else:
            self.dfly.unloadGrammar(ev.grammar)

    def handleWindowList(self, ev):
        # sometimes at startup list is empty
        if not ev.windows:
            return

        spokenWindows = {}
        for w in ev.windows:
            global spokenWindowRules
            spokenForms = []
            for rule in spokenWindowRules:
                spokenForms = rule(w)
                if spokenForms != []:
                    spokenForms = [set(spokenForms)]
                    break

            if spokenForms == []:
                # thought about using name instead of wmclass,
                # but the title tends to contain debris like
                # the name of the currently opened document/page
                nameset = extractWords(w.name)
                classset = extractWords(w.wmclass)
                spokenForms = [nameset, classset]

            spokenWindows[w] = spokenForms

        # remove empty sets
        for w, spokenForms in spokenWindows.items():
            try:
                spokenForms.remove(set())
            except ValueError:
                pass # python is stupid
            try:
                spokenForms.remove(set(u''))
            except ValueError:
                pass # python is stupid
        # remove windows that map to no forms
        spokenWindows = dict((k, v) for k, v in spokenWindows.iteritems() if v)

        omapping = buildSelectMapping('win', spokenWindows, SelectWindow)

        class WindowRule(MappingRule):
            mapping = omapping
            
        self.dfly.loadGrammar(WindowRule)        

    def stop(self):
        self.run = False
        self.dfly.cleanup()

    def restart(self):
        self.stop()
        sys.stdout.flush()
        sys.stderr.flush()
        python = sys.executable
        os.execl(python, python, *sys.argv)        

if __name__ == "__main__":
    main = MainThread()
    
    from rules.Always import AlwaysRule
    from rules.Emacs import EmacsRule
    from rules.XMonad import XMonadRule
    from rules.CUA import CUARule
    from rules.Chrome import ChromeRule

    main()
