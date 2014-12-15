import mdlog
log = mdlog.getLogger(__name__)

from Actions import Key, Text, SelectChoice
from EventLoop import getLoop
from EventList import FocusChangeEvent
from rules.Elements import Dictation, Integer
from rules.SeriesMappingRule import SeriesMappingRule
from rules.emacs.Emacs import Emacs
from rules.emacs.Cmd import runEmacsCmd, Cmd
from rules.Rule import registerRule
from rules.emacs.grammar import updateListGrammar, getStringList
from rules.emacs.Text import EmacsText
from wordUtils import extractWords
from Window import getFocusedWindow
from rules.emacs.Base import EmacsBase

@registerRule
class Term(EmacsBase):
    majorMode = "term-mode"

    mapping = {
        "line mode" : Key("c-c,c-j"),
        "care mode" : Key("c-c,c-k"),
    }

