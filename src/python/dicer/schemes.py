import re
from typing import Any, Literal, LiteralString, Pattern, Iterator 

# --- Constants ---
LINEBREAK = "\n"
SPACE = " "
SLASH = "/"

# --- EOF ---
class eof(str):
    def __new__(cls) -> "eof":
        return super().__new__(cls, "EOF")
EOF = eof()


# --- Position Pointer ---
class Point(tuple):
    """Position pointer with (ROW, COL), 0-indexed.

    Comparison checks 1. self.ROW, 2. self.COL. Never self.TYPE.
    """
    __slots__ = ("ROW", "COL", "TYPE")
    def __new__(cls,
                row,
                col,
                _type: Literal['start', 'end', '_test'],
                ) -> "Point":
        """Creates immutable position Point.

        row: int or integer-like
            Row, 0-indexed. Uses int(row).
        col: int or integer-like
            column, 0-indexed. Uses int(col).
        _type: \"start\"|\"end\"|\"_test\"
            Point type. \"_test\" for internal usage.
        """
        row, col = (int(row), int(col))
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


class TokenType(str):
    __slots__ = ("category","regex", "symbols",
                 "subtypes", "_id", "_help")
    def __new__(cls,
                id: int|float|str,
                name: str,
                regex: list[LiteralString] = [],
                symbols: list[str] = [],
                category: str = "OTHER",
                help_text: str|None = None,
                subtypes: list[dict] = [],
                ) -> "TokenType":
        inst = super().__new__(cls, name.upper())
        inst.regex = [e for e in regex]
        inst.symbols = [e for e in symbols]
        inst._help = help_text or ""
        inst.subtypes = [d for d in subtypes if type(d) == dict]
        inst.category = category
        inst._id = str(id) 
        return inst

    def id(self) -> str:
        return f"#{self._id}"

    def match_subtype(self,
                      arg: str,
                      ) -> list[tuple[str, str, str]]:
        """If matching returns a dictionary with keys:
        """
        for map in self.subtypes:
            for expr in map.get('regex', []):
                match = re.match(expr, arg.lower())
                if not match:
                    continue
                result = []
                for i, grp in enumerate(match.groups()):
                    result.append((map['idents'][i],
                                   map['types'][i],
                                   grp))
                return result
        return []


    def match(self,
              arg: str,
              match_subtypes: bool = True,
              ) -> bool:
        for expr in self.regex:
            if re.match(expr, arg.lower()):
                return True
        if match_subtypes:
            return bool(self.match_subtype(arg))
        else:
            return False

    def lookup(self,
               arg: str,
               sym_idx: int|list[int]|None = None
               ) -> bool:
        """Searches for argument in symbols.

        sym_idx: int | list[int] | None
            Specify symbol(s) by index. If None, full symbol list will be used.
            Defaults to None.
        Result:
            bool: True if found.
        """
        sym_idx = sym_idx or list(range(len(self.symbols) - 1))
        if isinstance(sym_idx, int):
            symbols = self.symbols[sym_idx]
        else:
            symbols = [self.symbols[i] for i in sym_idx]
        return arg.lower() in symbols

    def eval(self, arg: str) -> bool:
        """Evaluates if, either argument in symbol list, or argument in regex list.
        """
        return self.lookup(arg) or self.match(arg)

    def __repr__(self) -> str:
        if self.category:
            infix = "_" + self.category
        else:
            infix = ""
        return f"{self.id()}_{infix}{self}"

    def help(self, instant_print: bool = False) -> str:
        txt = [repr(self)]
        if self.help():
            txt.append(f"{2*SPACE}Help >>")
            txt.append(f"{4*SPACE}".join(self._help.split("\n")))
        result = LINEBREAK.join(txt)
        if instant_print:
            print(result)
        return result

