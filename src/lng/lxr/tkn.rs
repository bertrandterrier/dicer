pub enum Token {
    Misc(char),
    EoF,
    Name(String),
    Signal,

    // Literals
    String(String),
    Quote(Vec<u8>),
    Number(i64),
}
