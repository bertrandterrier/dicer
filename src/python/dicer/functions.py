from typing import NoReturn, Any
def break_process(msg: str|None = None,
                  exc: Exception|None = None) -> NoReturn:
    msg = msg or ""
    if isinstance(exc, Exception):
        raise exc
    else:
        raise RuntimeError(msg)

