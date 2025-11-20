from copy import deepcopy
from typing import Callable, Iterator
import re

import dicer as dcr
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

    def mkguess(self, guess: str, expect_tree) -> None:
        if self._guess:
            raise PermissionError("Cannot overwrite current guess. Use self.replace_guess() for that.")
        self._guess = guess





# --- LEXER ---
class DcrLexer:
    def __init__( self, src: str):
        if not src:
            raise ValueError("Empty source")

        self.__backup: list[DcrLexer] = []
        self.__stage: int = 0
        self._tokens: list[DcrToken] = []
        self._trash: list[str] = []

        self.__orig_src: str = src
        self._crsr = DcrCursor()
        self._src_buf: list[str|null|eof] = self.preprocess() 
        self._lxm_buf: LexemBuffer = LexemBuffer(tuple(self._crsr))


    @property
    def pos(self) -> tuple[int, int]:
        if not isinstance(self._crsr, DcrCursor):
            raise RuntimeError()
        return tuple(self._crsr)

    def snapshot(self) -> None:
        self.__backup.append(deepcopy(self))
        self.__stage += 1

    def get_backup(self, backsteps: int = 1, strict: bool = True) -> "DcrLexer":
        """Get backup snapshot of lexer state.
        """
        idx = self.__stage - backsteps
        if idx < 0 and strict:
            raise IndexError("Cannot got farther back then 0")
        elif idx < 0:
            return self.__backup[0]
        else:
            return self.__backup[idx]
        
    def rewind(self, **kwargs) -> None:
        """Resets state of token AFTER last (or before last) token was marked.
        """
        if self.__stage == 0:
            raise IndexError("Cannot rewind if stage 0")
        backup: DcrLexer = self.get_backup(**kwargs)
        self.__dict__ = deepcopy(backup.__dict__)
        self.__stage = max(self.__stage - kwargs.get('backsteps', 1), 0)

    def burn_lxm_payload(self, to_new_trash_elem: bool = False) -> None:
        """Whole lexem payload to trash. Use self.rewind() to restore and make 
        characters usable again.
        """
        if to_new_trash_elem:
            self._trash.append(EMPTY)
        self._trash[-1] += self._lxm_buf._buf
        self._lxm_buf = LexemBuffer(tuple(self._crsr))

    def mark_end(self, token_type: str) -> DcrToken:
        """Marks token end, creates token and new lexem buffer.
        """
        tkn = DcrToken(
            token_type,
            (self._lxm_buf.START, self._crsr.last()),
            idx = self._lxm_buf.IDX,
            payload = self._lxm_buf.getbuf()
        )
        self._tokens.append(tkn)
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
        char: str|eof|null = self.lookahead()
        if isinstance(char, (eof, null)):
            raise EOFError()
        if not skip:
            self._lxm_buf.tobuf(char)
        else:
            self.totrash(char)
        return

    def lookahead(self) -> str|eof|null:
        """Get next character."""
        lpos, cpos = self._crsr
        line: str|eof|null = self._src_buf[lpos]
        if isinstance(line, eof|null):
            return line
        else:
            return line[cpos]

    def preprocess(self) -> list[str|eof]:
        """Drop offset; drop comments; clean end to EOS."""
        buf = []
        orig = self.__orig_src.split("\n")
        i, line = (0, EMPTY)
        while i < len(orig):
            line = orig[i]
            i += 1

            # Clean commentary lines
            line_cmt_match = re.match(r"^~{2,}>.*$", line)
            cmt_match = re.match(r"^(.*?)(~{2,}>.*)$", line)
            if line_cmt_match:
                continue
            elif cmt_match:
                line, _ = cmt_match.groups()

            # Avoid empty lines at the beginning
            if line == EOF:
                buf.append(EOF)
                return buf
            elif len(buf) < 1:
                if line == str(EMPTY):
                    continue
                elif re.match(r"^\s+$", line):
                    continue

            line = line.strip()
            # Clean start of line
            dirthead = re.match(r"^[; ]*", line)
            if dirthead:
                if dirthead.end() == len(line):
                    continue
                else:
                    line = line[dirthead.end():]

            # Clean end of line
            if not line.endswith(";"):
                while line[-1] in [SPACE, NEWLINE] and len(line) > 1:
                    line = line[:-1]
                if line in [SPACE, NEWLINE]:
                    continue
                line = line + ";"
                
            buf.append(line)
        if len(buf) < 1:
            raise RuntimeError()
        elif buf[-1] != EOF:
            buf.append(EOF)
        return buf

    def get_tokens(self) -> list[DcrToken]:
        return [tkn for tkn in self._tokens]

    def fresh_token(self) -> bool:
        return bool(self._lxm_buf.getbuf())

def scan(src: str) -> DcrLexer:
    lxr: DcrLexer = DcrLexer(src)
    return lxr

def tokenize(src: str) -> list[DcrToken]:
    lxr: DcrLexer = scan(src)
    tkns = lxr.get_tokens()

    
    return tkns
