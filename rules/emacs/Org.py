from Actions import Key, Repeat
from rules.ContextualRule import makeContextualRule
from requirements.Emacs import IsEmacs
from requirements.ModeRequirement import ModeRequirement
from rules.emacs.common import emacsExtras, emacsDefaults

_mapping = {
    "save link"   : Key("c-c,l"),
    "agenda menu" : Key("c-c,a"),
    "agenda"      : Key("c-c,a,a"),
    "list to do"  : Key("c-c,a,t"),
}

OrgAnywhereRule = makeContextualRule("OrgAnywhere", _mapping, emacsExtras, emacsDefaults)
OrgAnywhereRule.context.addRequirement(IsEmacs)


# "scoot" -> expand section
# "cap scoot" -> collapse all sections
# "lima" -> log view to see record for the day
_mapping = {
    "new"                     : Key("a-enter"),
    "new todo"                : Key("as-enter"),
    "make headline"           : Key("c-c,asterisk"),
    "archive [<n>]"           : Key("c-c,c-x,c-a") * Repeat(extra="n"),
    "task [<n>]"              : Key("c-c,c-t") * Repeat(extra="n"),
    "follow"                  : Key("c-c,c-o"),
    "insert link"             : Key("c-c,c-l"),
    "schedule"                : Key("c-c,c-s"),
    "increase priority [<n>]" : Key("s-up:%(n)d"),
    "decrease priority [<n>]" : Key("s-down:%(n)d"),
    "priority one"            : Key("c-c,comma,a"),
    "priority two"            : Key("c-c,comma,b"),
    "priority three"          : Key("c-c,comma,c"),
}

OrgRule = makeContextualRule("Org", _mapping, emacsExtras, emacsDefaults)
OrgRule.context.addRequirement(IsEmacs)
OrgRule.context.addRequirement(ModeRequirement(modes=["org-mode", "org-agenda-mode"]))

