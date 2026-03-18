use std::{ ops, cmp::{ self, Ordering as Ord } };

#[derive(Debug)]
pub struct Point(pub usize, pub usize);

impl Point {
    pub fn new() -> Self {
        Self(0_usize, 0_usize)
    }
}

impl cmp::PartialEq for Point {
    fn eq(&self, rhs: &Point) -> bool {
        (self.0 == rhs.0) && (self.1 == rhs.1)
    }
    fn ne(&self, rhs: &Point) -> bool {
        (self.0 != rhs.0) || (self.1 != rhs.1)
    }
}

impl Clone for Point {
    fn clone(&self) -> Self {
        Point(self.0, self.1)
    }
}

impl Copy for Point{}

impl cmp::PartialOrd for Point {
    fn partial_cmp(&self, rhs: &Point) -> Option<Ord> {
        match (self.0.partial_cmp(&rhs.0), self.1.partial_cmp(&rhs.1)) {
            (Some(Ord::Equal), Some(x)) => Some(x),
            (Some(y), Some(_)) => Some(y),
            _ => None
        }
    }
}

impl ops::Add for Point {
    type Output = Self;
    fn add(self, rhs: Point) -> Self::Output {
        Point(self.0 + rhs.0, self.1 + rhs.1)
    }
}

impl ops::AddAssign for Point {
    fn add_assign(&mut self, rhs: Self) {
        self.1 += rhs.1
    }
}

pub struct Span<P>(pub P, pub P); 

impl<P> Span<P>
where P: cmp::PartialOrd + ops::Add + std::fmt::Debug + Copy 
{
    pub fn new(strict: bool, start: P, stop: P) -> Self {
        if start > stop && strict {
            panic!("Expected STOP({:?}) being greater or equal to START({:?})", stop, start)
        } else if start > stop {
            Span(stop, start)
        } else {
            Span(start, stop)
        }
    }
    pub fn contains(&self, p: &P) -> bool {
        p >= &self.0 && p <= &self.1
    }
}

impl<P> ops::AddAssign<usize> for Span<P>
where P: ops::AddAssign<usize>
{
    fn add_assign(&mut self, rhs: usize) {
        self.1 += rhs
    }
}
