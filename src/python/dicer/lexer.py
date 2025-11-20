from copy import deepcopy
from typing import Any, Iterator, Literal, Pattern
import re

from dicer.schemes import *


class DcrCursor:
    """Cursor with one directional line/column movement.
    """
    __slots__ = (
        "_line", "_col", "_hist"
    )
    def __new__(cls) -> "DcrCursor":
        """Create new cursor with LINE: 0, COLUMN: 0"""
        inst = object.__new__(cls)
        inst._line = 0
        inst._col = 0
        inst._hist = []
        return inst

    def __call__(self, linebreak: bool, steps: int = 1):
        """If linebreak=False: mycursor.move(); else same as mycursor.linebreak(True, 1)
        """
        self._col += steps

    def move(self, steps: int = 1):
        """Moves the column forward by STEPS."""
        self._col += abs(steps)

    def linebreak(self, reset_column: bool, num_of_breaks: int = 1):
        """Breaks column by NUM_OF_BREAKS. RESET_COLUMN will set COLUMN to 0.
        """
        self._hist.append(self._col)
        self._line += abs(num_of_breaks)
        if reset_column:
            self._col = 0

    @property
    def HISTORY(self) -> list:
        return self._hist

    @property
    def LINE(self) -> int:
        """Get line value."""
        return self._line

    @property
    def COLUMN(self) -> int:
        """Get column value."""
        return self._col

    def last(self) -> tuple[int, int]:
        if self.COLUMN > 0:
            return (self.LINE, self.COLUMN - 1)
        elif len(self.HISTORY) < 0:
            return (0, 0)
        else:
            return (self.LINE - 1, self.HISTORY[-1])

    def float(self) -> float:
        """Represents position as "<LINE>.<COLUMN>".
        ex. for LINE=3, COLUMN=5: '3.5'
        """
        return float(f"{self.LINE}.{self.COLUMN}")

    def __str__(self) -> str:
        return f"({self.LINE}, {self.COLUMN})"

    def __getitem__(self, i):
        if i == 0:
            return self.LINE
        elif i == 1:
            return self.COLUMN
        return None

    def __len__(self) -> int:
        """Returns number of total steps.
        Every linebreak will be +1 move, like every column will be +1 move.
        """
        count = len(self.HISTORY) - 1 # break "\n" steps
        for entry in self.HISTORY:
            count += entry
        return count

    def __iter__(self) -> Iterator:
        yield self.LINE
        yield self.COLUMN

    def _foreign_line_col(self, arg) -> tuple[int, int]:
        if isinstance(arg, (float)):
            varl, varc = str(arg).split(".", 1)
            return int(varl), int(varc)
        elif isinstance(arg, (tuple, list, DcrCursor)):
            lvar, cvar = arg
            return int(lvar), int(cvar)
        else:
            raise ValueError() 

    def __gt__(self, other) -> bool:
        l, c = self._foreign_line_col(other)
        return self.LINE > l or (self.COLUMN > c and self.LINE == l)

    def __eq__(self, other):
        try:
            l, c = self._foreign_line_col(other)
            return self.LINE == l and self.COLUMN == c
        except:
            return False

    def __st__(self, other) -> bool:
        l, c = self._foreign_line_col(other)
        return self.LINE < l or (self.COLUMN < c and self.LINE == l)

# --- BUFFER (Lexer) ---
class LexemBuffer:
    _prot: list[int] = [-1]

    @classmethod
    def _id(cls) -> int:
        cls._prot.append(cls._prot[-1] + 1)
        return cls._prot[-1]

    def __init__(self, start: Point):
        self.__id: int = LexemBuffer._id()
        self._start: Point = start
        self._curr_pos: Point = start
        self._buf: str = ""

    @property
    def IDX(self) -> int:
        return self.__id

    def getbuf(self) -> str:
        return self._buf

    def tobuf(self, arg: str) -> None:
        self._buf += arg

    @property
    def START(self) -> Point:
        return self._start

    def setpos(self, new: Point) -> None:
        self._curr_pos = new

    def update(self, arg: str, pos: Point) -> None:
        self._curr_pos = pos
        self._buf += arg


# --- Default Preprocess ---
def preprocess(
    src: str|list[str],
    x_offset: int = 0,
    x_cutoff: int = -1,
    y_offset: int|None = None,
    pttrns: dict[Literal['start', 'stop', 'cmt','ignore', 'extract'], Pattern] = {'cmt': re.compile(r"^(.*)(~{1,}>.*)")}
) -> list[str]:
    """Preprocess source string. Empty lines and comment lines will be dropped.

    src: str
        Source string.
    x_offset: int|Pattern|None
        Line offset, 0-indexed, inclusive. Defaults to 0.
    y_offset: int
        Column offset, 0-indexed. Will be used for every line. Use pttrns['extract'] 
        for other cases.
        Defaults to 0.
    x_cutoff: int
        Early cutoff line, exclusive. -1 for no early cutoff.
        Defaults to -1.
    pttrns: dict
        Use for special embedded cases.
            start   :: Does not start before not matched. Used AFTER offsets.
            stop    :: If matches, stop scanning.
            ignore  :: Ignore line, if matches.
            extract :: If match, group will be used as line. Otherwise ignored.
            comment :: Commentary, that will be dropped.
    """
    result: list[str] = []

    if isinstance(src, str):
        buf: list[str] = src.split("\n")[x_offset:]
    else:
        buf = src[x_offset:]
        
    if x_cutoff < 2 and x_cutoff > -1:
        return result
    elif x_cutoff > 1:
        buf = buf[:x_cutoff]

    start = not 'start' in pttrns.keys()
    for line in buf:
        if not start:
            if pttrns['start'].match(line):
                start = True
                continue
        elif 'ignore' in pttrns.keys():
            if pttrns['ignore'].match(line):
                continue
        elif 'stop' in pttrns.keys():
            if pttrns['stop'].match(line):
                break

        if len(line.strip()) < 1:
            continue

        if 'extract' in pttrns.keys():
            match = pttrns['extract'].match(line)
            if not match:
                continue
            line = match.group()

        if 'comment' in pttrns.keys():
            match = pttrns['cmt'].match(line)
            if match:
                line, _ = match.groups()
                if not line:
                    continue

    return result


