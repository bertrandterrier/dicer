from random import choices
import re
from string import ascii_letters, digits
from typing import Literal, LiteralString, Pattern

ALPHANUMS: str = ascii_letters + digits + "_"

NEWLINE: str = "\n"
SPACE: str = " "
TAB: str = "\t"
EMPTY: str = ""

class Eos(str):
    def __new__(cls) -> "Eos":
        return super().__new__(cls, ";")

    def __eq__(self, other) -> bool:
        if isinstance(other, Eos):
            return True
        elif str(other) == ";":
            return True
        else:
            return False

class Eof(str):
    def __new__(cls) -> "Eof":
        return super().__new__(cls, "END OF FILE")
    def __eq__(self, other) -> bool:
        if isinstance(other, Eof):
            return True
        elif str(other) == ";":
            return True
        else:
            return False

class Null(str):
    def __new__(cls) -> "Null":
        return super().__new__(cls, "EMPTY STRING ELEMENT")

    def __eq__(self, other) -> bool:
        if isinstance(other, Null):
            return True
        elif str(other) == ";":
            return True
        else:
            return False

NULL = Null()
EOF = Eof()
EOS = Eos()

Point = tuple[int, int]


class DcrToken:
    __slots__ = (
        "TYPE", "SCOPE", "IDX", "PAYLOAD"
    )
    def __new__(
        cls,
        _type: str,
        scope: tuple[Point, Point],
        idx: int,
        payload: str|None = None
    ) -> "DcrToken":
        inst = object.__new__(cls)
        inst.TYPE = _type
        inst.SCOPE = (scope[0], scope[1]) 
        inst.IDX = idx
        inst.PAYLOAD = payload
        return inst

    def start(self) -> Point:
        return self.SCOPE[0]

    def end(self) -> Point:
        return self.SCOPE[1]

    def col_end(self) -> int:
        return self.SCOPE[1][1]

    def col_start(self) -> int:
        return self.SCOPE[0][1]

    def lstart(self) -> int:
        return self.SCOPE[0][0]

    def lend(self) -> int:
        return self.SCOPE[1][0]

    def lrange(self) -> list[int]:
        return list(range(self.lstart(), self.lend() + 1))

GuessRule= tuple[str|LiteralString|Pattern, list[str]|str]

class Guess:
    def __init__(self, *rules: GuessRule):
        self._rules: list[tuple[str|Pattern, list[str]]] = []
        self._left: list[str] = []

        for rule, item in rules:
            if isinstance(rule, LiteralString):
                rule = re.compile(rule)
            if isinstance(item, str):
                item = [item]
            self._rules.append((rule, item))
            self._left+= item

    def check(self, arg: str) -> int:
        left = []
        new_rules: list[tuple[str|Pattern, list[str]]] = []
        rules = [t for t in self._rules]

        for r, tps in rules:
            if isinstance(r, str):
                matched = r in arg or r == arg
            elif isinstance(r, Pattern):
                matched = r.match(arg)
            else:
                raise TypeError()

            if matched:
                new_rules.append((r, tps))
                left += [t for t in tps if not tps in left]
        self._rules, self._left = (new_rules, left)
        return len(self._left)

    def get(self) -> list[str]:
        return self._left
