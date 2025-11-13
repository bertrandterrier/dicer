from enum import Enum, EnumType
from pathlib import Path
from typing import Callable, Literal
import yaml

import dicer as dcr

class eof(str):
    def __new__(cls) -> "eof":
        return super().__new__(cls, "EOF")

EOF = eof()

class TokenType(Enum):
    pass

def load_tkn_types(_path: str|Path=dcr.DCR_DATA_SHARED,
                   _needed_keys: list[str] = ['name', 'id'],
                   _formatter: dict[str, Callable[..., str]] = {
                        'name': lambda x: str(x).upper()
                    }) -> list[dict]:
    with open(_path, 'r') as f:
        raw: list[dict] = yaml.load(f, Loader=yaml.Loader)
    
    result: list[dict] = []
    for d in raw:
        var: dict = {}
        for key in _needed_keys:
            if not key in var.keys():
                raise LookupError("Need certain keys...")
        for k,v in d.items():
            fmt: Callable|None = _formatter.get(k)
            if fmt:
                v = fmt(v)
            var[k] = v
        result.append(var)
    return result

def set_tkn_types(data: list[dict]):
    for entry in data:
        setattr(TokenType,
                entry.get('name', 'ERR'),
                int(entry.get('id', -1)))
    return

set_tkn_types(load_tkn_types())

class Point(tuple):
    __slots__ = ("ROW", "COL", "TYPE")
    def __new__(cls,
                row,
                col,
                _type: Literal['start', 'end', '_test'],
                ) -> "Point":
        inst = super().__new__(cls, (row, col))
        inst.ROW, inst.COL = (int(row), int(col)) 
        inst.TYPE = _type
        return inst

    def _get_comp(self, other) -> "Point|None":
        if isinstance(other, Point):
            return other
        try:
            return Point(other[0], other[1], '_test')
        except:
            return None


    def __eq__(self, other) -> bool:
        other = self._get_comp(other)
        if not other:
            return False
        return other.ROW == self.ROW and self.COL == other.ROW

    def __gt__(self, other) -> bool:
        var: Point|None = self._get_comp(other)
        if not var:
            raise ValueError("Is not comparable")
        if var.ROW == self.ROW:
            return self.COL > var.COL
        return self.ROW > var.ROW

    def __ge__(self, other) -> bool:
        if self.__gt__(other):
            return True
        var: Point|None = self._get_comp(other)
        if not var:
            raise TypeError()
        return self.ROW == var.ROW and self.COL == var.COL
