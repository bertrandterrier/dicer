from typing import Any, Callable, Literal

import dicer as dcr

from dicer.schemes import Point, DcrTokenType, NEWLINE, EOF, eof, TERM


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
    __slots__ = ("_id", "_start", "_end",
                 "_token_obj", "_token_name", "_payload")
    def __new__(cls,
                token: DcrTokenType,
                start_point: Point,
                end_point: Point,
                payload: str|None = None) -> "DcrToken":

        inst = super().__new__(cls, (str(token),
                                     payload,
                                     (start_point, end_point)))
        inst._id = DcrTokenID()
        inst._start = start_point
        inst._end = end_point
        inst._payload = payload
        inst._token_obj = token
        inst._token_name = str(token)
        return inst

    @property
    def ID(self) -> int:
        return getattr(self, '_id', None) or dcr.fn.break_process()


    def get_payload(self) -> str|None:
        return getattr(self, '_payload', None)

    @property
    def START(self) -> tuple[int, int]:
        return getattr(self, '_start', None) or dcr.fn.break_process()

    @property
    def END(self) -> tuple[int, int]:
        return getattr(self, "_end", None) or dcr.fn.break_process()

    def get_name(self) -> str:
        return self._token_name

    def get_token_type(self) -> str:
        return str(self._token_obj)

class Lexer:
    def __init__(self, src: str):
        self._data: list[DcrToken] = []
        self._buf: str = src
        self._row: int = 0 
        self._col: int = 0
        self._last_row_max_col: int = 0
        self._cache: dict[str, str|int|DcrTokenType|None] = {
            'start_row': 0,
            'start_col': 0,
            'payload': ""
        }




class DcrLexer:
    __slots__ = ("__src", "_lxr", "_trc", "_bu",
                 "_trc_lim", "_bu_lim",
                 "_crsr")

    def __new__(cls) -> "DcrLexer":
        inst = object.__new__(cls)
        inst._trc, inst._bu = [[], []]
        inst._crsr = 0
        return inst

    def init_lexer(self, src: str, trace_limit: int = 30, backup_limit: int = 1) -> Lexer:
        if getattr(self, '_lxr'):
            raise PermissionError("To overwrite lexer use 'clean_reset_lexer'")
        self._lxr = Lexer(src)
        self.__src = src
        self._trc_lim = trace_limit
        self._bu_lim = backup_limit
        return self._lxr

    def clean_reset_lexer(self) -> Lexer:
        self._crsr = 0
        self._lxr = Lexer(self.__src)
        return self._lxr

    def del_lexer_stages(self, steps: int = 1) -> Lexer:
        if len(self._trc) < 1:
            raise LookupError("No trace found")
        snapshot, steps = (self._trc.pop(), steps - 1)
        while steps > 0 and self._trc:
            snapshot = self._trc.pop()
            steps -= 1
        self._crsr, self._lxr = snapshot
        return self._lxr


    def make_snapshot(self) -> None:
        self._trc.append(self._lxr)
        while len(self._trc) > self._trc_lim and len(self._trc) > 0:
            self._trc.pop(0)
    
    def make_backup(self) -> None:
        self._bu.append(self._lxr)
        while len(self._bu) > self._bu_lim and len(self._bu) > 0:
            self._bu.pop(0)
            
   
    def cursor(self) -> int:
        crsr = getattr(self, '_crsr', None)
        if not isinstance(crsr, int):
            raise LookupError("No cursor")
        return crsr

    def lookahead(self, lxr: Lexer) -> str:
        return lxr._buf[self.cursor()]

    def force_cursor(self) -> None:
        self._crsr += 1

    def force_lexer(self, lxr) -> Lexer:
        self._lxr = lxr
        return self._lxr
    
    def advance(self, lxr: Lexer, skip: bool):
        if not skip:
            lxr._cache['payload'] = str(lxr._cache['payload']) + self.lookahead(lxr)
        if lxr._buf[self.cursor()] in [NEWLINE, TERM]:
            lxr._row += 1
            lxr._last_row_max_col = lxr._col
            lxr._col = 0
        else:
            lxr._col += 1
        self.force_cursor()
        return self.force_lexer(lxr)
    
    def peak_ahead(self, lxr: Lexer, jump: int = 1) -> str|eof:
        if (self.cursor() + jump) >= len(lxr._buf):
            return EOF
        else:
            return lxr._buf[self.cursor()]
    
    def mark_type(self, lxr: Lexer, _type: DcrTokenType) -> Lexer:
        if lxr._col == 0:
            lxr._cache['end_row'] = lxr._row - 1
            lxr._cache['end_col'] = lxr._last_row_max_col
        else:
            lxr._cache['end_row'] = lxr._row
            lxr._cache['end_col'] = lxr._col - 1
    
        lxr._data.append(
            DcrToken(_type,
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
        return self.force_lexer(lxr) 
