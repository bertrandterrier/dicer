from dicer import lexer
from dicer.lexer import *

def get_comment(lxr: DcrLexer,
                token_type: DcrTokenType) -> None:
    cache, buf = ["", ""]
    state: int = 2      # 2: running, 1: success, 0: fail

    while state > 1:
        ...
    if state < 1:
        raise SyntaxError("Invalid comment syntax")
    
    return
