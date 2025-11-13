typedef enum {
	// --- MAIN ---
	EOF, UNKNOWN,

	// --- TEXT TYPES ---
	STRING,IDENTIFIER, 

	// --- NUMBER TYPES ---
	NUM, DEC_NUM, PERC,

	// --- DELIMS ---
	LBRACKET, RBRACKET,
	LPAREN, RPAREN,
	LBRACE, RBRACE,
	SEPERATOR, TERMINATOR, LINEBREAK,

	// --- CONNECTORS ---
	PIPE, ALTER_PIPE, AMP, COLON, PERIOD,

	// --- OPERATORS
	PLUS, MINUS, X, SLASH, DSLASH,

	// --- TRIGGERS ---
	QMARK, EXCLAM,
	AT, DOLLAR, HASH,

	// --- MOD-SYMS ---
	STAR, CAP, FLOOR,
} TokenType;

typedef struct DcrToken {
	TokenType type;
	char *value;
} DcrToken;

typedef struct DcrPoint

typedef struct Lexer {
	const char *source;
	int pos;
} Lexer;



char getbuf(Lexer *lx) {
	char c = lx->source[lx->pos];
	if (c == '\0') return '\0';
	return c;
}

void init(DcrLexer *lx, const char *src) {
	lx->source=src;
	lx->pos=0;
	lx->start.row=0;
	lx->start.col=0;
}

char peak_ahead(DcrLexer *lx, int mod) {
	char c=lx->source
}

void run(Lexer *lx) {
}
