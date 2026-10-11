//! Read-only Linux process snapshot prototype for a future Activity Monitor.
use std::env;
use std::fs;
use std::io::{self, Write};
use std::path::Path;
use std::time::Instant;

#[derive(Debug, PartialEq, Eq)]
struct Process {
    pid: u32,
    name: String,
    state: char,
    cpu_ticks: u64,
    rss_kib: Option<u64>,
}

fn parse_stat(input: &str) -> Option<Process> {
    // comm is enclosed in parentheses but may itself contain ')' and spaces.
    let open = input.find('(')?;
    let close = input.rfind(')')?;
    if close <= open || !input[close + 1..].starts_with(' ') {
        return None;
    }
    let pid = input[..open].trim().parse().ok()?;
    let name = input[open + 1..close].to_owned();
    let fields: Vec<&str> = input[close + 1..].split_whitespace().collect();
    // fields[0] is field 3 (state); fields[11/12] are utime/stime.
    let state = fields.first()?.chars().next()?;
    if fields.first()?.chars().count() != 1 {
        return None;
    }
    let user: u64 = fields.get(11)?.parse().ok()?;
    let system: u64 = fields.get(12)?.parse().ok()?;
    Some(Process {
        pid,
        name,
        state,
        cpu_ticks: user.checked_add(system)?,
        rss_kib: None,
    })
}

fn parse_rss_kib(status: &str) -> Option<u64> {
    status.lines().find_map(|line| {
        let value = line.strip_prefix("VmRSS:")?;
        let mut words = value.split_whitespace();
        let amount = words.next()?.parse().ok()?;
        (words.next()? == "kB").then_some(amount)
    })
}

fn read_process(proc_root: &Path, pid: u32) -> Option<Process> {
    let dir = proc_root.join(pid.to_string());
    // A process can exit between any two reads. Skipping it is normal.
    let stat = fs::read_to_string(dir.join("stat")).ok()?;
    let mut process = parse_stat(&stat)?;
    if process.pid != pid {
        return None;
    }
    let status = fs::read_to_string(dir.join("status")).ok()?;
    process.rss_kib = parse_rss_kib(&status);
    Some(process)
}

fn snapshot(proc_root: &Path) -> io::Result<Vec<Process>> {
    let mut pids = Vec::new();
    for entry in fs::read_dir(proc_root)? {
        let entry = entry?;
        if let Ok(pid) = entry.file_name().to_string_lossy().parse::<u32>() {
            pids.push(pid);
        }
    }
    pids.sort_unstable();
    Ok(pids
        .into_iter()
        .filter_map(|pid| read_process(proc_root, pid))
        .collect())
}

fn json_string(value: &str) -> String {
    let mut result = String::from("\"");
    for ch in value.chars() {
        match ch {
            '"' => result.push_str("\\\""),
            '\\' => result.push_str("\\\\"),
            '\n' => result.push_str("\\n"),
            '\r' => result.push_str("\\r"),
            '\t' => result.push_str("\\t"),
            c if c <= '\u{1f}' => result.push_str(&format!("\\u{:04x}", c as u32)),
            c => result.push(c),
        }
    }
    result.push('"');
    result
}

fn json_line(process: &Process) -> String {
    let rss = process
        .rss_kib
        .map_or_else(|| "null".to_owned(), |n| n.to_string());
    format!(
        "{{\"pid\":{},\"name\":{},\"state\":{},\"cpu_ticks\":{},\"rss_kib\":{}}}",
        process.pid,
        json_string(&process.name),
        json_string(&process.state.to_string()),
        process.cpu_ticks,
        rss
    )
}

fn benchmark(rounds: usize) -> io::Result<()> {
    let mut durations = Vec::with_capacity(rounds);
    let mut count = 0;
    for _ in 0..rounds {
        let start = Instant::now();
        count = snapshot(Path::new("/proc"))?.len();
        durations.push(start.elapsed().as_secs_f64() * 1000.0);
    }
    durations.sort_by(f64::total_cmp);
    let percentile = |p: usize| durations[((rounds * p).div_ceil(100)).saturating_sub(1)];
    let peak_kib = fs::read_to_string("/proc/self/status").ok().and_then(|s| {
        s.lines().find_map(|line| {
            line.strip_prefix("VmHWM:")?
                .split_whitespace()
                .next()?
                .parse::<u64>()
                .ok()
        })
    });
    eprintln!(
        "rounds={rounds} last_processes={count} p50_ms={:.3} p95_ms={:.3} peak_rss_kib={}",
        percentile(50),
        percentile(95),
        peak_kib.map_or_else(|| "unknown".to_owned(), |n| n.to_string())
    );
    Ok(())
}

fn main() -> io::Result<()> {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.first().map(String::as_str) == Some("--bench") && args.len() == 2 {
        let rounds = args[1]
            .parse::<usize>()
            .ok()
            .filter(|n| (1..=10_000).contains(n))
            .ok_or_else(|| {
                io::Error::new(io::ErrorKind::InvalidInput, "rounds must be 1..=10000")
            })?;
        return benchmark(rounds);
    }
    if !args.is_empty() {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "usage: activity-probe [--bench ROUNDS]",
        ));
    }
    let stdout = io::stdout();
    let mut output = io::BufWriter::new(stdout.lock());
    for process in snapshot(Path::new("/proc"))? {
        if let Err(error) = writeln!(output, "{}", json_line(&process)) {
            return if error.kind() == io::ErrorKind::BrokenPipe {
                Ok(())
            } else {
                Err(error)
            };
        }
    }
    match output.flush() {
        Err(error) if error.kind() == io::ErrorKind::BrokenPipe => Ok(()),
        result => result,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn stat(name: &str) -> String {
        let mut fields = vec!["0"; 13];
        fields[0] = "S";
        fields[11] = "7";
        fields[12] = "11";
        format!("42 ({name}) {}", fields.join(" "))
    }

    #[test]
    fn parses_parentheses_spaces_and_escape_characters() {
        let p = parse_stat(&stat("a ) b \\\"\n")).unwrap();
        assert_eq!(
            (p.pid, p.name.as_str(), p.state, p.cpu_ticks),
            (42, "a ) b \\\"\n", 'S', 18)
        );
        assert_eq!(json_line(&p),
                   "{\"pid\":42,\"name\":\"a ) b \\\\\\\"\\n\",\"state\":\"S\",\"cpu_ticks\":18,\"rss_kib\":null}");
    }

    #[test]
    fn rejects_truncated_or_overflowed_stat() {
        assert!(parse_stat("42 (name) S 0").is_none());
        assert!(parse_stat(&stat("normal").replace(" 11", " 18446744073709551616")).is_none());
    }

    #[test]
    fn parses_rss_and_missing_process() {
        assert_eq!(parse_rss_kib("Name:\ttest\nVmRSS:\t1234 kB\n"), Some(1234));
        assert_eq!(parse_rss_kib("Name:\ttest\n"), None);
        assert_eq!(
            read_process(Path::new("/definitely-not-a-proc-mount"), 42),
            None
        );
    }
}
