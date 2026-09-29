//! Reader for gridded module products (drift maps, debris ensembles, coverage rasters,
//! bathymetry): a TOML manifest beside a little-endian, C-order array of f32 or f64.
//!
//! ```toml
//! data = "drift-bran2016.f32"   # relative to the manifest
//! dtype = "f32"                  # "f32" or "f64"
//! shape = [48, 301, 351]
//!
//! [[axes]]                       # one per dimension, in order: explicit values...
//! name = "time_unix_s"
//! values = [1394236800.0, 1394240400.0]
//!
//! [[axes]]                       # ...or a regular axis
//! name = "latitude_deg"
//! start = -45.0
//! step = 0.1
//! ```
//!
//! NaN in the data means "not computed". It propagates through interpolation and is never
//! filled, so a module passes it on to the composer instead of inventing a value.

use serde::Deserialize;
use std::path::Path;

/// Arrays of more dimensions are refused at load; interpolation works on fixed-size arrays.
const MAX_DIMENSIONS: usize = 6;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Manifest {
    data: String,
    dtype: String,
    shape: Vec<usize>,
    axes: Vec<AxisSpec>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct AxisSpec {
    name: String,
    values: Option<Vec<f64>>,
    start: Option<f64>,
    step: Option<f64>,
}

/// One dimension's coordinates, strictly increasing or strictly decreasing.
#[derive(Debug, Clone, PartialEq)]
pub struct Axis {
    pub name: String,
    pub values: Vec<f64>,
}

#[derive(Debug, Clone)]
enum Data {
    F32(Vec<f32>),
    F64(Vec<f64>),
}

#[derive(Debug, Clone)]
pub struct RawArray {
    pub shape: Vec<usize>,
    pub axes: Vec<Axis>,
    data: Data,
}

impl RawArray {
    pub fn load(manifest: &Path) -> Result<Self, String> {
        let at = |e: String| format!("{}: {e}", manifest.display());
        let text = std::fs::read_to_string(manifest).map_err(|e| at(e.to_string()))?;
        let m: Manifest = toml::from_str(&text).map_err(|e| at(e.to_string()))?;
        if m.axes.len() != m.shape.len() || m.shape.is_empty() || m.shape.len() > MAX_DIMENSIONS {
            return Err(at(format!("{} axes for a {}-dimensional array (1 to {MAX_DIMENSIONS})", m.axes.len(), m.shape.len())));
        }
        let axes = m
            .axes
            .into_iter()
            .zip(&m.shape)
            .map(|(a, &n)| {
                let values = match (a.values, a.start, a.step) {
                    (Some(values), None, None) => values,
                    (None, Some(start), Some(step)) => (0..n).map(|i| start + step * i as f64).collect(),
                    _ => return Err(at(format!("axis {}: give either values, or start and step", a.name))),
                };
                let monotonic = values.windows(2).all(|w| w[1] > w[0]) || values.windows(2).all(|w| w[1] < w[0]);
                if values.len() != n || n < 2 || !monotonic {
                    return Err(at(format!("axis {}: need {n} >= 2 strictly monotonic values", a.name)));
                }
                Ok(Axis { name: a.name, values })
            })
            .collect::<Result<Vec<_>, _>>()?;
        let count: usize = m.shape.iter().product();
        let path = manifest.parent().unwrap_or(Path::new(".")).join(&m.data);
        let bytes = std::fs::read(&path).map_err(|e| format!("{}: {e}", path.display()))?;
        let width = match m.dtype.as_str() {
            "f32" => 4,
            "f64" => 8,
            other => return Err(at(format!("dtype {other}: expected f32 or f64"))),
        };
        if bytes.len() != count * width {
            return Err(format!("{}: {} bytes, expected {} for shape {:?}", path.display(), bytes.len(), count * width, m.shape));
        }
        let data = if width == 4 {
            Data::F32(bytes.chunks_exact(4).map(|c| f32::from_le_bytes(c.try_into().unwrap())).collect())
        } else {
            Data::F64(bytes.chunks_exact(8).map(|c| f64::from_le_bytes(c.try_into().unwrap())).collect())
        };
        Ok(RawArray { shape: m.shape, axes, data })
    }

    /// The value at a grid index (one per dimension). Panics on a wrong arity or an index out
    /// of range, which is a bug in the caller, rather than returning a wrong value.
    pub fn get(&self, index: &[usize]) -> f64 {
        assert_eq!(index.len(), self.shape.len(), "RawArray::get: wrong number of indices");
        let flat = index.iter().zip(&self.shape).fold(0, |acc, (&i, &n)| {
            assert!(i < n, "RawArray::get: index {i} out of range {n}");
            acc * n + i
        });
        match &self.data {
            Data::F32(v) => f64::from(v[flat]),
            Data::F64(v) => v[flat],
        }
    }

    /// Multilinear interpolation at axis coordinates (one per dimension). NaN outside the
    /// axes, or if any corner that carries weight is NaN: "not computed" propagates. Panics on
    /// a wrong number of coordinates.
    pub fn interpolate(&self, at: &[f64]) -> f64 {
        let dims = self.axes.len();
        assert_eq!(at.len(), dims, "RawArray::interpolate: wrong number of coordinates");
        let mut cells = [(0usize, 0.0f64); MAX_DIMENSIONS];
        for d in 0..dims {
            match locate(&self.axes[d].values, at[d]) {
                Some(cell) => cells[d] = cell,
                None => return f64::NAN,
            }
        }
        let mut index = [0usize; MAX_DIMENSIONS];
        let mut total = 0.0;
        for corner in 0..1usize << dims {
            let mut weight = 1.0;
            for (d, &(i, f)) in cells[..dims].iter().enumerate() {
                let upper = corner >> d & 1 == 1;
                index[d] = i + usize::from(upper);
                weight *= if upper { f } else { 1.0 - f };
            }
            if weight > 0.0 {
                total += weight * self.get(&index[..dims]);
            }
        }
        total
    }
}

/// Lower index and fraction of `x` on a strictly monotonic axis; None outside it.
fn locate(values: &[f64], x: f64) -> Option<(usize, f64)> {
    let (first, last) = (values[0], values[values.len() - 1]);
    if !(x >= first.min(last) && x <= first.max(last)) {
        return None;
    }
    let ascending = last > first;
    // Number of values at or below x (ascending) or at or above x (descending), at least 1.
    let above = values.partition_point(|&v| if ascending { v <= x } else { v >= x });
    let i = above.clamp(1, values.len() - 1) - 1;
    Some((i, (x - values[i]) / (values[i + 1] - values[i])))
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A 2 x 3 f32 grid with one NaN cell, read back from disk and interpolated by hand.
    #[test]
    fn reads_interpolates_and_propagates_not_computed() {
        let dir = std::env::temp_dir().join(format!("raw-array-test-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        // latitude (descending) x longitude: [[1, 2, 3], [4, 5, NaN]].
        let values: [f32; 6] = [1.0, 2.0, 3.0, 4.0, 5.0, f32::NAN];
        std::fs::write(dir.join("grid.f32"), values.iter().flat_map(|v| v.to_le_bytes()).collect::<Vec<_>>()).unwrap();
        let manifest = "data = \"grid.f32\"\ndtype = \"f32\"\nshape = [2, 3]\n\
                        [[axes]]\nname = \"latitude_deg\"\nvalues = [-30.0, -31.0]\n\
                        [[axes]]\nname = \"longitude_deg\"\nstart = 90.0\nstep = 0.5\n";
        std::fs::write(dir.join("grid.toml"), manifest).unwrap();
        let grid = RawArray::load(&dir.join("grid.toml")).unwrap();
        std::fs::remove_dir_all(&dir).unwrap();

        assert_eq!(grid.axes[1].values, vec![90.0, 90.5, 91.0]);
        assert_eq!(grid.get(&[1, 1]), 5.0);
        // Centre of the first cell: the mean of 1, 2, 4 and 5.
        assert!((grid.interpolate(&[-30.5, 90.25]) - 3.0).abs() < 1e-12);
        // On the grid line of the first column, the NaN corner carries no weight...
        assert!((grid.interpolate(&[-30.25, 90.5]) - 2.75).abs() < 1e-12);
        // ...but inside the cell that touches it, the result is not computed.
        assert!(grid.interpolate(&[-30.5, 90.75]).is_nan());
        // Outside the axes is not computed either, never extrapolated.
        assert!(grid.interpolate(&[-29.9, 90.25]).is_nan());
        assert!(grid.interpolate(&[-30.5, 91.1]).is_nan());
    }
}