# --- LEXER ---
class DcrLexer:
    def __init__(
        self,
        src: str|list[str],
        func: Callable[..., list[str]] = preprocess,
        *args,
        **kwargs
    ):
        """Initialize Dicer lexer.
        
        src: list
            Source as list of lines or string.
        func: callable(str|list,...) -> list[str]
            Preprocess function. Should take the source together with args and 
            kwargs and return a list of strings.
        """
        if not src:
            raise ValueError("Empty source")
        self.__backup: list[DcrLexer] = []

        self.__stage: int = 0
        self._tokens: list[DcrToken] = []
        self._trash: list[str] = []
        self._crsr = DcrCursor()


        self._src_buf: list[str|Null|Eof] = func(src, *args, **kwargs)
        self._lxm_buf: LexemBuffer = LexemBuffer(tuple(self._crsr))

        self._state: str|None = None
        self._guess: GuessRule|None = None


    @property
    def pos(self) -> tuple[int, int]:
        if not isinstance(self._crsr, DcrCursor):
            raise RuntimeError()
        return tuple(self._crsr)

    @property
    def guess_state(self) -> int:
        return self._guess_state

    def guess(self, guess: Any) -> None:
        if self._guess != None:
            raise PermissionError("Already in guess.")
        self.snapshot()
        self._guess = guess

    def unguess(self) -> None:
        self.undo() 
        self._guess = None

    def snapshot(self) -> None:
        """Creates a backup snapshot."""
        self.__backup.append(deepcopy(self))
        self.__stage += 1

    def get_backup(self, backsteps: int = 1, strict: bool = True) -> "DcrLexer":
        """Get backup snapshot of lexer state."""
        if abs(backsteps) > self.__stage and strict:
            raise IndexError("Cannot got farther back then 0")
        elif abs(backsteps) > self.__stage :
            return self.__backup[0]
        else:
            return self.__backup[-abs(backsteps)]
        
    def undo(self, **kwargs) -> None:
        """Resets state of token AFTER last (or before last) token was marked."""
        if self.__stage == 0:
            raise IndexError("Cannot undo if stage 0")

        backup: DcrLexer = self.get_backup(**kwargs)
        self.__dict__ = deepcopy(backup.__dict__)

    def burn_lxm_payload(self, to_new_trash_elem: bool = False) -> None:
        """Whole lexem payload to trash. Use self.undo() to restore and make 
        characters usable again.
        """
        if to_new_trash_elem:
            self._trash.append(EMPTY)
        self._trash[-1] += self._lxm_buf._buf
        self._lxm_buf = LexemBuffer(tuple(self._crsr))

    def mark_end(self, token_type: str) -> DcrToken:
        """Marks token end and creates token of token_type, creates token and new lexem buffer.
        """
        tkn = DcrToken(
            token_type,
            (self._lxm_buf.START, self._crsr.last()),
            idx = self._lxm_buf.IDX,
            payload = self._lxm_buf.getbuf()
        )
        self._tokens.append(tkn)
        self._guess = self._state = None
        self._lxm_buf = LexemBuffer(tuple(self._crsr))
        self._trash.append(EMPTY)
        return tkn


    def tobuf(self, arg: str) -> None:
        """Add character to lexem buffer. For standard usage use self.move_forward(False).
        """
        self._lxm_buf.tobuf(arg)

    def totrash(self, arg: str, new_elem: bool = False) -> None:
        """Add character to trash instead to token lexem. For standard usage 
        self.move_forward(True).
        """
        if new_elem:
            self._trash.append(EMPTY)
        self._trash[-1] += arg


    def move_forward(self, skip: bool) -> None:
        """Move cursor forward for one character. If SKIP true, ignore character 
        for token.
        """
        char: str|Eof|Null = self.lookahead()
        if isinstance(char, (Eof, Null)):
            raise EOFError()
        if not skip:
            self._lxm_buf.tobuf(char)
        else:
            self.totrash(char)
        return

    def lookahead(self) -> str|Eof|Null:
        """Get next character."""
        lpos, cpos = self._crsr
        line: str|Eof|Null = self._src_buf[lpos]
        if isinstance(line, Eof|Null):
            return line
        else:
            return line[cpos]

    def get_tokens(self) -> list[DcrToken]:
        return [tkn for tkn in self._tokens]

    @property
    def state(self) -> bool:
        return bool(self._lxm_buf.getbuf())

    @state.setter
    def state(self, other: str):
        self._state = other


# --- SCAN ---
def scan(src: str, *args, **kwargs) -> tuple[int, str, list[DcrToken]]:
    lxr: DcrLexer = DcrLexer(src, *args, **kwargs)

    if isinstance(lxr.lookahead(), (Eof, Null)):
        raise RuntimeError("No source left after preprocess")

    counter = 0
    while not isinstance(lxr.lookahead(), (Eof, Null)):
        counter += 1

        if lxr.lookahead() in [';', NEWLINE]:
            lxr.move_forward(False)
            lxr.mark_end('')



    print(f"Lexer finished at after step {counter}")
    
    # ...
    return 0, "FINE", lxr.get_tokens()


