import mdlog
log = mdlog.getLogger(__name__)
from rules.emacs.Cmd import runEmacsCmd 
from rules.WordSelector import WordSelector
from rules.emacs.EmacsEventGenerator import EmacsEventGenerator
from requirements.ModeRequirement import ModeRequirement
from wordUtils import extractWords
from EventLoop import getLoop
from EventList import NickEvent
from requirements.Emacs import IsEmacs
from Actions import Key
from rules.emacs.Text import EmacsText

nickListGen = EmacsEventGenerator("Nick", "md-active-erc-nicknames", NickEvent)

class NickNames(WordSelector):
    def __init__(self, name, cmdWord):
        WordSelector.__init__(self, name, cmdWord, allowNoChoice=False)
        self.rule.context.addRequirement(IsEmacs)
        self.rule.context.addRequirement(ModeRequirement(modes="erc-mode"))
        getLoop().subscribeEvent(NickEvent, self._onNickList)

    def _onNickList(self, ev):
        self._update(ev.choices)

    def _select(self, cmd, choice):
        if runEmacsCmd("(md-at-start-of-erc-input-line)") == 't':
            # we're addressing them, include the colon
            EmacsText("%s: " % choice, lower=False, capitalCheck=False)()
        else:
            # we're referring to them, omit the colon
            EmacsText("%s" % choice, lower=False, capitalCheck=False)()

    def _extractWords(self, n):
        x = extractWords(n)
        log.info("[%s] extracted words [%s] [%s]" % (type(self).__name__, n, x))
        return x

    # def _extractWords(self, w):
    #     return extractWords(w)
    #     # return extractWords(w, translate={},
    #     #                     useDict=True,
    #     #                     #detectBadConsonantPairs=True,
    #     #                     removeLeetSpeak=True)


_nickNameSelector = NickNames("NickNames", "nick")
