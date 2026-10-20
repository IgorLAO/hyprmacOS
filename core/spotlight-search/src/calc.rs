//! Avaliador restrito das contas digitadas no Spotlight.
//! Recusa expressões fora do contrato antigo; valores de precisão incerta
//! voltam ao avaliador Python durante a migração da view GTK.
use regex::Regex;
use std::sync::LazyLock;

static PERCENT: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^\s*([\d.]+)\s*%\s*(?:de|of)\s*([\d.]+)\s*$").unwrap());
static VALID: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^[\d.\s+\-*/()%]+$").unwrap());
static OPERATOR: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\d\s*[-+*/%]").unwrap());

#[derive(Debug, PartialEq)]
pub enum CalcResult { Invalid, Unsupported, Text(String) }

struct Parser<'a> { bytes: &'a [u8], cursor: usize }
impl<'a> Parser<'a> {
    fn new(input: &'a str) -> Self { Self { bytes: input.as_bytes(), cursor: 0 } }
    fn spaces(&mut self) {
        while self.bytes.get(self.cursor).is_some_and(u8::is_ascii_whitespace) { self.cursor += 1; }
    }
    fn eat(&mut self, token: u8) -> bool {
        self.spaces();
        if self.bytes.get(self.cursor) == Some(&token) { self.cursor += 1; true } else { false }
    }
    fn two_stars(&mut self) -> bool {
        self.spaces();
        if self.bytes.get(self.cursor..self.cursor+2) == Some(b"**".as_slice()) { self.cursor += 2; true } else { false }
    }
    fn expression(&mut self) -> Option<f64> {
        let mut value = self.term()?;
        loop {
            if self.eat(b'+') { value += self.term()?; }
            else if self.eat(b'-') { value -= self.term()?; }
            else { break; }
        }
        Some(value)
    }
    fn term(&mut self) -> Option<f64> {
        let mut value = self.factor()?;
        loop {
            self.spaces();
            if self.bytes.get(self.cursor..self.cursor+2) == Some(b"**".as_slice()) { break; }
            if self.eat(b'*') { value *= self.factor()?; }
            else if self.eat(b'/') { value /= self.factor()?; }
            else if self.eat(b'%') {
                let divisor = self.factor()?;
                value = value - (value / divisor).floor() * divisor;
            }
            else { break; }
            if !value.is_finite() { return None; }
        }
        Some(value)
    }
    fn factor(&mut self) -> Option<f64> {
        if self.eat(b'+') { return self.factor(); }
        if self.eat(b'-') { return self.factor().map(|value| -value); }
        self.power()
    }
    fn power(&mut self) -> Option<f64> {
        let mut value = self.atom()?;
        if self.two_stars() {
            let exponent = self.factor()?;
            if exponent.abs() > 100.0 { return None; }
            value = value.powf(exponent);
        }
        if value.is_finite() { Some(value) } else { None }
    }
    fn atom(&mut self) -> Option<f64> {
        if self.eat(b'(') {
            let value = self.expression()?;
            return self.eat(b')').then_some(value);
        }
        self.spaces();
        let start = self.cursor;
        while self.bytes.get(self.cursor).is_some_and(|byte| byte.is_ascii_digit() || *byte == b'.') { self.cursor += 1; }
        if start == self.cursor { return None; }
        let token = std::str::from_utf8(&self.bytes[start..self.cursor]).ok()?;
        if token.starts_with('0') && token.len() > 1 && !token.starts_with("0.") && !token.chars().all(|ch| ch == '0') {
            return None;
        }
        token.parse::<f64>().ok()
    }
}
fn grouped_int(value: i64) -> String {
    let text = value.to_string();
    let (sign, digits) = if let Some(rest) = text.strip_prefix('-') { ("-", rest) } else { ("", text.as_str()) };
    let mut result = String::new();
    for (index, character) in digits.chars().enumerate() {
        if index > 0 && (digits.len() - index) % 3 == 0 { result.push(' '); }
        result.push(character);
    }
    format!("{sign}{result}")
}

pub fn calculate(input: &str) -> CalcResult {
    let mut normalized = input.replace(',', ".").replace('×', "*").replace('÷', "/").replace('^', "**");
    if let Some(capture) = PERCENT.captures(&normalized) {
        normalized = format!("{}/100*{}", &capture[1], &capture[2]);
    }
    if !VALID.is_match(&normalized) || !OPERATOR.is_match(&normalized) { return CalcResult::Invalid; }
    // Python supports arbitrary-size integer powers. Keep that branch there
    // until this evaluator has an exact integer type.
    if normalized.contains("**") { return CalcResult::Unsupported; }
    // Python's AST rejects non-ASCII whitespace/numbers and comments here; let it
    // decide these rare cases until the entire search adapter is migrated.
    if !normalized.is_ascii() { return CalcResult::Unsupported; }
    let mut parser = Parser::new(&normalized);
    let Some(value) = parser.expression() else { return CalcResult::Invalid; };
    parser.spaces();
    if parser.cursor != parser.bytes.len() || !value.is_finite() { return CalcResult::Invalid; }
    if (normalized.contains('.') && (normalized.contains('%') || value.abs() > 1e4))
        || (normalized.contains('%') && normalized.contains('/')) {
        return CalcResult::Unsupported;
    }
    if value.abs() > 1e9 { return CalcResult::Unsupported; }
    let scaled = value * 1e10;
    if (scaled.fract().abs() - 0.5).abs() < 1e-7 { return CalcResult::Unsupported; }
    let rounded = scaled.round_ties_even() / 1e10;
    if rounded != 0.0 && rounded.abs() < 1e-4 { return CalcResult::Unsupported; }
    if rounded.fract() == 0.0 {
        return CalcResult::Text(grouped_int(rounded as i64));
    }
    CalcResult::Text(rounded.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn arithmetic_precedence_and_power_limit() {
        assert_eq!(calculate("12*7+1"), CalcResult::Text("85".into()));
        assert_eq!(calculate("15% de 80"), CalcResult::Text("12".into()));
        assert_eq!(calculate("-2^2"), CalcResult::Unsupported);
        assert_eq!(calculate("2^3^2"), CalcResult::Unsupported);
        assert_eq!(calculate("2^101"), CalcResult::Unsupported);
        assert_eq!(calculate("__import__('os')"), CalcResult::Invalid);
    }
}
