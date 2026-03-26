use thiserror::Error;

#[derive(Error, Debug)]
pub enum ScanError {
    #[error("Invalid character: `{0}`.")]
    InvalChar(char),
    #[error("End of stream.")]
    EoF,
    #[error("No match in PreMark for `{0}`")]
    NoPreMarkMatch(char),
    #[error("No match in `{0}` for `{1}`")]
    NoStrMatch(&'static str, String),
    #[error("No match in `{0}` for `{1}`")]
    NoCharMatch(String, char),
    #[error("No EoF found..")]
    NoEoF,
    #[error("Lexer needed too long. Buffer: {0}")]
    Timeout(String),
}
