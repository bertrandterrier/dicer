typedef enum TokenGroup {
	GRP_BASE_TYPE,

	GRP_DELIM,
	GRP_PAIR,
	GRP_REAL_PAIR,

	GRP_MATH_OP,
	GRP_EVAL_OP,
	GRP_CONNECT,
	GRP_STRONG_CONNECT,
	GRP_WEAK_CONNECT,

	GRP_ESC_SEQ,

	GRP_IGNORABLE,
} TokenGroup;

typedef enum TokenType {
	// Base types
	TKN_FLOAT,
	TKN_INTEGER,
	TKN_RAW_STRING,
	TKN_STRING,

	// --- DELIMITERS ---
	// Solo delimiters
	TKN_SEP,
	TKN_TERM,

	// Unreal pair delimiters
	TKN_SQUOTE,
	TKN_DQUOTE,
	TKN_TRIPLE_SQUOTE,
	TKN_TRIPLE_DQUOTE,

	// Real pair delimiters
	TKN_LPAR,
	TKN_RPAR,
	TKN_LBRACKET,
	TKN_RBRACKET,
	TKN_LBRACE,
	TKN_RBRACE,
	TKN_LRULE_DELIM,
	TKN_RRULE_DELIM,

	// --- OPERATORS ---
	// Strong connective operators
	TKN_NOT,
	TKN_EQUAL,
	TKN_PLUS,
	TKN_MINUS,
	TKN_SLASH,
	TKN_X_OP,
	TKN_GREATER_THAN,
	TKN_SMALLER_THAN,

	// Weak connective operators
	TKN_PERIOD,
	TKN_COLON,
	TKN_STAR,
	TKN_TOP,
	TKN_USCORE,
	
	// --- TRIGGER SYMBOLS ---
	TKN_AT,
	TKN_QMARK,
	TKN_EXCLAM,
	TKN_HASH,
	TKN_PESO,
	TKN_AMP,
	TKN_PERC,

	// --- ESCAPE SEQUENCES ---
	// Escape Symbol
	TKN_ESC,

	// Standard escape characters
	TKN_NEWLINE,
	TKN_TAB,

	// Dicer Escape sequences
	TKN_SPACE,
	TKN_ALTERT,
	TKN_DEL,

	// --- OTHER ---
	TKN_COMMENT,
	TKN_IDENTIFIER,
} TokenType;

typedef struct Point {
	int row;
	int col;
} Point;

typedef struct DcrToken {
	TokenType type;
	TokenGroup* groups;
	int group_count;

	Point start;
	Point stop;
} DcrToken;

typedef struct DcrNode {
	char* name;
	Point start;
	Point stop;

	int child_count;
	struct DcrNode** children;
} DcrNode;
