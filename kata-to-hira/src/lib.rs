use std::io::{self, Read};

// katakana - OFFSET = hiragana equivalent
const OFFSET: u32 = 0x60;

fn is_kata(c: char) -> bool {
    ('ァ'..='ヶ').contains(&c)
}

fn to_hiragana(c: char) -> char {
    if is_kata(c) {
        char::from_u32(c as u32 - OFFSET).expect("katakana invariant")
    } else {
        c
    }
}

pub fn kata_to_hira(s: &str, color: Option<bool>) -> String {
    let color = color.unwrap_or(false);

    if color {
        let mut last_is_kata = false;
        let mut out = String::new();

        for ch in s.chars() {
            let is_kata = is_kata(ch);

            if is_kata && !last_is_kata {
                out.push_str("\x1b[31m");
            }

            out.push(if is_kata { to_hiragana(ch) } else { ch });

            if !is_kata && last_is_kata {
                out.push_str("\x1b[0m");
            }

            last_is_kata = is_kata;
        }

        if last_is_kata {
            out.push_str("\x1b[0m");
        }

        return out;
    }

    s.chars().map(to_hiragana).collect()
}

pub fn run() -> io::Result<()> {
    let color = std::env::args().skip(1).any(|arg| arg == "--color");
    let mut buffer = String::new();
    io::stdin().read_to_string(&mut buffer)?;
    println!("{}", kata_to_hira(&buffer, Some(color)));
    Ok(())
}
