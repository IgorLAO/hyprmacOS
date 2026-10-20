//! Núcleo de normalização e ranking da busca Spotlight, sem GTK ou IPC.
mod calc;
mod filters;
use regex::Regex;
use serde_json::json;
use std::ffi::{c_char, CStr};
use std::sync::LazyLock;
use unicode_normalization::{char::canonical_combining_class, UnicodeNormalization};

static NAME_WORDS: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"[\s\-_.()/]+").unwrap());
static EXTRA_WORDS: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"[\s\-_.()/;]+").unwrap());

fn file_kind(word: &str) -> Option<&'static str> {
    match word.to_ascii_lowercase().as_str() {
        "pdf" | "pdfs" => Some("pdf"),
        "image" | "images" => Some("image"),
        "folder" | "folders" => Some("folder"),
        _ => None,
    }
}

pub fn file_query(input: &str) -> (String, Vec<&'static str>) {
    let mut kinds = Vec::new();
    let mut words = Vec::new();
    for word in input.split_whitespace() {
        if word.get(..5).is_some_and(|prefix| prefix.eq_ignore_ascii_case("kind:")) {
            let suffix = &word[5..];
            if suffix.bytes().all(|byte| byte.is_ascii_alphabetic()) {
                if let Some(kind) = file_kind(suffix) {
                    kinds.push(kind);
                    continue;
                }
            }
        }
        words.push(word);
    }
    if let Some(first) = words.first().and_then(|word| file_kind(word)) {
        kinds.push(first);
        words.remove(0);
    }
    let mut unique = Vec::new();
    for kind in kinds {
        if !unique.contains(&kind) { unique.push(kind); }
    }
    (words.join(" "), unique)
}

unsafe fn write_output(value: &str, output: *mut c_char, capacity: usize) -> usize {
    let bytes = value.as_bytes();
    if !output.is_null() && capacity > bytes.len() {
        unsafe {
            std::ptr::copy_nonoverlapping(bytes.as_ptr(), output.cast::<u8>(), bytes.len());
            *output.add(bytes.len()) = 0;
        }
    }
    bytes.len()
}

pub fn fold(input: &str) -> String {
    input.to_lowercase().nfkd().filter(|character| canonical_combining_class(*character) == 0).collect()
}

fn words(input: &str, include_semicolon: bool) -> Vec<&str> {
    let pattern = if include_semicolon { &*EXTRA_WORDS } else { &*NAME_WORDS };
    pattern.split(input).filter(|word| !word.is_empty()).collect()
}

pub fn score(query: &str, name: &str, extra: &str) -> f64 {
    let normalized = fold(name);
    if query.is_empty() { return 1.0; }
    if normalized == query { return 100.0; }
    if normalized.starts_with(query) {
        return 90.0 - (normalized.chars().count() - query.chars().count()).min(30) as f64 * 0.1;
    }
    let parts = words(&normalized, false);
    if parts.iter().any(|part| part.starts_with(query)) { return 75.0; }
    if query.chars().count() > 1 && parts.iter().filter_map(|part| part.chars().next()).collect::<String>().starts_with(query) {
        return 70.0;
    }
    if normalized.contains(query) { return 60.0; }
    let query_parts = query.split_whitespace().collect::<Vec<_>>();
    if query_parts.len() > 1 {
        if normalized.replace(' ', "").contains(&query.replace(' ', "")) { return 58.0; }
        if query_parts.iter().all(|word| normalized.contains(word)) { return 50.0; }
    }
    if !extra.is_empty() {
        let extra = fold(extra);
        if words(&extra, true).iter().any(|word| word.starts_with(query)) { return 55.0; }
        if query.chars().count() > 2 && extra.contains(query) { return 35.0; }
    }
    if query.chars().count() >= 4 && normalized.chars().next() == query.chars().next() {
        let mut remaining = normalized.chars();
        if query.chars().all(|character| remaining.by_ref().any(|candidate| candidate == character)) { return 18.0; }
    }
    0.0
}

fn c_input(pointer: *const c_char) -> String {
    if pointer.is_null() { return String::new(); }
    unsafe { CStr::from_ptr(pointer) }.to_string_lossy().into_owned()
}

/// # Safety
/// `input` must be a valid NUL-terminated string. If `output` is non-null and
/// `capacity` exceeds the returned length, it must reference writable memory.
#[no_mangle]
pub unsafe extern "C" fn hyprmac_spot_fold(input: *const c_char, output: *mut c_char, capacity: usize) -> usize {
    let normalized = fold(&c_input(input));
    unsafe { write_output(&normalized, output, capacity) }
}

/// # Safety
/// `input` must be a valid NUL-terminated string; `output` must reference
/// `capacity` writable bytes when non-null.
#[no_mangle]
pub unsafe extern "C" fn hyprmac_spot_file_query(input: *const c_char, output: *mut c_char, capacity: usize) -> usize {
    let (query, kinds) = file_query(&c_input(input));
    let result = json!([query, kinds]).to_string();
    unsafe { write_output(&result, output, capacity) }
}

/// # Safety
/// `input` must point to NUL-terminated JSON. If `output` is non-null, it must
/// reference `capacity` writable bytes. Returns the required output length.
#[no_mangle]
pub unsafe extern "C" fn hyprmac_spot_filters(input: *const c_char, output: *mut c_char, capacity: usize) -> usize {
    let request = serde_json::from_str(&c_input(input)).unwrap_or(serde_json::Value::Null);
    let result = filters::dispatch(&request).to_string();
    unsafe { write_output(&result, output, capacity) }
}

/// # Safety
/// `input` must be a valid NUL-terminated string; `output` must reference
/// `capacity` writable bytes when non-null. Returns -1 when Python should
/// evaluate an unusual precision case, 0 for an invalid expression, otherwise
/// the required byte count.
#[no_mangle]
pub unsafe extern "C" fn hyprmac_spot_calc(input: *const c_char, output: *mut c_char, capacity: usize) -> isize {
    match calc::calculate(&c_input(input)) {
        calc::CalcResult::Invalid => 0,
        calc::CalcResult::Unsupported => -1,
        calc::CalcResult::Text(result) => unsafe { write_output(&result, output, capacity) as isize },
    }
}

/// # Safety
/// Every non-null input must point to a valid NUL-terminated string.
#[no_mangle]
pub unsafe extern "C" fn hyprmac_spot_score(query: *const c_char, name: *const c_char, extra: *const c_char) -> f64 {
    score(&c_input(query), &c_input(name), &c_input(extra))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn accented_names_match_normalized_queries() {
        assert_eq!(fold("Ações"), "acoes");
        assert_eq!(score("acoes", "Ações", ""), 100.0);
    }

    #[test]
    fn ranking_keeps_name_over_extra_and_word_initials() {
        assert!(score("goo", "Google Chrome", "") > score("goo", "Chrome", "Google"));
        assert_eq!(score("term", "Ghostty", "Terminal"), 55.0);
        assert_eq!(score("gc", "Google Chrome", ""), 70.0);
    }

    #[test]
    fn file_type_tokens_preserve_other_query_words() {
        assert_eq!(file_query("Report kind:pdf kind:images"), ("Report".into(), vec!["pdf", "image"]));
        assert_eq!(file_query("pdf Report kind:pdf"), ("Report".into(), vec!["pdf"]));
        assert_eq!(file_query("mykind:pdf"), ("mykind:pdf".into(), vec![]));
    }
}
