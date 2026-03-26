pub enum Element {
    Null,

    // Base forms 
    String(String),
    Quote(Vec<u8>),

    Integer(i64),
    Float(f64),

    // Collections
    Serial,
    Array,
    Table,
    Map,
    Sheet,

    // Expressions
}

pub enum Form {
    Elem(Element),
    Operation,
    Assignment,
}
