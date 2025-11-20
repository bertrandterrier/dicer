from dicer.lexer import *
from dicer.schemes import *

dcrlexer: DcrLexer = DcrLexer()


def get_comment(lxr: Lexer, data: TokenData) -> Lexer:
    started = False
    expect: str = '<'
    while not dcrlexer(EOF):
        while dcrlexer(SPACE):
            lxr = dcrlexer.advance(lxr, True)
        if dcrlexer('<'):
            jump = 1
            if not dcrlexer.peak_ahead("~"):
                raise SyntaxError()
            while dcrlexer("~"):
                lxr = dcrlexer.advance(lxr, False)
            while dcrlexer(SPACE):
                lxr = dcrlexer.advance(lxr, True)
            if dcrlexer(NEWLINE):
                dcrlexer.advance(lxr, True)
                dcrlexer.mark_type(lxr, TokenData.get('lcmt'))
            return lxr
    return


def init(src: str) -> Lexer:
    lxr: Lexer = dcrlexer.init_lexer(src)
    return lxr
