import mdlog
log = mdlog.getLogger(__name__)

from EventLoop import getLoop
from EventList import FocusChangeEvent, WindowListEvent
from Window import Window, getWindowList, getFocusedWindow
from namedtuple import namedtuple
from copy import copy
import time
import re

REFRESH_TIME = 0.25

class WindowEventWatcher(object):
    def __init__(self, eventQ, filterFunc=lambda x: False):
        self.filterFunc = filterFunc
        self.pushQ = eventQ

        self.previousWindowId = None
        self.previousWindowName = None
        self.nextWindowList = getWindowList()
        self.previousWindowList = []

        # this is still too much of a perf hog, need real poll
        getLoop().subscribeTimer(REFRESH_TIME, self)

    def extractList(self, windowList):
        return [(w.winId, w.name) for w in windowList]

    def getEvents(self):
        events = []
        windowList = self.nextWindowList.result # force finishing        

        for window in windowList:
            if time.time() - window.lastXpropTime > REFRESH_TIME:
                window.refreshInfo()        

        # we only do filtering after refreshing, because otherwise
        # once a window is filtered it will stay filtered forever
        windowList = filter(self.filterFunc, windowList)

        newWindowList = self.extractList(windowList)
        if self.previousWindowList != newWindowList:
            events.append(WindowListEvent(windowList))
        self.previousWindowList = newWindowList

        newWindow = getFocusedWindow()
        newWindowId = newWindow.winId if newWindow else -1
        newWindowName = newWindow.name if newWindow else ""
        if self.previousWindowId != newWindowId or self.previousWindowName != newWindowName:
            events.append(FocusChangeEvent(newWindow))
        self.previousWindowId = newWindowId
        self.previousWindowName = newWindowName

        self.nextWindowList = getWindowList() # start async
        return events

    def __call__(self):
        for e in self.getEvents():
            self.pushQ.put(e)
        
if __name__ == "__main__":
    import sys
    import Queue

    q = Queue.Queue()
    sub = WindowEventWatcher(q, {".*Panel.*"})
    try:
        while True:
            # without a timeout, ctrl-c doesn't work because.. python
            ONEYEAR = 365 * 24 * 60 * 60
            ev = q.get(True, ONEYEAR)

            if isinstance(ev, WindowListEvent):
                print [w.name for w in ev.windows if w.name != '']
            else:
                print str(ev)
    except KeyboardInterrupt:
        sub.stop()
        sys.exit()
    
