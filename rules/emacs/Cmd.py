import mdlog
log = mdlog.getLogger(__name__)
log.setLevel(20)

import traceback
import os, fcntl
import os.path as op
import subprocess

from Actions import Action, Key, Text
import EventLoop
from EventLoop import getLoop
from EventList import FocusChangeEvent, EmacsConnectedEvent
import grammar
import rules.BaseRules as BaseRules
import socket
import errno
from Window import getFocusedWindow

EMACSCLIENT = "timeout 5 emacsclient" # timeout so we don't get stuck blocking
alternative = op.join(os.getenv("HOME"), "opt/bin/emacsclient")
log.info(alternative)
if op.exists(alternative):
    EMACSCLIENT = alternative

logCommands = False
def toggleCommandLogging(*args):
    global logCommands
    logCommands = not logCommands

class CommandClient(object):
    EMACS_TIMEOUT = 5
    
    def __init__(self):
        self.sock = None
        self.sock = self.makeSocket()

    def makeSocket(self):
        if self.sock:
            self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        fd = self.sock.fileno()
        old_flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        fcntl.fcntl(fd, fcntl.F_SETFD, old_flags | fcntl.FD_CLOEXEC)

    def tryConnect(self):
        if not self.sock:
            self.makeSocket()

        self.sock.settimeout(0.05)
        try:
            self.sock.connect(("localhost", 23233))
            log.info("Connected to emacs!")
            getLoop().put(EmacsConnectedEvent())
            return True
        except socket.error as e:
            log.error("Error connecting to emacs: %s" % e)
        except socket.timeout as e:
            log.error("Connection to emacs timed out.")
        return False

    def dumpOther(self):
        self.sock.close()
        self.sock = None

    def sendMsg(self, msg):
        try:
            self.sock.settimeout(self.EMACS_TIMEOUT)
            try:
                self.sock.sendall((msg + "\n").encode('utf-8'))
                return True
            except UnicodeDecodeError as e:
                log.error(str(e))
                return False
        except socket.error as e:
            log.info("Socket error while sending: %s" % e)
            if e.errno == errno.EPIPE or e.errno == errno.EBADF:
                self.dumpOther()
                return False
            else:
                raise
        except Exception as e:
            log.info("Unknown error while sending: %s" % e)
            self.dumpOther()
            raise

    def recvMsg(self):
        self.sock.settimeout(self.EMACS_TIMEOUT)
        out = ""

        newData = None
        try:
            while "\n" not in out:
                # print "in recv loop"
                newData = self.sock.recv(4096)
                out += newData
                # out += unicode(self.sock.recv(4096), 'utf-8')
        except socket.timeout as e:
            log.info("Emacs socket timeout.")
            self.dumpOther()
            return False
        except socket.error as e:
            log.info("Emacs socket error while receiving: %s" % e)
            if e.errno == errno.EPIPE or e.errno == errno.EBADF:
                self.dumpOther()
                return False
            else:
                raise
        except Exception as e:
            log.info("Unknown error while receiving: %s" % e)
            log.info("New data dump: [%s]" % newData)
            self.dumpOther()
            raise
            
        out = out.decode('utf-8')
        return out

    def runCmd(self, command, inFrame=True, dolog=False, allowError=False, queryOnly=True):
        """Run command optionally in particular frame,
        set True for active frame."""

        if command is None:
            raise Exception("Command must be a string.")

        if not self.sock:
            if not self.tryConnect():
                log.error("Can't run command, not connected: [%s]" % command)
                return "nil"

        wrapper = [u"{}"]

        if allowError:
            wrapper += [u'(condition-case err {} (error nil))']

        if inFrame:
            wrapper += [u'(with-current-buffer (window-buffer (if (window-minibuffer-p) (active-minibuffer-window) (selected-window))) {})']

        # See elisp function's documentation
        if not queryOnly:
            wrapper += [u'(let ((result {})) (md-generate-noop-input-event) result)']

        for w in reversed(wrapper):
            command = w.format(command)
            
        # have to delete newlines since they're the protocol delimeter
        command = command.replace("\n", "")

        if dolog or logCommands:
            log.info('emacs cmd: ' + command)

        self.sock.settimeout(None)
        if not self.sendMsg(command):
            log.info("Couldn't send message: [%s]" % command)
            return "nil"

        out = self.recvMsg().rstrip()
        
        if dolog or logCommands:
            log.info('emacs output: [%s]' % out)
        return out

