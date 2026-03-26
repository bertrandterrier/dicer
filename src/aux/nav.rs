use std::cmp::{ Ordering };
use std::ops::{ Add, AddAssign, Deref, DerefMut };
use std::fmt::{ Debug };

#[derive(Debug)]
pub struct Point<X, Y>(pub X, pub Y); 

impl<X, Y> PartialEq for Point<X, Y>
where
    X: PartialEq,
    Y: PartialEq,
{
    fn eq(&self, rhs: &Self) -> bool {
        self.0 == rhs.0 && self.1 == rhs.1
    }
    fn ne(&self, rhs: &Self) -> bool {
        self.0 != rhs.0 || self.1 != rhs.1
    }
}

impl<X, Y> Clone for Point<X, Y>
where
    X: Clone,
    Y: Clone,
{
    fn clone(&self) -> Self {
        Self(self.0.clone(), self.1.clone())
    }
}

impl<X, Y> Copy for Point<X, Y>
where
    X: Copy,
    Y: Copy,
{}

impl<X, Y> Eq for Point<X, Y> where X: Eq, Y: Eq, {}

impl<X: PartialOrd, Y: PartialOrd> PartialOrd for Point<X, Y> {
    fn partial_cmp(&self, rhs: &Self) -> Option<Ordering> {
        Some({
            match (self.0.partial_cmp(&rhs.0), self.1.partial_cmp(&rhs.1)) {
                (None, _) | (_, None) => return None,
                (Some(Ordering::Less), Some(Ordering::Greater)) | (Some(Ordering::Greater), Some(Ordering::Less)) => return None,
                (Some(x), Some(y)) => {
                    if x == y { x }
                    else if x == Ordering::Equal { y }
                    else { x }
                }
            }
        })
    }
}

impl<X, Y> Ord for Point<X, Y>
where
    X: Ord,
    Y: Ord,
{
    fn cmp(&self, rhs: &Self) -> Ordering {
        match self.partial_cmp(&rhs) {
            Some(r) => r,
            None => self.0.cmp(&self.0)
        }
    }
}

impl<X, Y> Add for Point<X, Y>
where
    X: Add<Output = X>,
    Y: Add<Output = Y>,
{
    type Output = Self;
    fn add(self, rhs: Point<X, Y>) -> Self::Output {
        let x = self.0 + rhs.0;
        let y = self.1 + rhs.1;
        Point(x, y)
    }
}

pub struct Span<P>
where
    P: Ord,
{
    pub strict: bool,
    start: P,
    stop: P 
}

impl<P> Span<P>
where
    P: Ord + Debug,
{
    pub fn new(strict: bool, start: P, stop: P) -> Self {
        match start.cmp(&stop) {
            Ordering::Greater => {
                if strict {
                    panic!("Expected START({:?}) being equal or less than STOP({:?})", start, stop)
                } else {
                    Span { strict, start: stop, stop: start }
                }
            }
            _ => Span { strict, start, stop }
        }
    }
    pub fn stop(&self) -> &P {
        &self.stop
    }
    pub fn start(&self) -> &P {
        &self.start
    }
}

#[derive(Clone, Copy, Debug)]
pub struct TextPoint {
    pub line: usize,
    pub column: usize,
}

impl TextPoint {
    pub fn new(line: usize, column: usize) -> Self {
        Self { line, column }
    }
    pub fn linefeed(&mut self) {
        self.line += 1;
        self.column = 0;
    }
    pub fn colfeed(&mut self) {
        self.column += 1;
    }
}

impl PartialEq for TextPoint {
    fn eq(&self, rhs: &Self) -> bool {
        self.column == rhs.column && self.line == rhs.line
    }
}

impl Eq for TextPoint {}

impl PartialOrd for TextPoint {
    fn partial_cmp(&self, rhs: &Self) -> Option<Ordering> {
        match self.line.partial_cmp(&rhs.line) {
            Some(Ordering::Equal) => self.column.partial_cmp(&rhs.column),
            Some(l) => Some(l),
            _ => None,
        }
    } 
}

impl Ord for TextPoint {
    fn cmp(&self, rhs: &Self) -> Ordering {
        match (self.line.cmp(&rhs.line), self.column.cmp(&rhs.column)) {
            (Ordering::Equal, c) => c,
            (l, _) => l,
        }
    }
}

#[derive(Debug)]
pub struct Cursor {
    idx: usize,
    pt: TextPoint,
}

impl Cursor {
    pub fn new() -> Self {
        Self { idx: 0, pt: TextPoint { line: 0, column: 0 } }
    }
    /// * `idx: usize` -- Actual character position. 
    /// * `col: usize` -- Virtual column.
    /// * `line: usize` -- Virtual line.
    pub fn setup(idx: usize, line: usize, column: usize) -> Self {
        Self { idx, pt: TextPoint { line, column } }
    }
    pub fn index(&self) -> &usize { &self.idx }
    pub fn point(&self) -> &TextPoint {
        &self.pt
    }
    pub fn line(&self) -> &usize { &self.pt.line }
    pub fn column(&self) -> &usize { &self.pt.column }
    pub fn as_point(&self) -> &TextPoint {
        &self.pt
    }
}

impl Clone for Cursor {
    fn clone(&self) -> Self {
        Cursor::setup(*self.index(), *self.line(), *self.column())
    }
}

impl Copy for Cursor {}

impl Deref for Cursor {
    type Target = TextPoint;
    fn deref(&self) -> &Self::Target {
        &self.pt
    }
}

impl DerefMut for Cursor {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.pt
    }
}

impl PartialEq for Cursor {
    fn eq(&self, rhs: &Self) -> bool {
        self.idx == rhs.idx && self.pt == rhs.pt
    }
}

impl Eq for Cursor {}

impl PartialOrd for Cursor {
    fn partial_cmp(&self, rhs: &Self) -> Option<Ordering> {
        self.idx.partial_cmp(&rhs.idx)
    }
}

impl Ord for Cursor {
    fn cmp(&self, rhs: &Self) -> Ordering {
        self.idx.cmp(&rhs.idx)
    }
}
