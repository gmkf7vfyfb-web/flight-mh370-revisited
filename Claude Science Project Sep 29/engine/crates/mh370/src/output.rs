//! Run artifacts: NumPy arrays, JSON, code revision and memory use.

use serde::Serialize;
use std::fs::File;
use std::io::{BufReader, Read};
use std::path::Path;

/// Stored as float32: particle sets run to gigabytes, and every column (lat/lon, Mach, counts,
/// origin indices below 2^24) fits in single precision. Weights below ~1e-38 underflow to zero,
/// a negligible share of the mass.
pub fn write_npy(path: &Path, shape: &[usize], data: &[f64]) -> Result<(), String> {
    write_array(path, shape, data.iter().flat_map(|v| (*v as f32).to_le_bytes()), "<f4")
}

/// Stored as float64: the stage files (hand-off, impacts, module outputs, predictions). They
/// carry Unix times (00:19:29.416, takeovers, predicted arrivals), which float32 resolves only
/// to 128 s, and weights, proposal corrections and log-likelihoods, where reweighting the tails
/// needs full precision. Their tables are small.
pub fn write_npy64(path: &Path, shape: &[usize], data: &[f64]) -> Result<(), String> {
    write_array(path, shape, data.iter().flat_map(|v| v.to_le_bytes()), "<f8")
}

fn write_array(path: &Path, shape: &[usize], values: impl Iterator<Item = u8>, descr: &str) -> Result<(), String> {
    let dims = shape.iter().map(|d| format!("{d},")).collect::<String>();
    let mut header = format!("{{'descr': '{descr}', 'fortran_order': False, 'shape': ({dims}), }}");
    while (10 + header.len() + 1) % 64 != 0 {
        header.push(' ');
    }
    header.push('\n');
    let mut bytes = b"\x93NUMPY\x01\x00".to_vec();
    bytes.extend((header.len() as u16).to_le_bytes());
    bytes.extend(header.as_bytes());
    bytes.extend(values);
    std::fs::write(path, bytes).map_err(|e| format!("{}: {e}", path.display()))
}

/// Read a `[rows, columns]` float32 or float64 NumPy array in blocks, one row at a time.
pub fn read_npy_rows(path: &Path, mut each: impl FnMut(&[f64])) -> Result<(), String> {
    let file = File::open(path).map_err(|e| format!("{}: {e}", path.display()))?;
    let mut reader = BufReader::with_capacity(1 << 20, file);
    let mut magic = [0u8; 10];
    reader.read_exact(&mut magic).map_err(|e| format!("{}: {e}", path.display()))?;
    if &magic[..6] != b"\x93NUMPY" {
        return Err(format!("{}: not a NumPy array", path.display()));
    }
    let header_len = u16::from_le_bytes([magic[8], magic[9]]) as usize;
    let mut header = vec![0u8; header_len];
    reader.read_exact(&mut header).map_err(|e| format!("{}: {e}", path.display()))?;
    let header = String::from_utf8_lossy(&header).to_string();
    if !header.contains("'fortran_order': False") {
        return Err(format!("{}: expected a C-order array", path.display()));
    }
    let width = if header.contains("'<f4'") {
        4
    } else if header.contains("'<f8'") {
        8
    } else {
        return Err(format!("{}: expected float32 or float64 rows", path.display()));
    };
    let shape: Vec<usize> = header
        .split_once("'shape': (")
        .ok_or_else(|| format!("{}: no shape", path.display()))?
        .1
        .split(')')
        .next()
        .unwrap_or("")
        .split(',')
        .filter_map(|s| s.trim().parse().ok())
        .collect();
    let [rows, columns] = shape[..] else {
        return Err(format!("{}: expected a two-dimensional array, not shape {shape:?}", path.display()));
    };
    // The declared shape must match the file, which also bounds every allocation below.
    let size = std::fs::metadata(path).map_err(|e| format!("{}: {e}", path.display()))?.len();
    let data = rows.checked_mul(columns).and_then(|n| n.checked_mul(width)).map(|n| n as u64);
    if data.and_then(|n| n.checked_add(10 + header_len as u64)) != Some(size) {
        return Err(format!("{}: {size} bytes do not hold shape {shape:?}", path.display()));
    }
    if columns == 0 {
        return Ok(());
    }
    let mut block = vec![0u8; columns * width * 4096];
    let mut row = vec![0.0f64; columns];
    let mut left = rows;
    while left > 0 {
        let take = left.min(4096);
        let bytes = &mut block[..take * columns * width];
        reader.read_exact(bytes).map_err(|e| format!("{}: {e}", path.display()))?;
        for chunk in bytes.chunks_exact(columns * width) {
            for (value, raw) in row.iter_mut().zip(chunk.chunks_exact(width)) {
                *value = match width {
                    4 => f64::from(f32::from_le_bytes(raw.try_into().unwrap())),
                    _ => f64::from_le_bytes(raw.try_into().unwrap()),
                };
            }
            each(&row);
        }
        left -= take;
    }
    Ok(())
}

