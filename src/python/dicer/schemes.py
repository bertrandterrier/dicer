from dataclasses import dataclass
from random import choices
from string import ascii_letters, digits
from typing import Iterable, Iterator, Literal, Callable, LiteralString

ALPHANUMS: str = ascii_letters + digits + "_"

NEWLINE: str = "\n"
SPACE: str = " "
TAB: str = "\t"
EMPTY: str = ""

class eos(str):
    def __new__(cls) -> "eos":
        return super().__new__(cls, ";")

    def __eq__(self, other) -> bool:
        if isinstance(other, eos):
            return True
        elif str(other) == ";":
            return True
        else:
            return False

class eof(str):
    def __new__(cls) -> "eof":
        return super().__new__(cls, "END OF FILE")
    def __eq__(self, other) -> bool:
        if isinstance(other, eof):
            return True
        elif str(other) == ";":
            return True
        else:
            return False

class null(str):
    def __new__(cls) -> "null":
        return super().__new__(cls, "EMPTY STRING ELEMENT")

    def __eq__(self, other) -> bool:
        if isinstance(other, null):
            return True
        elif str(other) == ";":
            return True
        else:
            return False

NULL = null()
EOF = eof()
EOS = eos()

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

CheckFuncPair = tuple[Callable[[str, str], bool], str|list[str]]
class GuessRule:
    def __init__(
        self,
        *tests: str|LiteralString|Callable[[str], bool]|CheckFuncPair,
    ):
        self._tcomps: list[str] = []
        self._tpttrns: list[LiteralString] = [] 
        self._t1funcs: list[Callable[[str], bool]] = []
        self._t2funcs: list[CheckFuncPair] = []

        for t in tests:
            if isinstance(t, LiteralString):
                self._tpttrns.append(t)
            elif isinstance(t, str):
                self._tcomps.append(t)
            elif isinstance(t, Callable):
                self._t1funcs.append(t)
            elif isinstance(t, tuple):
                self._t2funcs.append(t)
            else:
                raise TypeError()


class GuessBranch:
    NAME_LTTR_NUM: int = 8
    _reg: list[str] = []
    
    @classmethod
    def getname(cls, length: int = NAME_LTTR_NUM, selection_source: str = ALPHANUMS) -> str:
        if length < 1:
            raise ValueError()
        name = ""
        while len(name) == 0 or name in cls._reg:
            name = EMPTY.join(choices(ALPHANUMS, k = max(1, abs(length))))
        return name

    @classmethod
    def regname(cls, name) -> Literal[0, 1]:
        if len(name) < 1 or name in cls._reg:
            return 0
        else:
            cls._reg.append(name)
            return 1

    def __init__(
        self,
        null_branch: bool,
        precedence: int = 0,
        fin_rules: list[GuessRule],
        branchings: list[tuple[GuessRule, "GuessBranch"]],
    ):
        self._prec: int = precedence

class GuessTree:
    def __init__(self, name: str, *branches: GuessBranch):
        self._branches: 
