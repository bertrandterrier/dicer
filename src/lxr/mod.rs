mod lxr;
mod tkn;
pub use lxr::*;

#[cfg(test)]
mod test {
    use super::*;

    const EXAMPLE_SOURCE: &'static str = "#dcr!
!<show=dices>d6; roll standard D6 dice with `(1 2 3 4 5 6)` displayed as `\"󱅊 , 󱅋 , ..\"`
special_dice = #dice(0xf0787, `\\hf15c1`, \"\", \"\\treasure\"); all displayed \"󰞇 , 󱗁 , 󰜦 \"
gandulf_the_great = #!heroe{ name: \"Gandulf\" }; also callable via $Gandulf or @heroes:Gandulf";

    #[test]
    fn lexer_test() -> std::result::Result<(), crate::error::ScanError> {
        println!("::: LEXER TEST\n");
        let src: Vec<char> = EXAMPLE_SOURCE
            .chars()
            .map(|c| c)
            .collect();
        let mut l = Lexer::new(&src);

        let mut counter: usize = 0;

        while let Some(r) = l.next() {
            let start = format!(" {:o>3};{:o>3}]", r.start.line, r.stop.column);
            let stop = format!("[{:o>3};{:o>3}", r.stop.line, r.stop.column);
            println!("{} {:?}\n\t└──{}", start, r.kind, stop);

            if counter > 99 {
                return Err(crate::error::ScanError::Timeout(
                    format!("{}", l.get_debug_buff())
                ));
            } else {
                counter += 1
            }
        };
        println!("::: End of stream");
        return Ok(())
    }
}
