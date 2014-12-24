import mdlog
log = mdlog.getLogger(__name__)

import grammar
from rules.emacs.Base import EmacsBase
import EventLoop  
import EventList
from EventList import FocusChangeEvent
from rules.emacs.Cmd import runEmacsCmd 
from Window import getFocusedWindow
from listHelpers import deCamelize
from rules.Rule import registerRule
from rules.ruleUtil import buildRuleClass
from rules.MappingRule import MappingRule

class EmacsCommandWatcher(object):
    cmd = None
    allowError = False
    inFrame = True
    eventType = None
    interval = 1
    onTimer = True
    onFocus = True
    registeredLogPhrase = set()
    logCommands = False
    allEnabledLog = False
    enabled = True
    allEnabled = True
    
    def __init__(self):
        self.output = None
        if self.onTimer:
            EventLoop.getLoop().subscribeTimer(self.interval, self.update, priority=0)
        if self.onFocus:
            EventLoop.getLoop().subscribeEvent(FocusChangeEvent, self.update, priority=0)

        name = type(self).__name__
        if not name in self.registeredLogPhrase:
            phrase = ' '.join(deCamelize(name))
            mapping = {
                ("toggle logging %s" % phrase) : (lambda x: type(self).toggleLogging()), 
                ("toggle %s" % phrase) : (lambda x: type(self).toggleEnabled()),
            }
            logrule = buildRuleClass(name + "LogToggle", lambda x: True, mapping)
            self.registeredLogPhrase.add(name)
            registerRule(logrule)

    def _postProcess(self, output):
        lst = grammar.getStringList(output)
        lst.sort()
        return lst

    def update(self, ev=None):
        if not self.enabled or not self.allEnabled:
            return
        
        window = ev.window if ev else getFocusedWindow()
        if self._contextMatch(window):
            log.debug(self.cmd)
            newOutput = runEmacsCmd(self.cmd, inFrame=self.inFrame,
                                    allowError=self.allowError,
                                    dolog=(self.logCommands or self.allEnabledLog))
            newOutput = self._postProcess(newOutput)
        else:
            newOutput = "nil"

        if newOutput == self.output:
            return
        self.output = newOutput
        EventLoop.getLoop().put(self.eventType(newOutput))

    def _contextMatch(self, window):
        return window and EmacsBase.activeForWindow(window)

    @classmethod
    def toggleAllWatchers(log):
       cls.allEnabled = not cls.allEnabled
       cls.info("Setting all watchers to: %s" % cls.allEnabled)

    @classmethod
    def toggleAllWatchersLogging(cls):
       cls.allEnabledLog = not cls.allEnabledLog
       log.info("Setting all watchers logging to: %s" % cls.allEnabled)

    @classmethod
    def toggleLogging(cls):
        cls.logCommands = not cls.logCommands
        log.info("Setting %s watcher logging to: %s" % (cls.__name__, cls.allEnabled))

    @classmethod
    def toggleEnabled(cls):
        cls.enabled = not cls.enabled
        log.info("Setting %s watcher to: %s" % (cls.__name__, cls.allEnabled))
        
@registerRule
class ToggleAllWatchers(MappingRule):
    mapping = {
        "toggle all watchers" : (lambda x: EmacsCommandWatcher.toggleAllWatchers()),
        "toggle logging all watchers" : (lambda x: EmacsCommandWatcher.toggleAllWatchersLogging()),
    }

    def activeForWindow(self, w):
        return True