# --- Token Types ---
class TokenData:
    def __init__(self,
                 data: dict,
                 meta_pattern: LiteralString|None = r"^_.+",
                 ignore_pattern: LiteralString|None = None):
        self._raw: dict[str, Any] = {str(k): v for k, v in data.items()}
        self._meta: dict[str, Any] = {}
        self._reg: dict[str, list[str]] = {}
        self._tkns: dict[str, TokenType] = {}
        self._flat_data: list[TokenType] = [] 

        if ignore_pattern:
            self._ipttrn = re.compile(ignore_pattern)
            cleaned_data, _ = self._filter(self._raw, self._ipttrn)
        else:
            cleaned_data = self._raw
        if meta_pattern:
            self._mpttrn = re.compile(meta_pattern)
            filtered_data, self._meta = self._filter(cleaned_data,
                                                self._mpttrn)
        else:
            filtered_data = cleaned_data 

        for tkn in TokenData.mkreg(filtered_data):
            self._flat_data.append(tkn) 
            self._reg[tkn.category] = self._reg.get(tkn.category,
                                                      []
                                                      ).append(str(tkn))
            self._tkns[str(tkn)] = tkn

    @staticmethod
    def mkreg(data: dict) -> list[TokenType]:
        result: list[TokenType] = []

        for key, val in data.items():
            if not isinstance(val, dict):
                raise ValueError("Needs list of dictionaries")

            for sg, pl in zip(['symbol', 'regex'],
                              ['symbols', 'regexes']):
                val[pl] = val.get(pl, [])
                if sg in val.keys():
                    val[pl].append(val[sg])
                # If splitted into different regex operatons
                if 'subtypes' in val.keys():
                    val[pl] += val['subtypes'].get('regex', [])

            tkn = TokenType(val['id'],
                            val.get('name', 'unknown').upper(),
                            regex = val.get('regexes', []),
                            symbols = val.get('symbols', []),
                            help_text = val.get('help'),
                            category = key,
                            subtypes = val.get('subtypes', [])
                            )
            result.append(tkn)
        return result


    def key_ignorable(self, key: str, _pttrn: None|Pattern = None) -> bool:
        pttrn = _pttrn or self._ipttrn
        if not pttrn:
            return False
        elif not pttrn.match(key):
            return True
        else:
            return False
            

    def is_meta_key(self,
                    key: str,
                    _pttrn: Pattern|None = None
                    ) -> bool:
        pttrn = _pttrn or self._mpttrn
        if not pttrn:
            return False
        elif pttrn.match(key):
            return True
        else:
            return False

    def _filter(self, data: dict, pttrn: Pattern) -> tuple[dict, dict]:
        cleaned, rest = ({}, {})
        for key, val in data.items():
            if pttrn.match(key):
                cleaned[key] = val
            elif not isinstance(val, dict):
                cleaned[key]
                c, r = self._filter(val, pttrn = pttrn)
                if c:
                    cleaned[key] = {k: v for k, v in c.items()}
                if r:
                    rest[key] = {k: v for k, v in rest.items()}
        return cleaned, rest

    def gettkn(self, name: str, default: Any|None = None) -> Any:
        return self._tkns.get(name, default)

    def get(self,
            name: str,
            category: str|None = None,
            default: Any = None,
            ) -> Any:
        if '|' in name:
            return [self.get(n,
                             category=category,
                             default=default
                             ) for n in name.split("|")]
        if category:
            if not name in self._reg.get(category, {}):
                return default
        return self._tkns.get(name, default)

    def field_iter(self, name: str, alt: str) -> Iterator:
        for tkn in self._flat_data:
            val = getattr(tkn, name, getattr(tkn, alt))
            if val:
                yield val

    def match_token(self,
                    arg: str,
                    token: str) -> bool:
        tkn = self._tkns[token]
        return tkn.match(arg)

    def search(self,
            arg: str,
            if_multiple_react: Literal['first', 'error', 'default', 'last', 'in_str_list', None] = 'error',
            mode: Literal['eval', 'find', 'match'] = 'eval',
            category: str|None = None,
            default: Any = None,
            ) -> str|Any:
        result: str = ""
        for tkn in self._flat_data:
            if category and category != tkn.category:
                continue
            if not getattr(tkn, mode, lambda x: False)(arg):
                continue
            if len(result) == 0:
                result = tkn

            match if_multiple_react:
                case 'first':
                    return result
                case 'last':
                    result = tkn
                case 'error':
                    raise RuntimeError("Multiple matches")
                case 'default':
                    return default
                case None:
                    return None
                case 'in_str_list':
                    result += f"|{tkn}"
        if not result:
            return default
        return result

    def get_match(self, arg: str, **kwargs) -> str|Any:
        return self.search(arg, mode='match', **kwargs)

    def get_find(self, arg: str, **kwargs) -> str|Any:
        return self.search(arg, mode='find', **kwargs)
