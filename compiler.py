""" 
Source/Help for this file:
https://www.rickyspears.com/technology/building-your-own-programming-language-from-scratch-a-deep-dive/ 
"""

import re
from collections import namedtuple

Token = namedtuple("Token", ["type", "value"])

TOKEN_SPEC = [
    ("NUMBER", r"\b(?:nothing|all|universe|everything|\d+)\b"),
    ("ID", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
    ("ASSIGN", r"transforms into"),
    ("PRINT", r"you speak of"),
    ("INPUT", r"you seek wisdom from beyond and call it"),
    ("WHILE", r"> enter .* while .*"),
    ("LEAVE", r"> leave .*"),
    ("IF", r"> inspect whether .*"),
    ("AND", r"\band\b"),
    ("OR", r"\bor perhaps\b"),
    ("NOT", r"is not"),
    ("EQ", r"is much like"),
    ("NEQ", r"differs from"),
    ("LT", r"stands before"),
    ("GT", r"towers above"),
    ("LE", r"stands no further than"),
    ("GE", r"stands not below"),
    ("SUM", r"reflect on all you have learned:"),
    ("MINUS", r"recall the distance between"),
    ("MUL", r"envision .* by .*"),
    ("DIV", r"divide .* among .*"),
    ("MOD", r"keep what remains of .* after sharing with .*"),
    ("END", r"\."),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
]
