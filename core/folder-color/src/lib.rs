//! Recoloração de ícones de pasta; a view GTK fornece os pixels e o alvo.

use serde_json::Value;
use std::sync::OnceLock;

fn parse_hex(hex: &str) -> Option<[u8; 3]> {
    let bytes = hex.strip_prefix('#')?;
    if bytes.len() != 6 || !bytes.bytes().all(|part| part.is_ascii_hexdigit()) {
        return None;
    }
    Some([
        u8::from_str_radix(&bytes[0..2], 16).ok()?,
        u8::from_str_radix(&bytes[2..4], 16).ok()?,
        u8::from_str_radix(&bytes[4..6], 16).ok()?,
    ])
}

fn palette() -> &'static Vec<(String, [u8; 3])> {
    static PALETTE: OnceLock<Vec<(String, [u8; 3])>> = OnceLock::new();
    PALETTE.get_or_init(|| {
        let data: Value = serde_json::from_str(include_str!("../../accent/palette.json"))
            .expect("paleta de destaque válida");
        data.as_array()
            .expect("paleta em lista")
            .iter()
            .filter_map(|entry| {
                Some((
                    entry["name"].as_str()?.to_owned(),
                    parse_hex(entry["light"].as_str()?)?,
                ))
            })
            .collect()
    })
}

pub fn color_from_preferences(json: &[u8]) -> Option<[u8; 3]> {
    let settings: Value = serde_json::from_slice(json).ok()?;
    let name = settings["folder_color"].as_str()?;
    if name == "choose" {
        return parse_hex(settings["folder_color_custom"].as_str()?);
    }
    palette()
        .iter()
        .find(|(key, _)| key == name)
        .map(|(_, rgb)| *rgb)
}

#[no_mangle]
/// Resolve a cor configurada usando a paleta Tahoe compartilhada.
///
/// # Safety
/// `settings` deve apontar para `len` bytes legíveis, e `out_rgb` para três bytes graváveis.
pub unsafe extern "C" fn hyprmac_folder_color(
    settings: *const u8,
    len: usize,
    out_rgb: *mut u8,
) -> bool {
    if settings.is_null() || out_rgb.is_null() {
        return false;
    }
    let input = std::slice::from_raw_parts(settings, len);
    let Some(rgb) = color_from_preferences(input) else {
        return false;
    };
    std::ptr::copy_nonoverlapping(rgb.as_ptr(), out_rgb, 3);
    true
}

pub fn tint_rgba(pixels: &mut [u8], width: usize, height: usize, stride: usize, target: [u8; 3]) {
    let base_lightness = (0.2126 * 131.0 + 0.7152 * 197.0 + 0.0722 * 229.0) / 255.0;
    let target_lightness =
        (0.2126 * target[0] as f64 + 0.7152 * target[1] as f64 + 0.0722 * target[2] as f64) / 255.0;
    for y in 0..height {
        for x in 0..width {
            let at = y * stride + x * 4;
            let pixel = &mut pixels[at..at + 4];
            if pixel[3] == 0 {
                continue;
            }
            let max = *pixel[..3].iter().max().unwrap() as f64;
            let min = *pixel[..3].iter().min().unwrap() as f64;
            // A borda quase branca e os reflexos continuam neutros.
            if max - min < 16.0 && min > 175.0 {
                continue;
            }
            let lightness =
                (0.2126 * pixel[0] as f64 + 0.7152 * pixel[1] as f64 + 0.0722 * pixel[2] as f64)
                    / 255.0;
            let ratio = (lightness / base_lightness).clamp(0.0, 1.45);
            let lift = ((lightness - target_lightness * ratio) * 0.25).max(0.0);
            for channel in 0..3 {
                pixel[channel] = (target[channel] as f64 * ratio + lift * 255.0)
                    .clamp(0.0, 255.0)
                    .round() as u8;
            }
        }
    }
}

#[no_mangle]
/// Recolore um buffer RGBA vindo do GdkPixbuf.
///
/// # Safety
/// `pixels` deve apontar para `len` bytes graváveis durante toda a chamada.
pub unsafe extern "C" fn hyprmac_tint_folder(
    pixels: *mut u8,
    len: usize,
    width: usize,
    height: usize,
    stride: usize,
    red: u8,
    green: u8,
    blue: u8,
) -> bool {
    if pixels.is_null() || width == 0 || height == 0 || width > stride / 4 {
        return false;
    }
    let Some(needed) = height.checked_mul(stride) else {
        return false;
    };
    if needed > len {
        return false;
    }
    let bytes = std::slice::from_raw_parts_mut(pixels, len);
    tint_rgba(bytes, width, height, stride, [red, green, blue]);
    true
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn preserves_transparency_and_highlight() {
        let mut pixels = [30, 40, 50, 0, 250, 250, 250, 255, 131, 197, 229, 255];
        tint_rgba(&mut pixels, 3, 1, 12, [230, 60, 70]);
        assert_eq!(&pixels[..8], &[30, 40, 50, 0, 250, 250, 250, 255]);
        assert!(pixels[8] > pixels[9] && pixels[9] <= pixels[10]);
    }

    #[test]
    fn rejects_short_buffer() {
        let mut pixels = [0u8; 4];
        assert!(!unsafe { hyprmac_tint_folder(pixels.as_mut_ptr(), 4, 2, 1, 8, 1, 2, 3) });
    }

    #[test]
    fn resolves_palette_and_custom_color() {
        assert_eq!(
            color_from_preferences(br#"{"folder_color":"red"}"#),
            Some([0xe0, 0x38, 0x3e])
        );
        assert_eq!(
            color_from_preferences(
                br##"{"folder_color":"choose","folder_color_custom":"#12aBcD"}"##
            ),
            Some([0x12, 0xab, 0xcd])
        );
        assert_eq!(color_from_preferences(br#"{"folder_color":"auto"}"#), None);
        assert_eq!(
            color_from_preferences(br#"{"folder_color":"choose","folder_color_custom":"bad"}"#),
            None
        );
    }
}
