//! Geometria lógica do Dock, sem GTK, relógios nem acesso ao compositor.

#[repr(C)]
#[derive(Clone, Copy, Debug)]
pub struct Metrics {
    pub icon: i32,
    pub pad_top: i32,
    pub pad_side: i32,
    pub gap: i32,
    pub h: i32,
    pub radius: f64,
    pub dot: i32,
    pub dot_gap: i32,
    pub sep_col: i32,
    pub sep_h: i32,
    pub bottom: i32,
}

#[repr(C)]
#[derive(Clone, Copy, Debug)]
pub struct Drawn {
    pub index: i64,
    pub x: f64,
    pub y: f64,
    pub size: f64,
}

#[derive(Clone, Copy, Debug)]
pub struct HitPoint {
    pub x: f64,
    pub y: f64,
    pub origin_x: f64,
    pub origin_y: f64,
}

pub fn from_icon(icon: i32) -> Metrics {
    let scale = f64::from(icon) / 36.0;
    Metrics {
        icon: (36.0 * scale).round_ties_even() as i32,
        pad_top: (11.0 * scale).round_ties_even() as i32,
        pad_side: (8.0 * scale).round_ties_even() as i32,
        gap: (9.0 * scale).round_ties_even() as i32,
        h: (58.0 * scale).round_ties_even() as i32,
        radius: 15.0 * scale,
        dot: 4,
        dot_gap: 4,
        sep_col: (11.0 * scale).round_ties_even() as i32,
        sep_h: (41.0 * scale).round_ties_even() as i32,
        bottom: (4.0 * scale).round_ties_even() as i32,
    }
}

pub fn shifts(growths: &[f64]) -> Vec<f64> {
    let half_growth = growths.iter().sum::<f64>() / 2.0;
    let mut consumed = 0.0;
    growths
        .iter()
        .map(|growth| {
            let shift = consumed + growth / 2.0 - half_growth;
            consumed += growth;
            shift
        })
        .collect()
}

pub fn layout(metrics: Metrics, separators: &[u8]) -> (Vec<f64>, f64) {
    let mut x = f64::from(metrics.pad_side);
    let xs = separators
        .iter()
        .map(|sep| {
            let current = x;
            x += f64::from(
                if *sep != 0 {
                    metrics.sep_col
                } else {
                    metrics.icon
                } + metrics.gap,
            );
            current
        })
        .collect();
    (xs, x - f64::from(metrics.gap) + f64::from(metrics.pad_side))
}

pub fn index_at(
    metrics: Metrics,
    separators: &[u8],
    positions: &[f64],
    drawn: &[Drawn],
    point: HitPoint,
) -> Option<i64> {
    let HitPoint {
        x,
        y,
        origin_x,
        origin_y,
    } = point;
    if y < origin_y - f64::from(metrics.icon) || y > origin_y + f64::from(metrics.h) {
        return None;
    }
    for item in drawn {
        if item.x <= x && x < item.x + item.size && item.y <= y && y < item.y + item.size {
            return Some(item.index);
        }
    }
    if !drawn.is_empty() {
        for item in drawn {
            let half = f64::from(metrics.gap) / 2.0;
            if item.x - half <= x && x < item.x + item.size + half {
                return Some(item.index);
            }
        }
        return None;
    }
    for (index, (&sep, &position)) in separators.iter().zip(positions).enumerate() {
        let span = if sep != 0 {
            metrics.sep_col
        } else {
            metrics.icon
        };
        let left = origin_x + position - f64::from(metrics.gap) / 2.0;
        let right = origin_x + position + f64::from(span) + f64::from(metrics.gap) / 2.0;
        if left <= x && x < right {
            return Some(index as i64);
        }
    }
    None
}

#[no_mangle]
pub extern "C" fn hyprmac_dock_metrics(icon: i32) -> Metrics {
    from_icon(icon)
}

/// # Safety
/// `growths` references `count` readable doubles and `output` references
/// `count` writable doubles when count is nonzero.
#[no_mangle]
pub unsafe extern "C" fn hyprmac_dock_shifts(growths: *const f64, count: usize, output: *mut f64) {
    if count == 0 {
        return;
    }
    if growths.is_null() || output.is_null() {
        return;
    }
    let values = unsafe { std::slice::from_raw_parts(growths, count) };
    let result = shifts(values);
    unsafe {
        std::ptr::copy_nonoverlapping(result.as_ptr(), output, count);
    }
}

/// # Safety
/// `separators` references `count` readable bytes and `positions` references
/// `count` writable doubles when count is nonzero.
#[no_mangle]
pub unsafe extern "C" fn hyprmac_dock_layout(
    metrics: Metrics,
    separators: *const u8,
    count: usize,
    positions: *mut f64,
) -> f64 {
    if count == 0 {
        return layout(metrics, &[]).1;
    }
    if separators.is_null() || positions.is_null() {
        return f64::NAN;
    }
    let separators = unsafe { std::slice::from_raw_parts(separators, count) };
    let (result, width) = layout(metrics, separators);
    unsafe {
        std::ptr::copy_nonoverlapping(result.as_ptr(), positions, count);
    }
    width
}

/// # Safety
/// The separators and positions point to `count` elements, and drawn points to
/// `drawn_count` elements when those counts are nonzero.
#[no_mangle]
pub unsafe extern "C" fn hyprmac_dock_index_at(
    metrics: Metrics,
    separators: *const u8,
    positions: *const f64,
    count: usize,
    drawn: *const Drawn,
    drawn_count: usize,
    x: f64,
    y: f64,
    origin_x: f64,
    origin_y: f64,
) -> i64 {
    if count > 0 && (separators.is_null() || positions.is_null()) {
        return -1;
    }
    if drawn_count > 0 && drawn.is_null() {
        return -1;
    }
    let separators = if count == 0 {
        &[]
    } else {
        unsafe { std::slice::from_raw_parts(separators, count) }
    };
    let positions = if count == 0 {
        &[]
    } else {
        unsafe { std::slice::from_raw_parts(positions, count) }
    };
    let drawn = if drawn_count == 0 {
        &[]
    } else {
        unsafe { std::slice::from_raw_parts(drawn, drawn_count) }
    };
    index_at(
        metrics,
        separators,
        positions,
        drawn,
        HitPoint {
            x,
            y,
            origin_x,
            origin_y,
        },
    )
    .unwrap_or(-1)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn fixed_layout_and_hit_testing() {
        let metrics = from_icon(46);
        let (positions, width) = layout(metrics, &[0, 1, 0]);
        assert_eq!(
            positions,
            [
                metrics.pad_side as f64,
                (metrics.pad_side + metrics.icon + metrics.gap) as f64,
                (metrics.pad_side + metrics.icon + metrics.sep_col + 2 * metrics.gap) as f64
            ]
        );
        assert_eq!(
            width,
            (2 * metrics.pad_side + 2 * metrics.icon + metrics.sep_col + 2 * metrics.gap) as f64
        );
        assert_eq!(
            index_at(
                metrics,
                &[0, 1, 0],
                &positions,
                &[],
                HitPoint {
                    x: 120.0 + positions[1],
                    y: 50.0,
                    origin_x: 120.0,
                    origin_y: 50.0,
                }
            ),
            Some(1)
        );
    }
    #[test]
    fn magnification_keeps_center() {
        assert_eq!(shifts(&[]), Vec::<f64>::new());
        assert_eq!(shifts(&[10.0, 0.0, 10.0]), [-5.0, 0.0, 5.0]);
    }
}
