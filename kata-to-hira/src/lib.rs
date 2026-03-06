use std::io::{self, Read};

// katakana - OFFSET = hiragana equivalent
const OFFSET: u32 = 0x60;

fn to_hiragana(c: char) -> char {
    if ('ァ'..='ヶ').contains(&c) {
        char::from_u32(c as u32 - OFFSET).expect("katakana invariant")
    } else {
        c
    }
}

pub fn kata_to_hira(s: &str) -> String {
    s.chars().map(to_hiragana).collect()
}

pub fn run() -> io::Result<()> {
    let mut buffer = String::new();
    io::stdin().read_to_string(&mut buffer)?;
    println!("{}", kata_to_hira(&buffer));
    Ok(())
}
