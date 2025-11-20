from dataclasses import dataclass, field 

from dicer.lexer import Lexer
from dicer.schemes import Point


@dataclass
class Branch:
    name: str
    start: Point
    end: Point
    payload: "str|list[Branch]|None" = None
    rules: list[dict] = field(default_factory=list)

class Tree(str):
    __slots__ = ("_name", "_start", "_end",
                 "_load")
    def __new__(cls,
                start: tuple[int, int],
                end: tuple[int, int],
                name: str = "UNKNOWN",
                payload: str|list[Branch]|None = None) -> "Tree":
        inst = super().__new__(cls, name)
        return inst

class Nursery:
    def __init__(self, root: str = "source"):
        """Manages (makes, buffers, merges) branch and builds the main Tree
        class at the end.

        root: str
            Root name. How first element is called.
            Defaults to \"source\".
        """
        self._root: str = root
        self._branches: list[Branch] = []

