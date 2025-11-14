from pathlib import Path
from typing import Callable
import yaml

import dicer as dcr
from dicer import lexer

def read_tkn_types(_path: str|Path=dcr.DCR_DATA_SHARED,
                   _needed_keys: list[str] = ['name', 'id'],
                   _formatter: dict[str, Callable[..., str]] = {
                        'name': lambda x: str(x).upper()
                    }) -> list[dict]:
    """Read token types from a yaml.
    """
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

def write_tkns(file: str|Path,
               data: list[lexer.DcrToken],
               force_write: bool = False):
    """Write token list to yaml.
    """
    path = Path(file)
    if path.exists() and not force_write:
        raise FileExistsError()
    with open(path, 'w') as f:
        yaml.dump(data, f)
