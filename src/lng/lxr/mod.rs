pub mod tkn;

use crate::aux::pos::{ Point, Span };

pub struct Lexer<'a> {
    src: &'a [char],
    pos: usize,
    cursor: Point,
    buff: Option<tkn::Token>,
}

impl<'a> Lexer<'a> {
    pub fn new(src: &'a [char]) -> Self {
        Self { src,
            cursor: Point(0, 0),
            pos: 0,
            buff: None
        }
    }
    pub fn carr_advance(&mut self, linefeed: bool, expand_tab: bool) {
        self.pos += 1;
        if linefeed {
            self.cursor.0 += 1;
            self.cursor.1 = 0;
        } else if expand_tab {
            self.cursor += Point(0, 4);
        } else {
            self.cursor += Point(0, 1);
        };
    }
    pub fn lookahead(&mut self) -> Option<&char> {
        let c = self.src.get(self.pos)?;
        self.carr_advance(c == &'\n', c == &'\t');
        Some(c)
    }
    pub fn peak_forward(&mut self) -> Option<&char> {
        self.src.get(self.pos)
    }
    pub fn peak_backward(&mut self) -> Option<&char> {
        if self.pos < 1 {
            None
        } else {
            self.src.get(self.pos - 1)
        }
    }
    fn find_next_tkn(&mut self) -> Option<tkn::Token> {
        let (pos, cursor) = (self.pos, self.cursor);

        if let Some(c) = self.lookahead() {
            Some(match c {
                '\0' => tkn::Token::EoF,
                '\n' | '\t' | ' ' => return self.next(),
                _ => tkn::Token::Misc(*c),
            })
        } else {
            None
        }
    }
}

impl<'a> Iterator for Lexer<'a> {
    type Item = tkn::Token;

    fn next(&mut self) -> Option<Self::Item> {
    }
}
