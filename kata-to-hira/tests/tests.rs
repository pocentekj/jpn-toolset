use kata_to_hira::kata_to_hira;

#[test]
fn test_kata_to_hira() {
    assert_eq!(kata_to_hira("abcde", None), "abcde");

    assert_eq!(kata_to_hira("ヴ", None), "ゔ");

    assert_eq!(kata_to_hira("アイウエオ", None), "あいうえお");

    assert_eq!(
        kata_to_hira("ャュョァィゥェォッ", None),
        "ゃゅょぁぃぅぇぉっ"
    );

    assert_eq!(
        kata_to_hira("Rustでアイウエオを書く", None),
        "Rustであいうえおを書く"
    );

    assert_eq!(kata_to_hira("ー。、！？", None), "ー。、！？");

    for code in 'ァ' as u32..='ヶ' as u32 {
        let c = char::from_u32(code).unwrap();
        let converted = kata_to_hira(&c.to_string(), None);

        let expected = char::from_u32(code - 0x60).unwrap().to_string();

        assert_eq!(converted, expected);
    }
}
