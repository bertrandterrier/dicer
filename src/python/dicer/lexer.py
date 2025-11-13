from enum import Enum, EnumType
import dicer as dcr

import dicer as dcr
from dicer.schemes import Point, TokenType, EOF, eof

NEWLINE = "\n"
BREAKMARK = ";;"
NEXTMARK = ";"
TAB = "\t"
SPACE = " "


class DcrTokenID(int):
    __reg: list[int] = [0]

    def __new__(cls) -> "DcrTokenID":
        id = cls.get_next_id()
        return super().__new__(cls, id)

    @classmethod
    def get_next_id(cls) -> int:
        cls.__reg.append(cls.__reg[-1] + 1)
        return cls.__reg[-1]


class DcrToken(tuple):
    __slots__ = ("_id", "_start", "_end", "_type", "_payload")
    def __new__(cls,
                _type: TokenType,
                start_point: Point,
                end_point: Point,
                payload: str|None = None) -> "DcrToken":

        inst = super().__new__(cls, (_type,
                                     payload,
                                     (start_point, end_point)))
        inst._id = DcrTokenID()
        inst._start = start_point
        inst._end = end_point
        inst._payload = payload
        return inst

    @property
    def ID(self) -> int:
        return getattr(self, '_id', None) or dcr.fn.break_process()


    def get_payload(self) -> str|None:
        return getattr(self, '_payload', None)

    @property
    def STARTPOINT(self) -> tuple[int, int]:
        return getattr(self, '_start', None) or dcr.fn.break_process()

    @property
    def ENDPOINT(self) -> tuple[int, int]:
        return getattr(self, "_end", None) or dcr.fn.break_process()


class Lexer:
    def __init__(self, src: str):
        self._data: list[DcrToken] = []
        self._buf: list[str] = src.split("\n")
        self._row: int = 0 
        self._col: int = 0
        self._last_row_max_col: int = 0
        self._cache: dict[str, str|int|TokenType|None] = {
            'start_row': 0,
            'start_col': 0,
            'payload': ""
        }
        self._cursor: int = 0



def lookahead(lxr: Lexer) -> str:
    return lxr._buf[lxr._cursor]

def advance(lxr: Lexer, skip: bool):
    if not skip:
        lxr._cache['payload'] = str(lxr._cache['payload']) + lookahead(lxr)
    if lxr._buf[lxr._cursor] == NEWLINE:
        lxr._row += 1
        lxr._last_row_max_col = lxr._col
        lxr._col = 0
    else:
        lxr._col += 1
    lxr._cursor += 1
    return

def peak_ahead(lxr: Lexer, jump: int = 1) -> str|eof:
    if (lxr._cursor + jump) >= len(lxr._buf):
        return EOF
    else:
        return lxr._buf[lxr._cursor]

def mark_type(lxr: Lexer, _type: TokenType):
    lxr._cache['type'] = _type
    if lxr._col == 0:
        lxr._cache['end_row'] = lxr._row - 1
        lxr._cache['end_col'] = lxr._last_row_max_col
    else:
        lxr._cache['end_row'] = lxr._row
        lxr._cache['end_col'] = lxr._col - 1

    lxr._data.append(
        DcrToken(lxr._cache['type'],
                 Point(lxr._cache['start_row'],
                       lxr._cache['start_col'],
                       'start'),
                 Point(lxr._cache['end_row'],
                       lxr._cache['end_col'],
                       'end'),
                 payload = lxr._cache['payload']), # pyright: ignore
    )
    lxr._cache = {'start_row': lxr._row,
                  'start_col': lxr._col,
                  'payload': ""}
    return
