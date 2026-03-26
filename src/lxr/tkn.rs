use crate::aux::nav::{ Cursor };

#[derive(Debug)]
pub enum PrefixMark {
    AsStruct,           // #
    MetaStruct,         // #:
    MetaStructMod,      // #!
    CastStructElems,    // #?
    AsRun,              // &
    MetaRunMod,         // &!
    MetaRun,            // &:
    CastRunElems,       // &?
    Catch,              // $
    Cast,               // @
}

#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub enum Bracket {
    ParenL,
    ParenR,
    SquareL,
    SquareR,
    AngleL,
    AngleR,
    BraceL,
    BraceR,
    MathL,
    MathR,
}

impl Bracket {
    const REG: &'static[(char, char, Self, Self)] = &[
        ('<', '>', Self::AngleL,    Self::AngleR),
        ('[', ']', Self::SquareL,   Self::SquareR),
        ('{', '}', Self::BraceL,    Self::BraceR),
        ('(', ')', Self::ParenL,    Self::ParenR),
        ('⟨', '⟩', Self::MathL,     Self::MathR),
    ];
    pub fn as_str(&self) -> &'static char {
        let (cl, cr, bl, _)= Self::REG
            .iter()
            .find(|(_, _, l, r)| l == self || r == self)
            .unwrap();
        if self == bl { cl }
        else { cr }
    }
}

impl From<char> for Bracket {
    fn from(src: char) -> Self {
        if let Some((cl, _, bl, br)) = Self::REG
            .iter()
            .find(|(l, r, _, _)| l == &src || r == &src)
        {
            if &src == cl { *bl }
            else { *br }
        }
        else {
            panic!("Be careful using from for brackets, if not sure to match.")
        }
    }
}

#[derive(Debug)]
pub enum TokenKind {
    EoF,

    Sign(String),
    Operator(OpMark),
    Sigil(PrefixMark),
    Control(CtrlMark),

    // Literals
    String(String),
    Quote(Vec<u8>),
    Digit(u64),

    // Delimiters
    LineTerm,
    Seperator,
    Bracket(Bracket),
}

#[derive(Debug)]
pub enum CtrlMark {
    Assign,         // =    :=
    AddAssign,      // +=
    SubAssign,      // -=
    ApplyAssign,    // *=
    ConsumeAssign,  // /=
    AltAssign,      // |=
    Pipe,           // ::
    AltPipe,        // |:
    AltExclude,     // |-
    AltMod,         // |+
    AltFieldMod,    // |*
}

#[derive(Debug)]
pub enum OpMark {
    Exec,           // !
    Query,          // ?
    Connect,        // .
    Access,         // :
    Span,           // ..
    Add,            // +
    Subtract,       // -
    Apply,          // **
    Expand,         // *
    Consume,        // //
    CeilFunc,       // /*   /^
    FloorFunc,      // /.   /_
    Limit,          // ^
    TopLimit,       // ^^   ^*
    BottomLimit,    // ^_   ^.
    Relate,         // %
}
#[derive(Debug)]
pub struct Token {
    kind: TokenKind,
    start: Cursor,
    stop: Cursor,
}

impl std::fmt::Display for Token {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "[{:>3},{:>3}] {:?}\n ┗━[{:>3},{:>3}]",
            self.start.line,
            self.start.column,
            self.kind,
            self.stop.line,
            self.stop.column,
        )
    }
}
