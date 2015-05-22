from Actions import Key, Repeat
from rules.ContextualRule import makeContextualRule
from requirements.Emacs import IsEmacs
from requirements.ModeRequirement import ModeRequirement
from rules.emacs.common import emacsExtras, emacsDefaults
from rules.emacs.Cmd import Cmd
from rules.emacs.Keywords import KeywordRule
from rules.emacs.Text import EmacsText

_keywords = [
    ["awk", "ock"],
    "cat",
    ["cd", "CD"],
    #["cd", "see D"],
    ["cp", "copy"],
    "cut",
    "date",
    ["/dev/null", "dev null"],
    "diff",
    "disown",
    "do",
    "done",
    "echo",
    "else",
    "env",
    "exec",
    "exit",
    "export",
    "false",
    ["fi", "fee"],
    "find",
    "force",
    ["g++", "G plus plus"],
    ["gcc", "GCC"],
    "git",
    "git rebase",
    "git pull",
    "git push",
    "grep",
    ["--help", "help"],
    "history",
    ["~", "home"],
    "hostname",
    "if",
    ["ip", "I P"],
    "jobs",
    "localhost",
    ["ls", "list"],
    "kill",
    "make",
    ["mkdir", "make dir"],
    ["mv", "move"],
    "ping",
    ["pkill", "P kill"],
    "python",
    ["rm", "remove"],
    ["rsync", "R sync"],
    "search",
    "set",
    "setopt",
    "sort",
    ["ssh", "S S H"],
    "sudo",
    "then",
    "touch",
    "true",
    ["tsk", "tisk"],
    "type",
    ["uniq", "unique"],
    "unfunction",
    "unset",
    "unsetopt",
    ["/usr/bin/", "user bin"],
    "up",
    "wait",
    ["wc", "word count"],
    "which",
    "while",
    ["xargs", "X args"],
    ["zsh", "Z shell"],

    [">", "stood out"],
    ["2>", "stood err"],
    ["&>", "stood both"],
]

ShellKeywordRule = KeywordRule(["shell-mode", "sh-mode"], _keywords)

_mapping = {
    "back [<i>]"        : Key("b,enter") * Repeat(extra="i"),
    "forward [<i>]"     : Key("f,enter") * Repeat(extra="i"),
    "ascend [<i>]"      : (EmacsText("up") + Key("enter")) * Repeat(extra="i"),
}

ShellRule = makeContextualRule("Shell", _mapping, emacsExtras, emacsDefaults)
ShellRule.context.addRequirement(IsEmacs)
ShellRule.context.addRequirement(ModeRequirement(modes=["shell-mode", "sh-mode"]))
