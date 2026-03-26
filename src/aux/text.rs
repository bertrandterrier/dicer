pub trait Text {
    fn trunc(&self, max: usize, repl: &str) -> String;
    fn trunc_back(&self, max: usize, repl: &str) -> String;
    fn trunc_front(&self, max: usize, repl: &str) -> String;
    fn trunc_middle(&self, max: usize, repl: &str) -> String;
}

impl<'a, S: ToString> Text for S {
    fn trunc(&self, max: usize, repl: &str) -> String {
        self.trunc_front(max, repl)
    }
    fn trunc_front(&self, max: usize, repl: &str) -> String {
        format!("{}{}", 
            self.to_string()
                .chars()
                .take(max)
                .collect::<String>(),
            repl
        )
    }
    fn trunc_back(&self, max: usize, repl: &str) -> String {
        format!("{}{}", repl,
            self.to_string()
                .chars()
                .rev()
                .take(max - repl.len())
                .collect::<String>())
    } 
    fn trunc_middle(&self, max: usize, repl: &str) -> String {
        let s = self.to_string();
        let max_len: f64 = {
            if s.len() >= max { return s }
            else {
                ((max - std::cmp::min(max, repl.len())) as f64) / 2_f64
            }
        };
        format!("{}{}{}",
            s.chars()
                .take(max_len.ceil() as usize)
                .collect::<String>(),
            repl,
            s.chars()
                .rev()
                .take(max_len.floor() as usize)
                .collect::<String>()
        )
    }
}