clientInst = CommandClient()

def runEmacsCmd(command, inFrame=True, dolog=False, allowError=False, queryOnly=True):
    global clientInst
    return clientInst.runCmd(command, inFrame, dolog, allowError, queryOnly)

class Minibuf(Action):
    def __call__(self, extras={}):
#        Key("a-x")()
        Key("c-c,m,x")() # guaranteed to not use helm
        Text(self.data % extras)()
        Key("enter")()

class Cmd(Action):
    classLog = False
    
    def __init__(self, data=None, log=False, queryOnly=False):
        Action.__init__(self, data)
        self.log = log
        self.queryOnly = queryOnly
        # self.log = True
    
    def _fillData(self, extras):
        """Normally extras contains the full structure of the tree,
        but to make it so you can write self.data more succintly
        we substitute in the \"words\" for each entry in the
        extras dictionary that has one."""
        e = {k : (" ".join(v["words"])
                  if type(v) == dict and "words" in v else v) for k, v in extras.items()}
        return self.data % e

    def _lisp(self, extras):
        return self._fillData(extras)

    def _repetitions(self, extras={}):
        repeat = max(extras['n'] if 'n' in extras else 0,
                     extras['i'] if 'i' in extras else 0,
                     1)
        return repeat

    def __call__(self, extras={}):
        code = self._lisp(extras)
        if code is None:
            if self.log or self.classLog:
                log.info("%s no lisp code" % (type(self).__name__))
            return
        if self.log or self.classLog:
            log.info("%s lisp code: [%s]" % (type(self).__name__, code))
            
        for i in range(self._repetitions(extras)):
            runEmacsCmd(code, dolog=(self.log or self.classLog), queryOnly=self.queryOnly)

class CharCmd(Cmd):
    classLog = False
    def _lisp(self, extras={}):
        char = BaseRules.lookup(extras["charrule"])
        char = emacsChar(char)
        return self.data % char

class InsertString(Cmd):
    def __init__(self, stringReturningElisp):
        data = "(md-insert-text %s nil nil)" % stringReturningElisp
        Cmd.__init__(self, data)

def emacsChar(char):
    c = ["?"]
    # most characters don't need escaping, but some do
    if char in " \n\t()\\|;'`\"#.,\a\b\f\r":
        c.append("\\")
    c.append(char)
    return "".join(c)

getCommandsEl = """
(let ((y '()))
  (mapatoms 
   (lambda (x)
     (and (fboundp x)                    ; does x name a function?
	  (commandp (symbol-function x)) ; is it interactive?
	  (setq y (cons (symbol-name x) y))))) y)
"""

# TODO: this ended up being harder than I thought!
# there are over 1000 unique words in the list, so natlink
# complains that the grammar is too complex. I don't know
# where the threshold is but it will be hard to trim, may
# just need to go with a manual list, or some categories
# like anything with 'python' in the name, maybe have
# a separate "python command" vs. "buffer command" etc.
# for pulling out subsets...
def updateCommandGrammar():
    pass
    # commandlist = getStringList(runEmacsCmd(getCommandsEl))
    # all_words = set()
    # for c in commandlist:
    #     all_words.update(extractWords(c))
    # grammar = []
    # for reps in range(1):
    #     grammar += ['[(']
    #     grammar += ['|'.join(all_words)]
    #     grammar += [')]']
    #     grammar += [' ']
    # updateListGrammar(commandlist, 'command', set(),
    #                   SelectCommand, "EmacsCommandMapping")
            