pub fn write_json(path: &Path, value: &impl Serialize) -> Result<(), String> {
    let text = serde_json::to_string_pretty(value).map_err(|e| e.to_string())?;
    std::fs::write(path, text + "\n").map_err(|e| format!("{}: {e}", path.display()))
}

pub fn code_revision() -> String {
    let git = |args: &[&str]| {
        std::process::Command::new("git")
            .args(args)
            .output()
            .ok()
            .filter(|o| o.status.success())
            .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
    };
    match git(&["rev-parse", "--short", "HEAD"]) {
        Some(rev) if git(&["status", "--porcelain"]).is_some_and(|s| s.is_empty()) => rev,
        Some(rev) => format!("{rev}-dirty"),
        None => "unversioned".into(),
    }
}

/// Peak resident-set size of this process, or `None` where the platform does not report one.
///
/// Linux publishes the high-water mark as `VmHWM` in `/proc/self/status`, in kibibytes. macOS has
/// no `/proc`, so the same quantity is read from `getrusage(RUSAGE_SELF).ru_maxrss`, which Darwin
/// reports in **bytes** where Linux's `getrusage` would report kibibytes. Before this was handled,
/// a macOS run wrote `peak_memory_mib: null` into its manifest and the report failed to format it.
pub fn peak_memory_mib() -> Option<f64> {
    #[cfg(target_os = "linux")]
    {
        let status = std::fs::read_to_string("/proc/self/status").ok()?;
        let kib: f64 = status.lines().find(|l| l.starts_with("VmHWM:"))?.split_whitespace().nth(1)?.parse().ok()?;
        return Some(kib / 1024.0);
    }
    #[cfg(target_os = "macos")]
    {
        let mut usage = std::mem::MaybeUninit::<libc::rusage>::uninit();
        // SAFETY: getrusage writes the whole struct it is handed and reports failure in its return
        // value; the struct is only read once the call has returned zero.
        if unsafe { libc::getrusage(libc::RUSAGE_SELF, usage.as_mut_ptr()) } != 0 {
            return None;
        }
        let bytes = unsafe { usage.assume_init() }.ru_maxrss as f64;
        return Some(bytes / (1024.0 * 1024.0));
    }
    #[allow(unreachable_code)]
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Every platform this runs on reports a peak resident-set size, so a manifest written here
    /// never carries `peak_memory_mib: null`. A process that has loaded the test binary holds at
    /// least a mebibyte, and no run of this filter has approached a tebibyte.
    #[test]
    #[cfg(any(target_os = "linux", target_os = "macos"))]
    fn peak_memory_is_reported_in_mebibytes() {
        let mib = peak_memory_mib().expect("peak resident-set size is available on this platform");
        assert!((1.0..1_048_576.0).contains(&mib), "implausible peak memory: {mib} MiB");
    }

    /// Stage files keep Unix times to the millisecond (float32 would round 00:19:29.416 to 128 s
    /// steps); particle arrays are single precision; malformed headers are refused.
    #[test]
    fn npy_files_round_trip_at_their_precision() {
        let dir = std::env::temp_dir().join(format!("npy-test-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let values = [1_394_240_369.416, -37.123_456_789, 1e-300, f64::NAN];
        write_npy64(&dir.join("double.npy"), &[2, 2], &values).unwrap();
        write_npy(&dir.join("single.npy"), &[2, 2], &values).unwrap();
        let read = |name: &str| {
            let mut out = Vec::new();
            read_npy_rows(&dir.join(name), |row| out.extend_from_slice(row)).map(|_| out)
        };
        let double = read("double.npy").unwrap();
        assert_eq!(double[..3], values[..3]);
        assert!(double[3].is_nan());
        let single = read("single.npy").unwrap();
        assert_eq!(single[0], f64::from(1_394_240_369.416f64 as f32));
        assert_ne!(single[0], values[0]);
        write_npy64(&dir.join("flat.npy"), &[4], &values).unwrap();
        assert!(read("flat.npy").is_err(), "a one-dimensional array is refused");
        write_npy64(&dir.join("short.npy"), &[3, 2], &values).unwrap();
        assert!(read("short.npy").is_err(), "a shape the file cannot hold is refused");
        std::fs::remove_dir_all(&dir).unwrap();
    }
}
