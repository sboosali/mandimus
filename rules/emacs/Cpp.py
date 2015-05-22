#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Actions import Key
from rules.ContextualRule import makeContextualRule
from requirements.Emacs import IsEmacs
from requirements.ModeRequirement import ModeRequirement
from rules.emacs.common import emacsExtras, emacsDefaults
from rules.emacs.Cmd import Cmd
from rules.emacs.Keywords import KeywordRule

keywords = [
    # true keywords
    ["alignas", "align as"],
    ["alignof", "align of"],
    "assert",
    ["asm", "assembly"],
    "auto",
    "bool",
    "break",
    "case",
    "catch",
    "char",
    ["char16_t", "char sixteen"],
    ["char32_t", "char thirty two"],
    "class",
    "const",
    ["const_cast", "const cast"],
    ["constexpr", "const expr"],
    "continue",
    ["decltype", "decl type"],
    "default",
    "delete",
    "do",
    "double",
    ["dynamic_cast", "dynamic cast"],
    "else",
    ["#endif", "end if"],
    "enum",
    "explicit",
    "export",
    "extern",
    "false",
    "float",
    "for",
    "friend",
    "goto",
    "if",
    "inline",
    "int",
    "long",
    "main",
    "mutable",
    "namespace",
    "new",
    ["noexcept", "no except"],
    "nullptr",
    "operator",
    "private",
    "protected",
    "public",
    "register",
    "reinterpret_cast",
    "return",
    "short",
    "signed",
    ["std::size_t", "stood size"],
    ["sizeof", "size of"],
    "static",
    "static_assert",
    "static_cast",
    "struct",
    "switch",
    "template",
    "this",
    "thread_local",
    "throw",
    "true",
    "try",
    "typedef",
    ["typeid", "type I D"],
    "typename",
    "union",
    "unsigned",
    "using",
    "virtual",
    "void",
    "volatile",
    ["wchar_t", "wide char"],
    "while",

    # common enough
    ["endl", "end line"],
    "final",
    ["#include", "include"],
    ["int32_t", "int thirty two"],
    ["int64_t", "int sixty four"],
    "main",
    "override",
    ["std", "stood"],
    ["std::string", "string"],
    ["uint8_t", "you int eight"],
    ["uint16_t", "you int sixteen"],
    ["uint32_t", "you int thirty two"],
    ["uint64_t", "you int sixty four"],

    # boost
    ["bxxst", "boost"],
    "optional",
]

types = [
    "deque"
    "map",
    "multimap",
    "pair",
    "set",
    ["unique_ptr", "unique pointer"],
    ["unordered_map", "unordered map"],
    "vector",
]

CppKeywordRule = KeywordRule("c++-mode", keywords + types)
