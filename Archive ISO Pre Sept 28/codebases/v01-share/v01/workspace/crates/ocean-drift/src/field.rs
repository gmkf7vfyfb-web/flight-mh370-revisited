use std::{
    collections::BTreeMap,
    fs::File,
    io::{Read, Write},
    sync::Arc,
};

use memmap2::{Mmap, MmapOptions};
use mh370_domain::LatLon;
use serde::{Deserialize, Serialize};
use thiserror::Error;

const MAGIC: &[u8; 8] = b"MHGRID1\0";
const PACKED_I16: u32 = 1;
const FILE_BACKED_PACKED_BYTES: usize = 256 * 1024 * 1024;
const FILE_BACKED_COPY_BUFFER_BYTES: usize = 4 * 1024 * 1024;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum FieldTimeAxis {
    UnixSeconds,
    ClimatologicalMonth,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct VelocitySample {
    pub east_mps: f64,
    pub north_mps: f64,
    pub east_standard_error_mps: f64,
    pub north_standard_error_mps: f64,
}

#[derive(Debug, Clone)]
pub struct GriddedField {
    pub name: String,
    pub time_axis: FieldTimeAxis,
    times: Vec<f64>,
    latitudes: Vec<f64>,
    longitudes: Vec<f64>,
    components: BTreeMap<String, FieldComponent>,
    maximum_time_interpolation_gap_seconds: Option<f64>,
    renormalize_finite_spatial_corners: bool,
}

#[derive(Debug, Clone)]
enum FieldComponent {
    Float32(Vec<f32>),
    PackedI16 {
        values: PackedI16Values,
        scale: f64,
        offset: f64,
        missing: i16,
        persistent_land_mask: Option<i16>,
    },
}

#[derive(Debug, Clone)]
enum PackedI16Values {
    Owned(Vec<i16>),
    FileBacked {
        bytes: Arc<Mmap>,
        // Retain the immutable, unnamed backing file for the complete map
        // lifetime. It has no path that another process can replace or edit.
        _file: Arc<File>,
    },
}

impl PackedI16Values {
    fn value(&self, index: usize) -> i16 {
        match self {
            Self::Owned(values) => values[index],
            Self::FileBacked { bytes, .. } => {
                let offset = index * 2;
                i16::from_le_bytes([bytes[offset], bytes[offset + 1]])
            }
        }
    }
}

impl FieldComponent {
    fn value(&self, index: usize) -> f64 {
        match self {
            Self::Float32(values) => values[index] as f64,
            Self::PackedI16 {
                values,
                scale,
                offset,
                missing,
                persistent_land_mask,
            } => {
                let packed = values.value(index);
                if packed == *missing || persistent_land_mask.is_some_and(|value| packed == value) {
                    f64::NAN
                } else {
                    *offset + *scale * f64::from(packed)
                }
            }
        }
    }

    fn is_persistent_land_mask(&self, index: usize) -> bool {
        match self {
            Self::Float32(_) => false,
            Self::PackedI16 {
                values,
                persistent_land_mask,
                ..
            } => persistent_land_mask.is_some_and(|value| values.value(index) == value),
        }
    }
}

#[derive(Debug, Error, Clone, PartialEq)]
pub enum FieldError {
    #[error("invalid MHGRID1 field: {0}")]
    InvalidFormat(&'static str),
    #[error("field component is absent: {0}")]
    MissingComponent(String),
    #[error("field storage failure: {0}")]
    Storage(String),
    #[error("position lies outside the field")]
    OutsideSpace,
    #[error("time lies outside the field")]
    OutsideTime,
    #[error("field has a missing value at the interpolation point")]
    MissingValue,
}

impl GriddedField {
    pub fn from_bytes(name: impl Into<String>, bytes: &[u8]) -> Result<Self, FieldError> {
        Self::from_reader(name, bytes)
    }

    /// Decode one MHGRID field without retaining a second full-file byte
    /// buffer. This is the production loading path for multi-gigabyte native
    /// fields; `from_bytes` remains the convenient fixture interface.
    pub fn from_reader(name: impl Into<String>, input: impl Read) -> Result<Self, FieldError> {
        let mut reader = Reader::new(input);
        if reader.fixed::<8>()? != *MAGIC {
            return Err(FieldError::InvalidFormat("magic or schema"));
        }
        let schema = reader.u32()?;
        if !matches!(schema, 1..=3) {
            return Err(FieldError::InvalidFormat("magic or schema"));
        }
        let time_axis = match reader.u32()? {
            0 => FieldTimeAxis::UnixSeconds,
            1 => FieldTimeAxis::ClimatologicalMonth,
            _ => return Err(FieldError::InvalidFormat("time axis")),
        };
        let nt = reader.u32()? as usize;
        let ny = reader.u32()? as usize;
        let nx = reader.u32()? as usize;
        let nc = reader.u32()? as usize;
        if nt == 0 || ny < 2 || nx < 2 || nc == 0 {
            return Err(FieldError::InvalidFormat("dimensions"));
        }
        let times = reader.f64s(nt)?;
        let latitudes = reader.f64s(ny)?;
        let longitudes = reader.f64s(nx)?;
        if !increasing(&times) || !increasing(&latitudes) || !increasing(&longitudes) {
            return Err(FieldError::InvalidFormat("coordinate order"));
        }
        if time_axis == FieldTimeAxis::ClimatologicalMonth
            && (nt != 12 || times.iter().enumerate().any(|(i, x)| *x != i as f64))
        {
            return Err(FieldError::InvalidFormat("month coordinates"));
        }
        let count = nt
            .checked_mul(ny)
            .and_then(|v| v.checked_mul(nx))
            .ok_or(FieldError::InvalidFormat("dimension overflow"))?;
        let mut components = BTreeMap::new();
        for _ in 0..nc {
            let raw = reader.fixed::<16>()?;
            let end = raw.iter().position(|byte| *byte == 0).unwrap_or(raw.len());
            let component = std::str::from_utf8(&raw[..end])
                .map_err(|_| FieldError::InvalidFormat("component name"))?
                .to_string();
            if component.is_empty() || components.contains_key(&component) {
                return Err(FieldError::InvalidFormat("duplicate component"));
            }
            let values = if schema == 1 {
                FieldComponent::Float32(reader.f32s(count)?)
            } else {
                if reader.u32()? != PACKED_I16 {
                    return Err(FieldError::InvalidFormat("component encoding"));
                }
                let scale = reader.f64()?;
                let offset = reader.f64()?;
                let missing = reader.i16()?;
                let persistent_land_mask = (schema >= 3).then(|| reader.i16()).transpose()?;
                if !scale.is_finite()
                    || scale <= 0.0
                    || !offset.is_finite()
                    || persistent_land_mask == Some(missing)
                {
                    return Err(FieldError::InvalidFormat("component packing"));
                }
                FieldComponent::PackedI16 {
                    values: reader.packed_i16s(count, FILE_BACKED_PACKED_BYTES)?,
                    scale,
                    offset,
                    missing,
                    persistent_land_mask,
                }
            };
            components.insert(component, values);
        }
        if !reader.is_exhausted()? {
            return Err(FieldError::InvalidFormat("trailing bytes"));
        }
        Ok(Self {
            name: name.into(),
            time_axis,
            times,
            latitudes,
            longitudes,
            components,
            maximum_time_interpolation_gap_seconds: None,
            renormalize_finite_spatial_corners: false,
        })
    }

    /// Refuse interpolation across an unsupported temporal gap. Exact samples
    /// on either side remain usable. Climatological fields ignore this limit.
    pub fn set_maximum_time_interpolation_gap_seconds(
        &mut self,
        seconds: Option<f64>,
    ) -> Result<(), FieldError> {
        if seconds.is_some_and(|value| !value.is_finite() || value <= 0.0) {
            return Err(FieldError::InvalidFormat("maximum time interpolation gap"));
        }
        self.maximum_time_interpolation_gap_seconds = seconds;
        Ok(())
    }

    /// Renormalize bilinear weights over finite corners in the containing
    /// grid cell. This is intended only for a field with an independently
    /// established persistent land mask; it never converts a missing value to
    /// zero and still rejects cells without any finite weighted corner.
    pub fn set_renormalize_finite_spatial_corners(&mut self, enabled: bool) {
        self.renormalize_finite_spatial_corners = enabled;
    }

    pub fn time_range(&self) -> (f64, f64) {
        (self.times[0], *self.times.last().unwrap())
    }
    pub fn spatial_bounds(&self) -> (f64, f64, f64, f64) {
        (
            self.latitudes[0],
            *self.latitudes.last().unwrap(),
            self.longitudes[0],
            *self.longitudes.last().unwrap(),
        )
    }

    pub fn velocity(&self, time: f64, position: LatLon) -> Result<VelocitySample, FieldError> {
        let optional = |name: &str| match self.interpolate(name, time, position) {
            Ok(value) => Ok(value),
            Err(FieldError::MissingComponent(_)) => Ok(0.0),
            Err(error) => Err(error),
        };
        Ok(VelocitySample {
            east_mps: self.interpolate("u", time, position)?,
            north_mps: self.interpolate("v", time, position)?,
            east_standard_error_mps: optional("u_error")?,
            north_standard_error_mps: optional("v_error")?,
        })
    }

    pub fn interpolate(
        &self,
        component: &str,
        time: f64,
        position: LatLon,
    ) -> Result<f64, FieldError> {
        let values = self
            .components
            .get(component)
            .ok_or_else(|| FieldError::MissingComponent(component.to_string()))?;
        let (ta, tb, tf) = self.time_bracket(time)?;
        let (ya, yb, yf) =
            bracket(&self.latitudes, position.latitude.0).ok_or(FieldError::OutsideSpace)?;
        let (xa, xb, xf) =
            bracket(&self.longitudes, position.longitude.0).ok_or(FieldError::OutsideSpace)?;
        let first = self.spatial(values, ta, ya, yb, xa, xb, yf, xf)?;
        if ta == tb {
            return Ok(first);
        }
        let second = self.spatial(values, tb, ya, yb, xa, xb, yf, xf)?;
        Ok(first + tf * (second - first))
    }

    #[allow(clippy::too_many_arguments)]
    fn spatial(
        &self,
        values: &FieldComponent,
        time: usize,
        ya: usize,
        yb: usize,
        xa: usize,
        xb: usize,
        yf: f64,
        xf: f64,
    ) -> Result<f64, FieldError> {
        let index =
            |y: usize, x: usize| (time * self.latitudes.len() + y) * self.longitudes.len() + x;
        let indices = [index(ya, xa), index(ya, xb), index(yb, xa), index(yb, xb)];
        let corners = indices.map(|index| values.value(index));
        if self.renormalize_finite_spatial_corners {
            let weights = [
                (1.0 - yf) * (1.0 - xf),
                (1.0 - yf) * xf,
                yf * (1.0 - xf),
                yf * xf,
            ];
            let mut weighted_value = 0.0;
            let mut finite_weight = 0.0;
            for ((value, index), weight) in corners.into_iter().zip(indices).zip(weights) {
                if value.is_finite() && weight > 0.0 {
                    weighted_value += weight * value;
                    finite_weight += weight;
                } else if weight > 0.0 && !values.is_persistent_land_mask(index) {
                    return Err(FieldError::MissingValue);
                }
            }
            if finite_weight <= f64::EPSILON {
                return Err(FieldError::MissingValue);
            }
            return Ok(weighted_value / finite_weight);
        } else if corners.iter().any(|value| !value.is_finite()) {
            return Err(FieldError::MissingValue);
        }
        let south = corners[0] + xf * (corners[1] - corners[0]);
        let north = corners[2] + xf * (corners[3] - corners[2]);
        Ok(south + yf * (north - south))
    }

    fn time_bracket(&self, unix_seconds: f64) -> Result<(usize, usize, f64), FieldError> {
        if self.time_axis == FieldTimeAxis::ClimatologicalMonth {
            // A monthly mean is an interval statistic, not an instantaneous
            // value at month start. Use it piecewise over its named month.
            let month = month_index(unix_seconds)?;
            return Ok((month, month, 0.0));
        }
        let bracket = bracket(&self.times, unix_seconds).ok_or(FieldError::OutsideTime)?;
        if let Some(maximum) = self.maximum_time_interpolation_gap_seconds {
            if bracket.0 != bracket.1 && self.times[bracket.1] - self.times[bracket.0] > maximum {
                return Err(FieldError::OutsideTime);
            }
        }
        Ok(bracket)
    }
}

fn increasing(values: &[f64]) -> bool {
    values.iter().all(|v| v.is_finite()) && values.windows(2).all(|p| p[1] > p[0])
}
fn bracket(values: &[f64], value: f64) -> Option<(usize, usize, f64)> {
    if !value.is_finite() || value < values[0] || value > *values.last()? {
        return None;
    }
    match values.binary_search_by(|candidate| candidate.total_cmp(&value)) {
        Ok(i) => Some((i, i, 0.0)),
        Err(upper) => {
            let lower = upper.checked_sub(1)?;
            Some((
                lower,
                upper,
                (value - values[lower]) / (values[upper] - values[lower]),
            ))
        }
    }
}

fn month_index(unix_seconds: f64) -> Result<usize, FieldError> {
    if !unix_seconds.is_finite() {
        return Err(FieldError::OutsideTime);
    }
    let days = (unix_seconds / 86_400.0).floor() as i64;
    let (_, month, _) = civil_from_days(days);
    Ok((month - 1) as usize)
}

// Howard Hinnant's public-domain civil calendar conversion, shifted to Unix.
fn civil_from_days(days_since_1970: i64) -> (i64, i64, i64) {
    let z = days_since_1970 + 719_468;
    let era = if z >= 0 { z } else { z - 146_096 } / 146_097;
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1_460 + doe / 36_524 - doe / 146_096) / 365;
    let mut year = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let day = doy - (153 * mp + 2) / 5 + 1;
    let month = mp + if mp < 10 { 3 } else { -9 };
    year += i64::from(month <= 2);
    (year, month, day)
}

struct Reader<R> {
    input: R,
}
impl<R: Read> Reader<R> {
    fn new(input: R) -> Self {
        Self { input }
    }
    fn fixed<const N: usize>(&mut self) -> Result<[u8; N], FieldError> {
        let mut bytes = [0; N];
        self.input
            .read_exact(&mut bytes)
            .map_err(|_| FieldError::InvalidFormat("truncated"))?;
        Ok(bytes)
    }
    fn is_exhausted(&mut self) -> Result<bool, FieldError> {
        let mut byte = [0];
        self.input
            .read(&mut byte)
            .map(|count| count == 0)
            .map_err(|_| FieldError::InvalidFormat("read failure"))
    }
    fn u32(&mut self) -> Result<u32, FieldError> {
        Ok(u32::from_le_bytes(self.fixed()?))
    }
    fn i16(&mut self) -> Result<i16, FieldError> {
        Ok(i16::from_le_bytes(self.fixed()?))
    }
    fn f64(&mut self) -> Result<f64, FieldError> {
        Ok(f64::from_le_bytes(self.fixed()?))
    }
    fn f64s(&mut self, count: usize) -> Result<Vec<f64>, FieldError> {
        self.values(count, 8, |value| {
            f64::from_le_bytes(value.try_into().unwrap())
        })
    }
    fn f32s(&mut self, count: usize) -> Result<Vec<f32>, FieldError> {
        self.values(count, 4, |value| {
            f32::from_le_bytes(value.try_into().unwrap())
        })
    }
    fn i16s(&mut self, count: usize) -> Result<Vec<i16>, FieldError> {
        self.values(count, 2, |value| {
            i16::from_le_bytes(value.try_into().unwrap())
        })
    }
    fn packed_i16s(
        &mut self,
        count: usize,
        file_backed_threshold_bytes: usize,
    ) -> Result<PackedI16Values, FieldError> {
        let byte_count = count
            .checked_mul(2)
            .ok_or(FieldError::InvalidFormat("dimension overflow"))?;
        if byte_count < file_backed_threshold_bytes {
            return self.i16s(count).map(PackedI16Values::Owned);
        }

        let mut file = tempfile::tempfile().map_err(storage_error)?;
        let mut buffer = vec![0; FILE_BACKED_COPY_BUFFER_BYTES.min(byte_count)];
        let mut remaining = byte_count;
        while remaining > 0 {
            let length = remaining.min(buffer.len());
            self.input
                .read_exact(&mut buffer[..length])
                .map_err(|_| FieldError::InvalidFormat("truncated"))?;
            file.write_all(&buffer[..length]).map_err(storage_error)?;
            remaining -= length;
        }
        file.sync_data().map_err(storage_error)?;

        let file = Arc::new(file);
        // SAFETY: `tempfile()` creates a private unnamed file. The retained
        // `Arc<File>` is never exposed or mutated after this point, so the
        // mapped byte range cannot be truncated or changed while it is read.
        let bytes = unsafe {
            MmapOptions::new()
                .len(byte_count)
                .map(file.as_ref())
                .map_err(storage_error)?
        };
        Ok(PackedI16Values::FileBacked {
            bytes: Arc::new(bytes),
            _file: file,
        })
    }
    fn values<T>(
        &mut self,
        count: usize,
        width: usize,
        decode: impl Fn(&[u8]) -> T,
    ) -> Result<Vec<T>, FieldError> {
        count
            .checked_mul(width)
            .ok_or(FieldError::InvalidFormat("dimension overflow"))?;
        let elements_per_chunk = (1024 * 1024 / width).max(1);
        let mut bytes = vec![0; elements_per_chunk * width];
        let mut values = Vec::with_capacity(count);
        while values.len() < count {
            let element_count = (count - values.len()).min(elements_per_chunk);
            let byte_count = element_count * width;
            self.input
                .read_exact(&mut bytes[..byte_count])
                .map_err(|_| FieldError::InvalidFormat("truncated"))?;
            values.extend(bytes[..byte_count].chunks_exact(width).map(&decode));
        }
        Ok(values)
    }
}

fn storage_error(error: std::io::Error) -> FieldError {
    FieldError::Storage(error.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_abs_diff_eq;
    fn fixture(monthly: bool) -> Vec<u8> {
        let times = if monthly {
            (0..12).map(f64::from).collect::<Vec<_>>()
        } else {
            vec![0.0, 10.0]
        };
        let mut bytes = MAGIC.to_vec();
        bytes.extend(1u32.to_le_bytes());
        bytes.extend(u32::from(monthly).to_le_bytes());
        bytes.extend((times.len() as u32).to_le_bytes());
        bytes.extend(2u32.to_le_bytes());
        bytes.extend(2u32.to_le_bytes());
        bytes.extend(1u32.to_le_bytes());
        for value in times {
            bytes.extend(value.to_le_bytes());
        }
        for value in [-1.0_f64, 1.0, 10.0, 12.0] {
            bytes.extend(value.to_le_bytes());
        }
        let mut name = [0u8; 16];
        name[0] = b'u';
        bytes.extend(name);
        let count = if monthly { 48 } else { 8 };
        for index in 0..count {
            bytes.extend((index as f32).to_le_bytes());
        }
        bytes
    }
    #[test]
    fn trilinear_axis_order_matches_independent_calculation() {
        let f = GriddedField::from_bytes("fixture", &fixture(false)).unwrap();
        assert_abs_diff_eq!(
            f.interpolate("u", 5.0, LatLon::new(0.0, 11.0).unwrap())
                .unwrap(),
            3.5,
            epsilon = 1e-12
        );
    }
    #[test]
    fn january_is_month_zero() {
        let f = GriddedField::from_bytes("fixture", &fixture(true)).unwrap();
        assert_abs_diff_eq!(
            f.interpolate("u", 1_420_070_400.0, LatLon::new(-1.0, 10.0).unwrap())
                .unwrap(),
            0.0,
            epsilon = 1e-12
        );
    }

    #[test]
    fn packed_i16_preserves_scale_and_missing_values() {
        let mut bytes = MAGIC.to_vec();
        bytes.extend(2u32.to_le_bytes());
        bytes.extend(0u32.to_le_bytes());
        for value in [2u32, 2, 2, 1] {
            bytes.extend(value.to_le_bytes());
        }
        for value in [0.0_f64, 10.0, -1.0, 1.0, 10.0, 12.0] {
            bytes.extend(value.to_le_bytes());
        }
        let mut name = [0u8; 16];
        name[0] = b'u';
        bytes.extend(name);
        bytes.extend(PACKED_I16.to_le_bytes());
        bytes.extend(0.001_f64.to_le_bytes());
        bytes.extend(0.0_f64.to_le_bytes());
        bytes.extend((-30_000_i16).to_le_bytes());
        for value in [100_i16, 200, 300, 400, 500, 600, 700, 800] {
            bytes.extend(value.to_le_bytes());
        }
        let field = GriddedField::from_bytes("packed", &bytes).unwrap();
        assert_abs_diff_eq!(
            field
                .interpolate("u", 5.0, LatLon::new(0.0, 11.0).unwrap())
                .unwrap(),
            0.45,
            epsilon = 1e-12
        );
    }

    #[test]
    fn file_backed_packed_values_match_owned_values_and_reject_truncation() {
        let expected = [-29_999_i16, -12, 0, 32_767];
        let bytes = expected
            .iter()
            .flat_map(|value| value.to_le_bytes())
            .collect::<Vec<_>>();

        let mut owned_reader = Reader::new(bytes.as_slice());
        let owned = owned_reader
            .packed_i16s(expected.len(), usize::MAX)
            .unwrap();
        assert!(matches!(owned, PackedI16Values::Owned(_)));

        let mut mapped_reader = Reader::new(bytes.as_slice());
        let mapped = mapped_reader.packed_i16s(expected.len(), 0).unwrap();
        assert!(matches!(mapped, PackedI16Values::FileBacked { .. }));
        for (index, value) in expected.into_iter().enumerate() {
            assert_eq!(owned.value(index), value);
            assert_eq!(mapped.value(index), value);
        }

        let mut truncated_reader = Reader::new(&bytes[..bytes.len() - 1]);
        assert!(matches!(
            truncated_reader.packed_i16s(expected.len(), 0),
            Err(FieldError::InvalidFormat("truncated"))
        ));
    }

    #[test]
    fn configured_time_gap_is_outside_support_not_interpolated() {
        let mut field = GriddedField::from_bytes("gap", &fixture(false)).unwrap();
        field
            .set_maximum_time_interpolation_gap_seconds(Some(4.0))
            .unwrap();
        assert_eq!(
            field.interpolate("u", 5.0, LatLon::new(0.0, 11.0).unwrap()),
            Err(FieldError::OutsideTime)
        );
        assert!(field
            .interpolate("u", 0.0, LatLon::new(0.0, 11.0).unwrap())
            .is_ok());
    }

    #[test]
    fn finite_corner_renormalization_is_explicit_and_never_uses_zero() {
        let mut bytes = MAGIC.to_vec();
        bytes.extend(3u32.to_le_bytes());
        bytes.extend(0u32.to_le_bytes());
        for value in [2u32, 2, 2, 1] {
            bytes.extend(value.to_le_bytes());
        }
        for value in [0.0_f64, 10.0, -1.0, 1.0, 10.0, 12.0] {
            bytes.extend(value.to_le_bytes());
        }
        let mut name = [0u8; 16];
        name[0] = b'u';
        bytes.extend(name);
        bytes.extend(PACKED_I16.to_le_bytes());
        bytes.extend(0.001_f64.to_le_bytes());
        bytes.extend(0.0_f64.to_le_bytes());
        bytes.extend((-30_000_i16).to_le_bytes());
        bytes.extend((-29_999_i16).to_le_bytes());
        for value in [-29_999_i16, 200, 300, 400, -29_999, 200, 300, 400] {
            bytes.extend(value.to_le_bytes());
        }
        let mut field = GriddedField::from_bytes("coastal-mask", &bytes).unwrap();
        let point = LatLon::new(0.0, 11.0).unwrap();
        assert_eq!(
            field.interpolate("u", 0.0, point),
            Err(FieldError::MissingValue)
        );
        field.set_renormalize_finite_spatial_corners(true);
        assert_abs_diff_eq!(
            field.interpolate("u", 0.0, point).unwrap(),
            0.3,
            epsilon = 1e-12
        );
        let missing_node = LatLon::new(-1.0, 10.0).unwrap();
        assert_eq!(
            field.interpolate("u", 0.0, missing_node),
            Err(FieldError::MissingValue)
        );

        let first_value_offset = 8 + 6 * 4 + 6 * 8 + 16 + 4 + 8 + 8 + 2 + 2;
        bytes[first_value_offset..first_value_offset + 2]
            .copy_from_slice(&(-30_000_i16).to_le_bytes());
        let mut transient_gap = GriddedField::from_bytes("transient-gap", &bytes).unwrap();
        transient_gap.set_renormalize_finite_spatial_corners(true);
        assert_eq!(
            transient_gap.interpolate("u", 0.0, point),
            Err(FieldError::MissingValue)
        );
    }
}
