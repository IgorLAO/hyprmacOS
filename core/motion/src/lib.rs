//! Núcleo matemático das molas usadas pelo shell, Dock e Spotlight.
//! ABI C pequena para a camada GTK atual; sem estado global, GTK ou timers.

#[repr(C)]
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct SpringState {
    pub value: f64,
    pub velocity: f64,
}

pub fn spring_step(mut value: f64, mut velocity: f64, target: f64, dt: f64, frequency: f64, damping: f64) -> SpringState {
    let dt = dt.clamp(0.0, 0.05);
    let omega = 2.0 * std::f64::consts::PI * frequency;
    let steps = (dt / 0.008).ceil().max(1.0) as usize;
    let h = dt / steps as f64;
    for _ in 0..steps {
        velocity += (omega * omega * (target - value) - 2.0 * damping * omega * velocity) * h;
        value += velocity * h;
    }
    if (target - value).abs() < 0.001 && velocity.abs() < 0.01 {
        SpringState { value: target, velocity: 0.0 }
    } else {
        SpringState { value, velocity }
    }
}

#[no_mangle]
pub extern "C" fn hyprmac_spring_step(value: f64, velocity: f64, target: f64, dt: f64, frequency: f64, damping: f64) -> SpringState {
    spring_step(value, velocity, target, dt, frequency, damping)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn delayed_frame_is_bounded_and_settles() {
        assert_eq!(spring_step(0.0, 0.0, 1.0, 1.0, 3.7, 0.82), spring_step(0.0, 0.0, 1.0, 0.05, 3.7, 0.82));
        assert_eq!(spring_step(0.999, 0.005, 1.0, 0.016, 3.7, 0.82), SpringState { value: 1.0, velocity: 0.0 });
    }
}
