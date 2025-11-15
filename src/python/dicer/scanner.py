import dicer as dcr
from dicer.lexer import *
from dicer.tokens import TokenData, EOF

lexer: LexHandler = LexHandler()


def get_tokens(dcrlexer: DcrLexer,
               data: TokenData) -> list[DcrToken]:
    result: list[DcrToken] = []

    while not lexer(EOF):
        if lexer("\\"):
            lexer.advance(dcrlexer, True)
            lexer.advance(dcrlexer, False)
        elif lexer("<") and lexer.peak_ahead("~"):
            lexer.advance(dcrlexer, True)
            while not lexer("\n"):
                lexer.advance(dcrlexer, True)
            lexer.mark_type(dcrlexer,)
            lexer.advance(dcrlexer, False)



    return result

def init(source_file: str,
         data_file: str = str(dcr.DCR_DATA_SHARED)):
    with open(source_file, 'r') as f:
        src = f.read()
    
    raw_tkn_data = dcr.io.read_yaml(data_file)

    data = TokenData(raw_tkn_data)

    dcr_lxr = lexer.init_lexer(src)
    result: list[DcrToken] = get_tokens(dcrLexer, data)
    return
