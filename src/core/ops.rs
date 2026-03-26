/// Operation signal.
#[derive(Clone, Copy)]
pub enum Signal {
    AngleLeft,
    AngleRight,
    At,
    Bar,
    Comma,
    Dash,
    Equal,
    Et,
    ExclamMark,
    Caret,
    Period,
    Peso,
    Plus,
    Pound,
    Slash,
    Star,
    QuestMark,
}

impl Signal {
    const REG: &'static[(char, Self)] = &[
	('<', Self::AngleLeft),
	('>', Self::AngleRight),
	('@', Self::At),
	('|', Self::Bar),
	(',', Self::Comma),
	('-', Self::Dash),
	('=', Self::Equal),
	('&', Self::Et),
	('!', Self::ExclamMark),
	('^', Self::Caret),
	('.', Self::Period),
	('$', Self::Peso),
	('+', Self::Plus),
	('#', Self::Pound),
	('/', Self::Slash),
	('*', Self::Star),
	('?', Self::QuestMark),
    ];
}

impl TryFrom<&char> for Signal {
    type Error = ();
    fn try_from(src: &char) -> Result<Self, Self::Error> {
        Ok(Self::REG
            .iter()
            .find(|(c, _)| c == src)
            .ok_or(())?
            .1)
    }
}
