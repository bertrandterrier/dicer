use crate::error::ScanError;
use crate::aux::nav::{ Cursor, TextPoint, Span };
use crate::lxr::tkn::{ self, TokenKind as Tk };

pub type Result = std::result::Result<tkn::Token, ScanError>;

/// Lexer (scanner) implemented as iterator. 
///
/// # Fields
/// * `src: &'a [char]` -- Reference to source characters.
/// * `buff: Option<Result>` -- Buffer for storing next Token.
/// * `index: usize` -- One dimensional character position.
pub struct Lexer<'a> {
    src: &'a [char],
    buff: Option<tkn::Token>,
    mark: Cursor,

    // Cursor
    idx: usize,
    pos: TextPoint,
}

impl<'a> Lexer<'a> {
    pub fn new(src: &'a [char]) -> Self {
        Self {
            src,
            buff: None,
            mark: Cursor::new(),
            idx: 0,
            pos: TextPoint::new(0, 0)
        }
    }
    pub fn get_debug_buff(&self) -> String  {
        format!("{:?}", self.buff)
    }
    pub fn carr_advance(&mut self, linefeed: bool, expand_tab: bool) {
        self.idx += 1;
        if linefeed { self.pos.linefeed() }
        else if expand_tab {
            for _ in 0..4 { self.pos.colfeed() }
        }
        else { self.pos.colfeed() }
    }
    /// Next character + moving forward.
    pub fn lookahead(&mut self) -> Option<&char> {
        let c = self.src.get(self.idx)?;
        self.carr_advance(c == &'\n', c == &'\t');
        Some(c)
    }
    /// Next character. Not moving forward.
    pub fn peak_ahead(&mut self) -> Option<&char> {
        self.src.get(self.idx)
    }
    /// Previous character if possible.
    pub fn peak_behind(&mut self) -> Option<&char> {
        if self.idx < 1 {
            None
        } else {
            self.src.get(self.idx - 1)
        }
    }
    /// Returns position as `crate::aux::nav::Cursor`.
    pub fn get_cursor(&self) -> Cursor {
        Cursor::setup(self.idx, self.pos.line, self.pos.column)
    }
    /// Retrieves next token from characters in source.
    fn consume_next(&mut self) -> Option<tkn::Token> {
        self.mark = self.get_cursor();

        let c: char = *self.lookahead()?;
        let k: Tk = match c {
            ' ' | '\t' | ',' => return self.consume_next(),
            | ';' => {
                while ['\0', '\n'].contains(self.lookahead().unwrap_or(&'.')) {
                    continue
                };
                Tk::LineTerm
            }
            '[' | '(' | '{' =>  
        }
    }
}

impl<'a> Iterator for Lexer<'a> {
    type Item = tkn::Token;

    fn next(&mut self) -> Option<Self::Item> {
        if let Some(r) = self.buff.take() {
            match r {
                Ok(s) => Some(s),
                Err(ScanError::EoF) => None,
                Err(e) => {
                    println!(">>> WARNING: {:?}", e);
                    self.next()
                }
            }
        }
        else {
            self.buff = Some(self.get_next_token());
            return self.next()
        }
    }
}
