from Actions import keys
from Mode import Mode
from modes.Chrome import ChromeMode
import sys, os

def restartMandimus():
    sys.stdout.flush()
    sys.stderr.flush()
    python = sys.executable
    os.execl(python, python, *sys.argv)

class XMonadMode(Mode):
    def __init__(self):
        Mode.__init__(self)

    @property
    def commands(self):
        c = {
            "left" : keys("ctrl+alt+s"),
            "right" : keys("ctrl+alt+h"),
            "move left" : keys("ctrl+alt+a"),
            "move right" : keys("ctrl+alt+t"),
            "next" : keys("ctrl+alt+e"),
            "previous" : keys("ctrl+alt+o"),
            "move next" : keys("ctrl+alt+shift+e"),
            "move previous" : keys("ctrl+alt+shift+o"),
            "expand" : keys("ctrl+alt+i"),
            "shrink" : keys("ctrl+alt+n"),
            "cycle" : keys("ctrl+alt+backslash"),
            "kill window" : keys("ctrl+alt+x"),
            "make master" : keys("ctrl+alt+Return"),
            "editor" : keys("ctrl+alt+w"),
            "browser" : keys("ctrl+alt+b"),
            "new terminal" : keys("ctrl+shift+alt+t"),
            "restart window manager" : keys("ctrl+alt+q"),
            "restart mandimus" : restartMandimus
            }
        return c

    def browser(self):
        pass