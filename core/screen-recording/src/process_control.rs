//! Estado do processo de gravação: PID guardado e timer de início.
use std::env;
use std::fs;
use std::path::{Path, PathBuf};

pub(crate) fn runtime_file(name: &str) -> PathBuf {
    PathBuf::from(env::var_os("XDG_RUNTIME_DIR").unwrap_or_else(|| "/tmp".into())).join(name)
}

pub(crate) fn stop_existing(pidfile: &Path) -> bool {
    let Some(pid) = fs::read_to_string(pidfile)
        .ok()
        .and_then(|text| text.trim().parse::<i32>().ok())
    else {
        return false;
    };
    // A stale PID can be reused by an unrelated process. Check argv[0] before
    // sending SIGTERM; the wrapper and installer keep this executable name.
    let Ok(command_line) = fs::read(format!("/proc/{pid}/cmdline")) else {
        return false;
    };
    if !is_recorder_command_line(&command_line) {
        return false;
    }
    unsafe { libc::kill(pid, libc::SIGTERM) == 0 }
}

fn is_recorder_command_line(command_line: &[u8]) -> bool {
    let Some(argv0) = command_line.split(|byte| *byte == 0).next() else {
        return false;
    };
    let Ok(argv0) = std::str::from_utf8(argv0) else {
        return false;
    };
    Path::new(argv0)
        .file_name()
        .is_some_and(|name| name == "hyprmac-screen-recording")
}

pub(crate) fn recording_delay(value: Option<&str>) -> u64 {
    value
        .and_then(|text| text.parse::<u64>().ok())
        .filter(|seconds| *seconds <= 10)
        .unwrap_or(0)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn only_recorder_command_line_can_be_stopped() {
        assert!(is_recorder_command_line(
            b"/home/user/.local/bin/hyprmac-screen-recording\0screen\0"
        ));
        assert!(!is_recorder_command_line(b"/usr/bin/other-process\0"));
        assert!(!is_recorder_command_line(
            b"/usr/bin/other-process\0hyprmac-screen-recording\0"
        ));
        assert!(!is_recorder_command_line(b""));
    }

    #[test]
    fn recording_timer_accepts_only_short_nonnegative_values() {
        assert_eq!(recording_delay(Some("5")), 5);
        assert_eq!(recording_delay(Some("10")), 10);
        assert_eq!(recording_delay(Some("-1")), 0);
        assert_eq!(recording_delay(Some("1000")), 0);
        assert_eq!(recording_delay(None), 0);
    }
}
