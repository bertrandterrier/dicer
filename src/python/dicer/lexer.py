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

class DcrLexer:
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
        self._cursor: int = 0


_history_stor_lim: int = 1
_backup_stor_lim: int = 23
_history: list[list[DcrLexer]] = []
_backup: list[DcrLexer] = []

lexer: DcrLexer = DcrLexer("")

def get_snap(step_mod: int = 0) -> DcrLexer:
    var_backup = [lxr for lxr in _backup]
    var_lxr = var_backup.pop(0)
    while step_mod > 0:
        if not var_backup:
            return var_lxr
        var_lxr = var_backup.pop()
        step_mod -= 1
    return var_lxr

def reset_lexer(steps_back: int = 1):
    global lexer
    lexer = get_snap(steps_back - 1)
    return lexer

def mkbackup() -> None:
    global _backup
    _backup.append(lexer)
    while len(_backup) > _backup_stor_lim and len(_backup) > 0:
        _backup.pop(0)

def write_to_history() -> None:
    global _history
    _history.append(_backup)
    while len(_history) > _history_stor_lim and len(_history) > 0:
        _history.pop(0)
        

def mklxr(src: str,
            backup_max: int =_backup_stor_lim,
            hist_max: int = _history_stor_lim,
            ) -> DcrLexer:
    global _history_stor_lim, _backup_stor_lim
    _history_stor_lim = hist_max
    _backup_stor_lim = backup_max

    write_to_history()
    global lexer
    lexer = DcrLexer(src)
    return lexer

def setlxr(lxr: DcrLexer) -> DcrLexer:
    mkbackup()
    global lexer
    lexer = lxr
    return lexer

def lookahead(lxr: DcrLexer) -> str:
    return lxr._buf[lxr._cursor]

def advance(lxr: DcrLexer, skip: bool):
    if not skip:
        lxr._cache['payload'] = str(lxr._cache['payload']) + lookahead(lxr)
    if lxr._buf[lxr._cursor] in [NEWLINE, TERM]:
        lxr._row += 1
        lxr._last_row_max_col = lxr._col
        lxr._col = 0
    else:
        lxr._col += 1
    lxr._cursor += 1
    return setlxr(lxr)

def peak_ahead(lxr: DcrLexer, jump: int = 1) -> str|eof:
    if (lxr._cursor + jump) >= len(lxr._buf):
        return EOF
    else:
        return lxr._buf[lxr._cursor]

def mark_type(lxr: DcrLexer, _type: DcrTokenType) -> DcrLexer:
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
    return setlxr(lxr)
