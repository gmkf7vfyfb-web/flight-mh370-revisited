mod bfo_table;
mod known_flight_png;

pub use bfo_table::{build_bfo_match_tables_svg, BfoMatchTablePanel, BfoMatchTables};
pub use known_flight_png::{build_accident_panel_png, build_known_flight_panel_png};

use std::fmt::Write as _;

use serde::{Deserialize, Serialize};
use thiserror::Error;

const PAGE_WIDTH: f64 = 595.0;
const PAGE_HEIGHT: f64 = 842.0;
const NAVY: (f64, f64, f64) = (0.055, 0.122, 0.208);
const BLUE: (f64, f64, f64) = (0.08, 0.35, 0.58);
const ORANGE: (f64, f64, f64) = (0.94, 0.48, 0.18);
const LIGHT: (f64, f64, f64) = (0.94, 0.96, 0.98);
const GREY: (f64, f64, f64) = (0.35, 0.39, 0.44);
const HPD_50: [u8; 3] = [139, 135, 181];
const HPD_90: [u8; 3] = [174, 173, 207];
const HPD_95: [u8; 3] = [199, 201, 220];
const HPD_99: [u8; 3] = [226, 228, 237];
const CONTOUR_50: [u8; 3] = [81, 65, 116];
const CONTOUR_90: [u8; 3] = [107, 101, 143];
const CONTOUR_95: [u8; 3] = [137, 139, 160];
const CONTOUR_99: [u8; 3] = [92, 92, 92];
const DISPLAY_KERNEL_NOTICE: &str = "HPD contours use a fixed 5-cell display kernel; estimator weights and numerical summaries are unchanged.";

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ReportPoint {
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    pub weight: f64,
}

/// Common-raster comparison of two spatial posterior measures.
///
/// These metrics use the same fixed display kernel as the publication maps.
/// They are descriptive comparisons of model-conditional posteriors, not a
/// Bayes factor or a probability assigned to either model family.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PosteriorSpatialComparison {
    pub raster_columns: usize,
    pub raster_rows: usize,
    pub bounds: ReportMapBounds,
    pub overlap_coefficient: f64,
    pub total_variation_distance: f64,
    pub jensen_shannon_divergence_nats: f64,
    pub first_hpd_area_km2: PosteriorHpdArea,
    pub second_hpd_area_km2: PosteriorHpdArea,
    pub method: String,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct PosteriorHpdArea {
    pub mass_50: f64,
    pub mass_90: f64,
    pub mass_95: f64,
    pub mass_99: f64,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct ReportMapBounds {
    pub longitude_min_deg: f64,
    pub longitude_max_deg: f64,
    pub latitude_min_deg: f64,
    pub latitude_max_deg: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ReportMapReference {
    pub label: String,
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    pub heading_true_deg: Option<f64>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ReportMapRoute {
    pub label: String,
    #[serde(default)]
    pub style: String,
    /// Route coordinates in latitude, longitude order.
    pub coordinates_deg: Vec<[f64; 2]>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ReportMapContext {
    pub bounds: ReportMapBounds,
    #[serde(default)]
    pub references: Vec<ReportMapReference>,
    #[serde(default)]
    pub routes: Vec<ReportMapRoute>,
}
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DiagnosticPoint {
    pub label: String,
    pub effective_sample_size: f64,
    pub log_evidence_increment: f64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ReportDocument {
    pub title: String,
    pub subtitle: String,
    pub summary: Vec<(String, String)>,
    pub points: Vec<ReportPoint>,
    pub diagnostics: Vec<DiagnosticPoint>,
    pub evidence_conditions: Vec<String>,
    pub limitations: Vec<String>,
    pub map_context: Option<ReportMapContext>,
}

#[derive(Debug, Error)]
pub enum ReportError {
    #[error("report title or posterior point set is empty")]
    EmptyReport,
    #[error("posterior contains invalid coordinates or weights")]
    InvalidPosterior,
    #[error("posterior has zero total probability")]
    ZeroMass,
    #[error("report map bounds are invalid")]
    InvalidMapBounds,
    #[error("embedded map background is invalid")]
    InvalidMapBackground,
    #[error("embedded report font is invalid")]
    InvalidReportFont,
    #[error("raw-BFO feasibility table is incomplete or invalid")]
    InvalidBfoTable,
    #[error("PNG encoding failed: {0}")]
    PngEncoding(String),
}

#[derive(Clone)]
struct Grid {
    longitude_min: f64,
    longitude_max: f64,
    latitude_min: f64,
    latitude_max: f64,
    columns: usize,
    rows: usize,
    mass: Vec<f64>,
}

#[derive(Clone)]
struct DensitySurface {
    mass: Vec<f64>,
    threshold_50: f64,
    threshold_90: f64,
    threshold_95: f64,
    threshold_99: f64,
}

#[derive(Debug, Clone, Copy, PartialEq)]
struct ContourSegment {
    start: (f64, f64),
    end: (f64, f64),
}

fn validate(document: &ReportDocument) -> Result<(), ReportError> {
    if document.title.trim().is_empty() || document.points.is_empty() {
        return Err(ReportError::EmptyReport);
    }
    if document.points.iter().any(|point| {
        !point.latitude_deg.is_finite()
            || !point.longitude_deg.is_finite()
            || !point.weight.is_finite()
            || point.weight < 0.0
            || !(-90.0..=90.0).contains(&point.latitude_deg)
    }) {
        return Err(ReportError::InvalidPosterior);
    }
    if document
        .points
        .iter()
        .map(|point| point.weight)
        .sum::<f64>()
        <= 0.0
    {
        return Err(ReportError::ZeroMass);
    }
    Ok(())
}

fn grid_with_bounds(
    points: &[ReportPoint],
    required: Option<(f64, f64)>,
    fixed: Option<ReportMapBounds>,
) -> Result<Grid, ReportError> {
    if let Some(bounds) = fixed {
        if !bounds.longitude_min_deg.is_finite()
            || !bounds.longitude_max_deg.is_finite()
            || !bounds.latitude_min_deg.is_finite()
            || !bounds.latitude_max_deg.is_finite()
            || bounds.longitude_min_deg >= bounds.longitude_max_deg
            || bounds.latitude_min_deg >= bounds.latitude_max_deg
            || bounds.latitude_min_deg < -90.0
            || bounds.latitude_max_deg > 90.0
        {
            return Err(ReportError::InvalidMapBounds);
        }
    }
    let positive = points
        .iter()
        .filter(|point| point.weight > 0.0)
        .collect::<Vec<_>>();
    let support_longitude_min = positive
        .iter()
        .map(|point| point.longitude_deg)
        .fold(f64::INFINITY, f64::min);
    let support_longitude_max = positive
        .iter()
        .map(|point| point.longitude_deg)
        .fold(f64::NEG_INFINITY, f64::max);
    let support_latitude_min = positive
        .iter()
        .map(|point| point.latitude_deg)
        .fold(f64::INFINITY, f64::min);
    let support_latitude_max = positive
        .iter()
        .map(|point| point.latitude_deg)
        .fold(f64::NEG_INFINITY, f64::max);
    let mut longitude_min = fixed
        .map(|value| value.longitude_min_deg)
        .unwrap_or(support_longitude_min);
    let mut longitude_max = fixed
        .map(|value| value.longitude_max_deg)
        .unwrap_or(support_longitude_max);
    let mut latitude_min = fixed
        .map(|value| value.latitude_min_deg)
        .unwrap_or(support_latitude_min);
    let mut latitude_max = fixed
        .map(|value| value.latitude_max_deg)
        .unwrap_or(support_latitude_max);
    let support_touches_or_exceeds_bounds = support_longitude_min <= longitude_min
        || support_longitude_max >= longitude_max
        || support_latitude_min <= latitude_min
        || support_latitude_max >= latitude_max;
    longitude_min = longitude_min.min(support_longitude_min);
    longitude_max = longitude_max.max(support_longitude_max);
    latitude_min = latitude_min.min(support_latitude_min);
    latitude_max = latitude_max.max(support_latitude_max);
    if let Some((latitude, longitude)) = required {
        latitude_min = latitude_min.min(latitude);
        latitude_max = latitude_max.max(latitude);
        longitude_min = longitude_min.min(longitude);
        longitude_max = longitude_max.max(longitude);
    }
    if longitude_max - longitude_min < 1e-6 {
        longitude_min -= 0.5;
        longitude_max += 0.5;
    }
    if latitude_max - latitude_min < 1e-6 {
        latitude_min -= 0.5;
        latitude_max += 0.5;
    }
    if fixed.is_none() || support_touches_or_exceeds_bounds {
        let longitude_margin = 0.05 * (longitude_max - longitude_min);
        let latitude_margin = 0.05 * (latitude_max - latitude_min);
        longitude_min -= longitude_margin;
        longitude_max += longitude_margin;
        latitude_min = (latitude_min - latitude_margin).max(-90.0);
        latitude_max = (latitude_max + latitude_margin).min(90.0);
    }

    let columns = 64usize;
    let rows = 64usize;
    let mut mass = vec![0.0; columns * rows];
    for point in points {
        if point.weight == 0.0 {
            continue;
        }
        let x = ((point.longitude_deg - longitude_min) / (longitude_max - longitude_min)
            * columns as f64)
            .floor()
            .clamp(0.0, (columns - 1) as f64) as usize;
        let y = ((point.latitude_deg - latitude_min) / (latitude_max - latitude_min) * rows as f64)
            .floor()
            .clamp(0.0, (rows - 1) as f64) as usize;
        mass[y * columns + x] += point.weight;
    }
    let total = mass.iter().sum::<f64>();
    if total <= 0.0 {
        return Err(ReportError::ZeroMass);
    }
    for value in &mut mass {
        *value /= total;
    }
    Ok(Grid {
        longitude_min,
        longitude_max,
        latitude_min,
        latitude_max,
        columns,
        rows,
        mass,
    })
}

fn grid(points: &[ReportPoint], required: Option<(f64, f64)>) -> Result<Grid, ReportError> {
    grid_with_bounds(points, required, None)
}

fn grid_on_geometry(points: &[ReportPoint], geometry: &Grid) -> Result<Grid, ReportError> {
    if points.is_empty()
        || points.iter().any(|point| {
            !point.latitude_deg.is_finite()
                || !point.longitude_deg.is_finite()
                || !point.weight.is_finite()
                || point.weight < 0.0
                || point.latitude_deg < geometry.latitude_min
                || point.latitude_deg > geometry.latitude_max
                || point.longitude_deg < geometry.longitude_min
                || point.longitude_deg > geometry.longitude_max
        })
    {
        return Err(ReportError::InvalidPosterior);
    }
    let mut mass = vec![0.0; geometry.columns * geometry.rows];
    for point in points.iter().filter(|point| point.weight > 0.0) {
        let column = ((point.longitude_deg - geometry.longitude_min)
            / (geometry.longitude_max - geometry.longitude_min)
            * geometry.columns as f64)
            .floor()
            .clamp(0.0, (geometry.columns - 1) as f64) as usize;
        let row = ((point.latitude_deg - geometry.latitude_min)
            / (geometry.latitude_max - geometry.latitude_min)
            * geometry.rows as f64)
            .floor()
            .clamp(0.0, (geometry.rows - 1) as f64) as usize;
        mass[row * geometry.columns + column] += point.weight;
    }
    let total = mass.iter().sum::<f64>();
    if !total.is_finite() || total <= 0.0 {
        return Err(ReportError::ZeroMass);
    }
    for value in &mut mass {
        *value /= total;
    }
    Ok(Grid {
        longitude_min: geometry.longitude_min,
        longitude_max: geometry.longitude_max,
        latitude_min: geometry.latitude_min,
        latitude_max: geometry.latitude_max,
        columns: geometry.columns,
        rows: geometry.rows,
        mass,
    })
}

fn density_threshold(values: &[f64], probability: f64) -> f64 {
    let mut ranked = values.to_vec();
    ranked.sort_by(|first, second| second.total_cmp(first));
    let total = ranked.iter().sum::<f64>();
    let mut cumulative = 0.0;
    for value in ranked {
        cumulative += value;
        if cumulative >= probability * total {
            return value;
        }
    }
    0.0
}

fn smooth_density(grid: &Grid) -> DensitySurface {
    let kernel = [0.06136, 0.24477, 0.38774, 0.24477, 0.06136];
    let mut horizontal = vec![0.0; grid.mass.len()];
    for row in 0..grid.rows {
        for column in 0..grid.columns {
            for (offset, weight) in kernel.iter().enumerate() {
                let source = column as isize + offset as isize - 2;
                if (0..grid.columns as isize).contains(&source) {
                    horizontal[row * grid.columns + column] +=
                        grid.mass[row * grid.columns + source as usize] * weight;
                }
            }
        }
    }
    let mut mass = vec![0.0; grid.mass.len()];
    for row in 0..grid.rows {
        for column in 0..grid.columns {
            for (offset, weight) in kernel.iter().enumerate() {
                let source = row as isize + offset as isize - 2;
                if (0..grid.rows as isize).contains(&source) {
                    mass[row * grid.columns + column] +=
                        horizontal[source as usize * grid.columns + column] * weight;
                }
            }
        }
    }
    let total = mass.iter().sum::<f64>();
    for value in &mut mass {
        *value /= total;
    }
    DensitySurface {
        threshold_50: density_threshold(&mass, 0.5),
        threshold_90: density_threshold(&mass, 0.9),
        threshold_95: density_threshold(&mass, 0.95),
        threshold_99: density_threshold(&mass, 0.99),
        mass,
    }
}

fn hpd_area_km2(grid: &Grid, density: &DensitySurface, threshold: f64) -> f64 {
    const EARTH_MEAN_RADIUS_KM: f64 = 6_371.008_8;
    let longitude_width_rad =
        ((grid.longitude_max - grid.longitude_min) / grid.columns as f64).to_radians();
    let latitude_height_deg = (grid.latitude_max - grid.latitude_min) / grid.rows as f64;
    let mut area = 0.0;
    for row in 0..grid.rows {
        let latitude_lower = grid.latitude_min + row as f64 * latitude_height_deg;
        let latitude_upper = latitude_lower + latitude_height_deg;
        let cell_area = EARTH_MEAN_RADIUS_KM.powi(2)
            * longitude_width_rad
            * (latitude_upper.to_radians().sin() - latitude_lower.to_radians().sin()).abs();
        for column in 0..grid.columns {
            if density.mass[row * grid.columns + column] >= threshold {
                area += cell_area;
            }
        }
    }
    area
}

fn hpd_areas(grid: &Grid, density: &DensitySurface) -> PosteriorHpdArea {
    PosteriorHpdArea {
        mass_50: hpd_area_km2(grid, density, density.threshold_50),
        mass_90: hpd_area_km2(grid, density, density.threshold_90),
        mass_95: hpd_area_km2(grid, density, density.threshold_95),
        mass_99: hpd_area_km2(grid, density, density.threshold_99),
    }
}

/// Compare two weighted spatial posteriors on one union-support raster.
pub fn compare_spatial_posteriors(
    first: &[ReportPoint],
    second: &[ReportPoint],
) -> Result<PosteriorSpatialComparison, ReportError> {
    let mut union = Vec::with_capacity(first.len() + second.len());
    union.extend_from_slice(first);
    union.extend_from_slice(second);
    let geometry = grid(&union, None)?;
    let first_grid = grid_on_geometry(first, &geometry)?;
    let second_grid = grid_on_geometry(second, &geometry)?;
    let first_density = smooth_density(&first_grid);
    let second_density = smooth_density(&second_grid);

    let overlap_coefficient = first_density
        .mass
        .iter()
        .zip(&second_density.mass)
        .map(|(first, second)| first.min(*second))
        .sum::<f64>();
    let total_variation_distance = 0.5
        * first_density
            .mass
            .iter()
            .zip(&second_density.mass)
            .map(|(first, second)| (first - second).abs())
            .sum::<f64>();
    let jensen_shannon_divergence_nats = first_density
        .mass
        .iter()
        .zip(&second_density.mass)
        .map(|(first, second)| {
            let midpoint = 0.5 * (first + second);
            let first_term = if *first > 0.0 {
                0.5 * first * (first / midpoint).ln()
            } else {
                0.0
            };
            let second_term = if *second > 0.0 {
                0.5 * second * (second / midpoint).ln()
            } else {
                0.0
            };
            first_term + second_term
        })
        .sum::<f64>();

    Ok(PosteriorSpatialComparison {
        raster_columns: geometry.columns,
        raster_rows: geometry.rows,
        bounds: ReportMapBounds {
            longitude_min_deg: geometry.longitude_min,
            longitude_max_deg: geometry.longitude_max,
            latitude_min_deg: geometry.latitude_min,
            latitude_max_deg: geometry.latitude_max,
        },
        overlap_coefficient,
        total_variation_distance,
        jensen_shannon_divergence_nats,
        first_hpd_area_km2: hpd_areas(&first_grid, &first_density),
        second_hpd_area_km2: hpd_areas(&second_grid, &second_density),
        method: "64x64 union-support raster with the publication 5-cell separable display kernel; descriptive model-family comparison only".to_string(),
    })
}

fn density_sample(density: &DensitySurface, grid: &Grid, x: f64, y: f64) -> f64 {
    let grid_x = x.clamp(0.0, 1.0) * (grid.columns - 1) as f64;
    let grid_y = y.clamp(0.0, 1.0) * (grid.rows - 1) as f64;
    let x0 = grid_x.floor() as usize;
    let y0 = grid_y.floor() as usize;
    let x1 = (x0 + 1).min(grid.columns - 1);
    let y1 = (y0 + 1).min(grid.rows - 1);
    let tx = grid_x - x0 as f64;
    let ty = grid_y - y0 as f64;
    let at = |column: usize, row: usize| density.mass[row * grid.columns + column];
    let bottom = at(x0, y0) * (1.0 - tx) + at(x1, y0) * tx;
    let top = at(x0, y1) * (1.0 - tx) + at(x1, y1) * tx;
    bottom * (1.0 - ty) + top * ty
}

fn density_band(value: f64, density: &DensitySurface) -> Option<([u8; 3], u8)> {
    if value >= density.threshold_50 {
        Some((HPD_50, 84))
    } else if value >= density.threshold_90 {
        Some((HPD_90, 62))
    } else if value >= density.threshold_95 {
        Some((HPD_95, 44))
    } else if value >= density.threshold_99 {
        Some((HPD_99, 28))
    } else {
        None
    }
}

fn contour_intersection(
    first: (f64, f64, f64),
    second: (f64, f64, f64),
    threshold: f64,
) -> (f64, f64) {
    let fraction = if (second.2 - first.2).abs() < 1e-18 {
        0.5
    } else {
        ((threshold - first.2) / (second.2 - first.2)).clamp(0.0, 1.0)
    };
    (
        first.0 + fraction * (second.0 - first.0),
        first.1 + fraction * (second.1 - first.1),
    )
}

fn segment_pair_distance(first: (f64, f64), second: (f64, f64)) -> f64 {
    (first.0 - second.0).hypot(first.1 - second.1)
}

fn contour_segments(grid: &Grid, density: &DensitySurface, threshold: f64) -> Vec<ContourSegment> {
    let node = |column: usize, row: usize, value: f64| {
        (
            column as f64 / (grid.columns - 1) as f64,
            row as f64 / (grid.rows - 1) as f64,
            value,
        )
    };
    let mut segments = Vec::new();
    for row in 0..grid.rows - 1 {
        for column in 0..grid.columns - 1 {
            let bottom_left = node(column, row, density.mass[row * grid.columns + column]);
            let bottom_right = node(
                column + 1,
                row,
                density.mass[row * grid.columns + column + 1],
            );
            let top_right = node(
                column + 1,
                row + 1,
                density.mass[(row + 1) * grid.columns + column + 1],
            );
            let top_left = node(
                column,
                row + 1,
                density.mass[(row + 1) * grid.columns + column],
            );
            let mut crossings = Vec::new();
            for (first, second) in [
                (bottom_left, bottom_right),
                (bottom_right, top_right),
                (top_right, top_left),
                (top_left, bottom_left),
            ] {
                if (first.2 >= threshold) != (second.2 >= threshold) {
                    crossings.push(contour_intersection(first, second, threshold));
                }
            }
            let pairs = if crossings.len() == 2 {
                vec![(0, 1)]
            } else if crossings.len() == 4 {
                let pairing_a = segment_pair_distance(crossings[0], crossings[1])
                    + segment_pair_distance(crossings[2], crossings[3]);
                let pairing_b = segment_pair_distance(crossings[0], crossings[3])
                    + segment_pair_distance(crossings[1], crossings[2]);
                if pairing_a <= pairing_b {
                    vec![(0, 1), (2, 3)]
                } else {
                    vec![(0, 3), (1, 2)]
                }
            } else {
                Vec::new()
            };
            for (first, second) in pairs {
                segments.push(ContourSegment {
                    start: crossings[first],
                    end: crossings[second],
                });
            }
        }
    }
    segments
}

fn ascii(value: &str) -> String {
    value
        .chars()
        .map(|character| match character {
            '°' => " deg ".to_string(),
            '–' | '—' => "-".to_string(),
            '×' => "x".to_string(),
            '‰' => " per mil".to_string(),
            '²' => "^2".to_string(),
            '±' => "+/-".to_string(),
            '≤' => "<=".to_string(),
            '≥' => ">=".to_string(),
            character if character.is_ascii() => character.to_string(),
            _ => "?".to_string(),
        })
        .collect()
}

fn pdf_escape(value: &str) -> String {
    ascii(value)
        .replace('\\', "\\\\")
        .replace('(', "\\(")
        .replace(')', "\\)")
}

struct Canvas {
    content: String,
}

impl Canvas {
    fn new() -> Self {
        Self {
            content: String::new(),
        }
    }

    fn fill_rect(&mut self, x: f64, y: f64, width: f64, height: f64, color: (f64, f64, f64)) {
        let _ = writeln!(
            self.content,
            "{:.3} {:.3} {:.3} rg {:.2} {:.2} {:.2} {:.2} re f",
            color.0, color.1, color.2, x, y, width, height
        );
    }

    fn stroke_rect(
        &mut self,
        x: f64,
        y: f64,
        width: f64,
        height: f64,
        color: (f64, f64, f64),
        line_width: f64,
    ) {
        let _ = writeln!(
            self.content,
            "{:.3} {:.3} {:.3} RG {:.2} w {:.2} {:.2} {:.2} {:.2} re S",
            color.0, color.1, color.2, line_width, x, y, width, height
        );
    }

    fn line(
        &mut self,
        x1: f64,
        y1: f64,
        x2: f64,
        y2: f64,
        color: (f64, f64, f64),
        line_width: f64,
    ) {
        let _ = writeln!(
            self.content,
            "{:.3} {:.3} {:.3} RG {:.2} w {:.2} {:.2} m {:.2} {:.2} l S",
            color.0, color.1, color.2, line_width, x1, y1, x2, y2
        );
    }

    fn text(&mut self, x: f64, y: f64, size: f64, bold: bool, color: (f64, f64, f64), value: &str) {
        let font = if bold { "F2" } else { "F1" };
        let _ = writeln!(
            self.content,
            "BT /{} {:.2} Tf {:.3} {:.3} {:.3} rg {:.2} {:.2} Td ({}) Tj ET",
            font,
            size,
            color.0,
            color.1,
            color.2,
            x,
            y,
            pdf_escape(value)
        );
    }
}

fn pdf_color(color: [u8; 3]) -> (f64, f64, f64) {
    (
        color[0] as f64 / 255.0,
        color[1] as f64 / 255.0,
        color[2] as f64 / 255.0,
    )
}

fn preblended_rgb(color: [u8; 3], alpha: u8) -> [u8; 3] {
    let alpha = alpha as f64 / 255.0;
    color.map(|channel| (255.0 - alpha * (255.0 - channel as f64)).round() as u8)
}

fn preblended_pdf_color(color: [u8; 3], alpha: u8) -> (f64, f64, f64) {
    pdf_color(preblended_rgb(color, alpha))
}

fn draw_map(
    canvas: &mut Canvas,
    grid: &Grid,
    density: &DensitySurface,
    rect: (f64, f64, f64, f64),
    compact: bool,
) {
    let (x, y, width, height) = rect;
    canvas.fill_rect(x, y, width, height, (1.0, 1.0, 1.0));
    let cell_width = width / grid.columns as f64;
    let cell_height = height / grid.rows as f64;
    for row in 0..grid.rows {
        for column in 0..grid.columns {
            let value = density.mass[row * grid.columns + column];
            let Some((color, alpha)) = density_band(value, density) else {
                continue;
            };
            let px = x + column as f64 * cell_width;
            let py = y + row as f64 * cell_height;
            canvas.fill_rect(
                px,
                py,
                cell_width + 0.05,
                cell_height + 0.05,
                preblended_pdf_color(color, alpha),
            );
        }
    }

    for index in 0..=4 {
        let fraction = index as f64 / 4.0;
        let px = x + fraction * width;
        let py = y + fraction * height;
        canvas.line(px, y, px, y + height, (0.82, 0.85, 0.88), 0.35);
        canvas.line(x, py, x + width, py, (0.82, 0.85, 0.88), 0.35);
        let longitude = grid.longitude_min + fraction * (grid.longitude_max - grid.longitude_min);
        let latitude = grid.latitude_min + fraction * (grid.latitude_max - grid.latitude_min);
        canvas.text(
            px - 14.0,
            y - 14.0,
            if compact { 6.5 } else { 8.0 },
            false,
            GREY,
            &format!("{longitude:.1} E"),
        );
        canvas.text(
            x - 39.0,
            py - 2.0,
            if compact { 6.5 } else { 8.0 },
            false,
            GREY,
            &format!("{latitude:.1}"),
        );
    }
    for (threshold, color, line_width) in [
        (density.threshold_99, CONTOUR_99, 0.55),
        (density.threshold_95, CONTOUR_95, 0.75),
        (density.threshold_90, CONTOUR_90, 0.9),
        (density.threshold_50, CONTOUR_50, 1.2),
    ] {
        for segment in contour_segments(grid, density, threshold) {
            canvas.line(
                x + segment.start.0 * width,
                y + segment.start.1 * height,
                x + segment.end.0 * width,
                y + segment.end.1 * height,
                pdf_color(color),
                if compact {
                    line_width * 0.85
                } else {
                    line_width
                },
            );
        }
    }
    canvas.stroke_rect(x, y, width, height, NAVY, 0.8);
    let slot_width = width / 4.0;
    for (index, (label, color, line_width)) in [
        ("50% HPD", CONTOUR_50, 1.2),
        ("90% HPD", CONTOUR_90, 0.9),
        ("95% HPD", CONTOUR_95, 0.75),
        ("99% HPD", CONTOUR_99, 0.55),
    ]
    .iter()
    .enumerate()
    {
        let legend_x = x + index as f64 * slot_width;
        let legend_y = y + height + 11.0;
        canvas.line(
            legend_x,
            legend_y,
            legend_x + 18.0,
            legend_y,
            pdf_color(*color),
            *line_width,
        );
        canvas.text(
            legend_x + 22.0,
            legend_y - 2.5,
            if compact { 6.5 } else { 7.5 },
            false,
            GREY,
            label,
        );
    }
}

fn wrap_lines(value: &str, maximum: usize) -> Vec<String> {
    let value = ascii(value);
    let mut lines = Vec::new();
    let mut current = String::new();
    for word in value.split_whitespace() {
        if !current.is_empty() && current.len() + word.len() + 1 > maximum {
            lines.push(current);
            current = String::new();
        }
        if !current.is_empty() {
            current.push(' ');
        }
        current.push_str(word);
    }
    if !current.is_empty() {
        lines.push(current);
    }
    lines
}

fn first_page(document: &ReportDocument, grid: &Grid, density: &DensitySurface) -> String {
    let mut canvas = Canvas::new();
    canvas.fill_rect(0.0, PAGE_HEIGHT - 116.0, PAGE_WIDTH, 116.0, NAVY);
    let title_lines = wrap_lines(&document.title, 50);
    let title_size = if title_lines.len() == 1 { 22.0 } else { 17.0 };
    let title_start_y = if title_lines.len() == 1 { 790.0 } else { 805.0 };
    for (index, line) in title_lines.iter().enumerate() {
        canvas.text(
            42.0,
            title_start_y - index as f64 * 20.0,
            title_size,
            true,
            (1.0, 1.0, 1.0),
            line,
        );
    }
    let subtitle_start_y = title_start_y - title_lines.len() as f64 * 20.0 - 1.0;
    for (index, line) in wrap_lines(&document.subtitle, 105).iter().enumerate() {
        canvas.text(
            42.0,
            subtitle_start_y - index as f64 * 10.0,
            8.5,
            false,
            (0.82, 0.89, 0.95),
            line,
        );
    }
    canvas.text(42.0, 704.0, 12.0, true, NAVY, "Estimate at a glance");
    let mut y = 681.0;
    for (index, (label, value)) in document.summary.iter().take(8).enumerate() {
        let column = index % 2;
        if index > 0 && column == 0 {
            y -= 37.0;
        }
        let x = 42.0 + column as f64 * 260.0;
        canvas.text(x, y, 7.5, true, GREY, &label.to_uppercase());
        canvas.text(x, y - 15.0, 11.0, false, NAVY, value);
    }
    draw_map(
        &mut canvas,
        grid,
        density,
        (52.0, 178.0, 491.0, 345.0),
        true,
    );
    canvas.text(
        52.0,
        147.0,
        8.0,
        false,
        GREY,
        "Probability is conditional on the named motion, SATCOM, and evidence configuration.",
    );
    canvas.text(52.0, 134.0, 7.2, false, GREY, DISPLAY_KERNEL_NOTICE);
    canvas.line(42.0, 82.0, 553.0, 82.0, (0.75, 0.79, 0.83), 0.5);
    canvas.text(
        42.0,
        62.0,
        7.5,
        false,
        GREY,
        "Generated directly from deterministic run artifacts. No figure has been hand edited.",
    );
    canvas.content
}

fn map_page(_document: &ReportDocument, grid: &Grid, density: &DensitySurface) -> String {
    let mut canvas = Canvas::new();
    canvas.text(48.0, 797.0, 18.0, true, NAVY, "Posterior geography");
    canvas.text(
        48.0,
        777.0,
        8.5,
        false,
        GREY,
        "Highest-density regions are computed from the weighted particle population.",
    );
    canvas.text(48.0, 763.0, 7.2, false, GREY, DISPLAY_KERNEL_NOTICE);
    draw_map(
        &mut canvas,
        grid,
        density,
        (74.0, 164.0, 460.0, 560.0),
        false,
    );
    canvas.text(74.0, 126.0, 8.0, true, NAVY, "Interpretation");
    let note = "The map is a probability density over the modelled impact state. It is not a searched-area elimination map, and structural model alternatives must be compared separately.";
    for (index, line) in wrap_lines(note, 104).iter().enumerate() {
        canvas.text(74.0, 111.0 - index as f64 * 11.0, 7.5, false, GREY, line);
    }
    canvas.content
}

fn diagnostic_page(document: &ReportDocument) -> String {
    let mut canvas = Canvas::new();
    canvas.text(
        48.0,
        797.0,
        18.0,
        true,
        NAVY,
        "Numerical behaviour and conditions",
    );
    canvas.text(
        48.0,
        777.0,
        8.5,
        false,
        GREY,
        "Adaptive likelihood tempering, particle diversity, and declared evidence conditions.",
    );
    let x = 64.0;
    let y = 486.0;
    let width = 480.0;
    let height = 220.0;
    canvas.fill_rect(x, y, width, height, LIGHT);
    let maximum_ess = document
        .diagnostics
        .iter()
        .map(|point| point.effective_sample_size)
        .fold(1.0, f64::max);
    if document.diagnostics.len() > 1 {
        let mut previous = None;
        for (index, point) in document.diagnostics.iter().enumerate() {
            let px =
                x + 24.0 + index as f64 / (document.diagnostics.len() - 1) as f64 * (width - 48.0);
            let py = y + 25.0 + point.effective_sample_size / maximum_ess * (height - 50.0);
            if let Some((last_x, last_y)) = previous {
                canvas.line(last_x, last_y, px, py, BLUE, 1.7);
            }
            canvas.fill_rect(px - 2.0, py - 2.0, 4.0, 4.0, ORANGE);
            if index % 2 == 0 || document.diagnostics.len() <= 8 {
                canvas.text(px - 10.0, y + 8.0, 6.0, false, GREY, &point.label);
            }
            previous = Some((px, py));
        }
    }
    canvas.text(
        x + 8.0,
        y + height + 10.0,
        8.0,
        true,
        NAVY,
        "Effective sample size",
    );
    canvas.text(
        x + width - 118.0,
        y + height + 10.0,
        7.0,
        false,
        GREY,
        &format!("peak {:.0}", maximum_ess),
    );

    canvas.text(48.0, 447.0, 11.0, true, NAVY, "Evidence conditions");
    let mut cursor = 429.0;
    for condition in document.evidence_conditions.iter().take(8) {
        for (line_index, line) in wrap_lines(condition, 102).iter().enumerate() {
            let prefix = if line_index == 0 { "- " } else { "  " };
            canvas.text(54.0, cursor, 7.5, false, GREY, &format!("{prefix}{line}"));
            cursor -= 10.0;
        }
        cursor -= 3.0;
    }

    cursor = cursor.min(295.0);
    canvas.text(48.0, cursor, 11.0, true, NAVY, "Material limitations");
    cursor -= 18.0;
    for limitation in document.limitations.iter().take(8) {
        for (line_index, line) in wrap_lines(limitation, 102).iter().enumerate() {
            let prefix = if line_index == 0 { "- " } else { "  " };
            canvas.text(54.0, cursor, 7.5, false, GREY, &format!("{prefix}{line}"));
            cursor -= 10.0;
        }
        cursor -= 3.0;
        if cursor < 45.0 {
            break;
        }
    }
    canvas.content
}

fn pdf(pages: &[String], title: &str) -> Vec<u8> {
    let info_object = 5 + pages.len() * 2;
    let mut objects = Vec::<String>::new();
    objects.push("<< /Type /Catalog /Pages 2 0 R >>".to_string());
    let kids = (0..pages.len())
        .map(|index| format!("{} 0 R", 5 + index * 2))
        .collect::<Vec<_>>()
        .join(" ");
    objects.push(format!(
        "<< /Type /Pages /Count {} /Kids [{}] >>",
        pages.len(),
        kids
    ));
    objects.push("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>".to_string());
    objects.push("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>".to_string());
    for (index, content) in pages.iter().enumerate() {
        let content_object = 6 + index * 2;
        objects.push(format!(
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {:.0} {:.0}] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {} 0 R >>",
            PAGE_WIDTH, PAGE_HEIGHT, content_object
        ));
        objects.push(format!(
            "<< /Length {} >>\nstream\n{}endstream",
            content.as_bytes().len(),
            content
        ));
    }
    objects.push(format!(
        "<< /Title ({}) /Author (MH370 estimator) /Creator (mh370-reporting) /Producer (mh370-reporting) >>",
        pdf_escape(title)
    ));
    debug_assert_eq!(objects.len(), info_object);

    let mut output = String::from("%PDF-1.4\n%MH370\n");
    let mut offsets = Vec::with_capacity(objects.len());
    for (index, object) in objects.iter().enumerate() {
        offsets.push(output.as_bytes().len());
        let _ = write!(output, "{} 0 obj\n{}\nendobj\n", index + 1, object);
    }
    let xref = output.as_bytes().len();
    let _ = writeln!(output, "xref");
    let _ = writeln!(output, "0 {}", objects.len() + 1);
    let _ = writeln!(output, "0000000000 65535 f ");
    for offset in offsets {
        let _ = writeln!(output, "{offset:010} 00000 n ");
    }
    let _ = writeln!(
        output,
        "trailer\n<< /Size {} /Root 1 0 R /Info {} 0 R >>\nstartxref\n{}\n%%EOF",
        objects.len() + 1,
        info_object,
        xref
    );
    output.into_bytes()
}

pub fn build_pdf(document: &ReportDocument) -> Result<Vec<u8>, ReportError> {
    validate(document)?;
    let grid = grid_with_bounds(
        &document.points,
        None,
        document.map_context.as_ref().map(|context| context.bounds),
    )?;
    let density = smooth_density(&grid);
    Ok(pdf(
        &[
            first_page(document, &grid, &density),
            map_page(document, &grid, &density),
            diagnostic_page(document),
        ],
        &document.title,
    ))
}

pub fn build_posterior_svg(document: &ReportDocument) -> Result<Vec<u8>, ReportError> {
    validate(document)?;
    let grid = grid_with_bounds(
        &document.points,
        None,
        document.map_context.as_ref().map(|context| context.bounds),
    )?;
    let density = smooth_density(&grid);
    let plot_x = 115.0;
    let plot_y = 105.0;
    let plot_width = 1_020.0;
    let plot_height = 630.0;
    let cell_width = plot_width / grid.columns as f64;
    let cell_height = plot_height / grid.rows as f64;
    let mut svg = String::new();
    let _ = writeln!(
        svg,
        "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1200\" height=\"850\" viewBox=\"0 0 1200 850\">"
    );
    let _ = writeln!(svg, "<rect width=\"1200\" height=\"850\" fill=\"white\"/>");
    let _ = writeln!(
        svg,
        "<text x=\"60\" y=\"46\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"25\" font-weight=\"700\" fill=\"#0e1f35\">{}</text>",
        ascii(&document.title)
    );
    let _ = writeln!(
        svg,
        "<g id=\"hpd-density-bands\" aria-label=\"Display-smoothed highest-posterior-density bands\">"
    );
    for row in 0..grid.rows {
        for column in 0..grid.columns {
            let value = density.mass[row * grid.columns + column];
            let Some((color, alpha)) = density_band(value, &density) else {
                continue;
            };
            let [red, green, blue] = preblended_rgb(color, alpha);
            let x = plot_x + column as f64 * cell_width;
            let y = plot_y + (grid.rows - 1 - row) as f64 * cell_height;
            let _ = writeln!(
                svg,
                "<rect x=\"{x:.2}\" y=\"{y:.2}\" width=\"{:.2}\" height=\"{:.2}\" fill=\"rgb({red},{green},{blue})\"/>",
                cell_width + 0.1,
                cell_height + 0.1
            );
        }
    }
    let _ = writeln!(svg, "</g>");
    for index in 0..=4 {
        let fraction = index as f64 / 4.0;
        let x = plot_x + fraction * plot_width;
        let y = plot_y + fraction * plot_height;
        let longitude = grid.longitude_min + fraction * (grid.longitude_max - grid.longitude_min);
        let latitude = grid.latitude_max - fraction * (grid.latitude_max - grid.latitude_min);
        let _ = writeln!(
            svg,
            "<line x1=\"{x:.2}\" y1=\"{plot_y}\" x2=\"{x:.2}\" y2=\"{}\" stroke=\"#cfd6dd\" stroke-width=\"1\"/>",
            plot_y + plot_height
        );
        let _ = writeln!(
            svg,
            "<line x1=\"{plot_x}\" y1=\"{y:.2}\" x2=\"{}\" y2=\"{y:.2}\" stroke=\"#cfd6dd\" stroke-width=\"1\"/>",
            plot_x + plot_width
        );
        let _ = writeln!(
            svg,
            "<text x=\"{:.2}\" y=\"780\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"15\" text-anchor=\"middle\" fill=\"#59636f\">{longitude:.1} E</text>",
            x
        );
        let _ = writeln!(
            svg,
            "<text x=\"100\" y=\"{:.2}\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"15\" text-anchor=\"end\" fill=\"#59636f\">{latitude:.1}</text>",
            y + 5.0
        );
    }
    for (id, label, threshold, color, line_width) in [
        (
            "hpd-99-contour",
            "99% HPD",
            density.threshold_99,
            CONTOUR_99,
            1.3,
        ),
        (
            "hpd-95-contour",
            "95% HPD",
            density.threshold_95,
            CONTOUR_95,
            1.6,
        ),
        (
            "hpd-90-contour",
            "90% HPD",
            density.threshold_90,
            CONTOUR_90,
            2.0,
        ),
        (
            "hpd-50-contour",
            "50% HPD",
            density.threshold_50,
            CONTOUR_50,
            2.6,
        ),
    ] {
        let _ = writeln!(
            svg,
            "<g id=\"{id}\" aria-label=\"{label}\" fill=\"none\" stroke=\"#{:02x}{:02x}{:02x}\" stroke-width=\"{line_width}\"><title>{label}</title>",
            color[0], color[1], color[2]
        );
        for segment in contour_segments(&grid, &density, threshold) {
            let x1 = plot_x + segment.start.0 * plot_width;
            let y1 = plot_y + (1.0 - segment.start.1) * plot_height;
            let x2 = plot_x + segment.end.0 * plot_width;
            let y2 = plot_y + (1.0 - segment.end.1) * plot_height;
            let _ = writeln!(
                svg,
                "<line x1=\"{x1:.2}\" y1=\"{y1:.2}\" x2=\"{x2:.2}\" y2=\"{y2:.2}\"/>"
            );
        }
        let _ = writeln!(svg, "</g>");
    }
    let _ = writeln!(
        svg,
        "<rect x=\"{plot_x}\" y=\"{plot_y}\" width=\"{plot_width}\" height=\"{plot_height}\" fill=\"none\" stroke=\"#0e1f35\" stroke-width=\"2\"/>"
    );
    for (index, (label, color, line_width)) in [
        ("50% HPD", CONTOUR_50, 2.6),
        ("90% HPD", CONTOUR_90, 2.0),
        ("95% HPD", CONTOUR_95, 1.6),
        ("99% HPD", CONTOUR_99, 1.3),
    ]
    .iter()
    .enumerate()
    {
        let x = 230.0 + index as f64 * 235.0;
        let _ = writeln!(
            svg,
            "<line x1=\"{x:.1}\" y1=\"78\" x2=\"{:.1}\" y2=\"78\" stroke=\"#{:02x}{:02x}{:02x}\" stroke-width=\"{line_width}\"/>",
            x + 42.0,
            color[0],
            color[1],
            color[2]
        );
        let _ = writeln!(
            svg,
            "<text x=\"{:.1}\" y=\"83\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"14\" fill=\"#171717\">{label}</text>",
            x + 50.0
        );
    }
    let _ = writeln!(
        svg,
        "<text x=\"600\" y=\"827\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"12\" text-anchor=\"middle\" fill=\"#59636f\">{DISPLAY_KERNEL_NOTICE}</text>"
    );
    let _ = writeln!(svg, "</svg>");
    Ok(svg.into_bytes())
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightArcReport {
    pub label: String,
    pub time_utc: String,
    pub truth_latitude_deg: f64,
    pub truth_longitude_deg: f64,
    pub truth_heading_true_deg: f64,
    pub points: Vec<ReportPoint>,
    pub metrics: Vec<(String, String)>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct KnownFlightControlReport {
    pub title: String,
    pub subtitle: String,
    pub summary: Vec<(String, String)>,
    pub arcs: Vec<KnownFlightArcReport>,
    pub evidence_conditions: Vec<String>,
    pub limitations: Vec<String>,
}

fn validate_known_flight(document: &KnownFlightControlReport) -> Result<(), ReportError> {
    if document.title.trim().is_empty() || document.arcs.is_empty() {
        return Err(ReportError::EmptyReport);
    }
    for arc in &document.arcs {
        if arc.label.trim().is_empty()
            || !arc.truth_latitude_deg.is_finite()
            || !arc.truth_longitude_deg.is_finite()
            || !arc.truth_heading_true_deg.is_finite()
            || !(-90.0..=90.0).contains(&arc.truth_latitude_deg)
        {
            return Err(ReportError::InvalidPosterior);
        }
        validate(&ReportDocument {
            title: arc.label.clone(),
            subtitle: String::new(),
            summary: Vec::new(),
            points: arc.points.clone(),
            diagnostics: Vec::new(),
            evidence_conditions: Vec::new(),
            limitations: Vec::new(),
            map_context: None,
        })?;
    }
    Ok(())
}

fn known_flight_summary_page(document: &KnownFlightControlReport) -> String {
    let mut canvas = Canvas::new();
    canvas.fill_rect(0.0, PAGE_HEIGHT - 126.0, PAGE_WIDTH, 126.0, NAVY);
    canvas.text(42.0, 790.0, 21.0, true, (1.0, 1.0, 1.0), &document.title);
    canvas.text(
        42.0,
        764.0,
        9.0,
        false,
        (0.82, 0.89, 0.95),
        &document.subtitle,
    );
    canvas.text(42.0, 680.0, 13.0, true, NAVY, "Control result");
    let mut y = 651.0;
    for (index, (label, value)) in document.summary.iter().take(10).enumerate() {
        let column = index % 2;
        if index > 0 && column == 0 {
            y -= 43.0;
        }
        let x = 42.0 + 264.0 * column as f64;
        canvas.text(x, y, 7.0, true, GREY, &label.to_uppercase());
        canvas.text(x, y - 16.0, 11.0, false, NAVY, value);
    }

    let mut cursor = 393.0;
    canvas.text(
        42.0,
        cursor,
        11.0,
        true,
        NAVY,
        "Evidence and inference conditions",
    );
    cursor -= 20.0;
    for item in document.evidence_conditions.iter().take(8) {
        for (index, line) in wrap_lines(item, 100).iter().enumerate() {
            canvas.text(
                49.0,
                cursor,
                7.5,
                false,
                GREY,
                &format!("{}{}", if index == 0 { "- " } else { "  " }, line),
            );
            cursor -= 10.0;
        }
        cursor -= 3.0;
    }

    cursor = cursor.min(215.0);
    canvas.text(42.0, cursor, 11.0, true, NAVY, "Material limitations");
    cursor -= 20.0;
    for item in document.limitations.iter().take(6) {
        for (index, line) in wrap_lines(item, 100).iter().enumerate() {
            canvas.text(
                49.0,
                cursor,
                7.5,
                false,
                GREY,
                &format!("{}{}", if index == 0 { "- " } else { "  " }, line),
            );
            cursor -= 10.0;
        }
        cursor -= 3.0;
    }
    canvas.line(42.0, 62.0, 553.0, 62.0, (0.75, 0.79, 0.83), 0.5);
    canvas.text(
        42.0,
        44.0,
        7.5,
        false,
        GREY,
        &format!(
            "The following {} pages show posterior density, held-back position, and true-heading arrow at each selected SATCOM arc.",
            document.arcs.len()
        ),
    );
    canvas.content
}

fn draw_truth(
    canvas: &mut Canvas,
    grid: &Grid,
    x: f64,
    y: f64,
    width: f64,
    height: f64,
    arc: &KnownFlightArcReport,
) {
    let px = x
        + (arc.truth_longitude_deg - grid.longitude_min)
            / (grid.longitude_max - grid.longitude_min)
            * width;
    let py = y
        + (arc.truth_latitude_deg - grid.latitude_min) / (grid.latitude_max - grid.latitude_min)
            * height;
    let red = (0.72, 0.08, 0.10);
    canvas.line(px - 5.0, py, px + 5.0, py, red, 1.8);
    canvas.line(px, py - 5.0, px, py + 5.0, red, 1.8);
    let heading = arc.truth_heading_true_deg.to_radians();
    let length = 31.0;
    let end_x = px + length * heading.sin();
    let end_y = py + length * heading.cos();
    canvas.line(px, py, end_x, end_y, red, 1.8);
    for offset in [-0.48_f64, 0.48] {
        canvas.line(
            end_x,
            end_y,
            end_x - 8.0 * (heading + offset).sin(),
            end_y - 8.0 * (heading + offset).cos(),
            red,
            1.8,
        );
    }
    canvas.text(px + 7.0, py + 7.0, 7.5, true, red, "held-back truth");
}

fn known_flight_arc_page(arc: &KnownFlightArcReport) -> Result<String, ReportError> {
    let grid = grid(
        &arc.points,
        Some((arc.truth_latitude_deg, arc.truth_longitude_deg)),
    )?;
    let density = smooth_density(&grid);
    let mut canvas = Canvas::new();
    canvas.text(48.0, 797.0, 18.0, true, NAVY, &arc.label);
    canvas.text(
        48.0,
        776.0,
        8.5,
        false,
        GREY,
        &format!(
            "{} | truth {:.4} deg, {:.4} deg | true heading {:.1} deg",
            arc.time_utc,
            arc.truth_latitude_deg,
            arc.truth_longitude_deg,
            arc.truth_heading_true_deg
        ),
    );
    draw_map(
        &mut canvas,
        &grid,
        &density,
        (74.0, 254.0, 460.0, 438.0),
        false,
    );
    draw_truth(&mut canvas, &grid, 74.0, 254.0, 460.0, 438.0, arc);

    canvas.text(
        48.0,
        214.0,
        11.0,
        true,
        NAVY,
        "Posterior and control metrics",
    );
    let mut y = 190.0;
    for (index, (label, value)) in arc.metrics.iter().take(10).enumerate() {
        let column = index % 2;
        if index > 0 && column == 0 {
            y -= 31.0;
        }
        let x = 48.0 + column as f64 * 265.0;
        canvas.text(x, y, 6.7, true, GREY, &label.to_uppercase());
        canvas.text(x, y - 13.0, 9.0, false, NAVY, value);
    }
    canvas.text(
        48.0,
        42.0,
        7.2,
        false,
        GREY,
        "Density combines equal-weight deterministic seed replicates. The red cross and arrow were loaded only during scoring.",
    );
    canvas.text(48.0, 29.0, 7.0, false, GREY, DISPLAY_KERNEL_NOTICE);
    Ok(canvas.content)
}

pub fn build_known_flight_pdf(document: &KnownFlightControlReport) -> Result<Vec<u8>, ReportError> {
    validate_known_flight(document)?;
    let mut pages = Vec::with_capacity(document.arcs.len() + 1);
    pages.push(known_flight_summary_page(document));
    for arc in &document.arcs {
        pages.push(known_flight_arc_page(arc)?);
    }
    Ok(pdf(&pages, &document.title))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn document() -> ReportDocument {
        ReportDocument {
            title: "MH370 estimate".to_string(),
            subtitle: "deterministic fixture".to_string(),
            summary: vec![("Particles".to_string(), "4".to_string())],
            points: vec![
                ReportPoint {
                    latitude_deg: -30.0,
                    longitude_deg: 95.0,
                    weight: 0.2,
                },
                ReportPoint {
                    latitude_deg: -31.0,
                    longitude_deg: 96.0,
                    weight: 0.4,
                },
                ReportPoint {
                    latitude_deg: -32.0,
                    longitude_deg: 97.0,
                    weight: 0.3,
                },
                ReportPoint {
                    latitude_deg: -33.0,
                    longitude_deg: 98.0,
                    weight: 0.1,
                },
            ],
            diagnostics: vec![
                DiagnosticPoint {
                    label: "one".to_string(),
                    effective_sample_size: 4.0,
                    log_evidence_increment: -1.0,
                },
                DiagnosticPoint {
                    label: "two".to_string(),
                    effective_sample_size: 3.0,
                    log_evidence_increment: -2.0,
                },
            ],
            evidence_conditions: vec!["SATCOM only".to_string()],
            limitations: vec!["fixture only".to_string()],
            map_context: None,
        }
    }

    #[test]
    fn generated_pdf_has_three_vector_pages_and_xref() {
        let fixture = document();
        let bytes = build_pdf(&fixture).unwrap();
        let text = std::str::from_utf8(&bytes).unwrap();
        assert!(text.starts_with("%PDF-1.4"));
        assert_eq!(text.matches("/Type /Page ").count(), 3);
        for label in ["50% HPD", "90% HPD", "95% HPD", "99% HPD"] {
            assert!(text.contains(label));
        }
        assert!(text.contains(DISPLAY_KERNEL_NOTICE));
        assert!(!text.contains("% HDR"));
        assert!(text.contains("xref"));
        assert!(text.ends_with("%%EOF\n"));
        assert_eq!(bytes, build_pdf(&fixture).unwrap());
    }

    #[test]
    fn generated_svg_is_standalone_vector_output() {
        let fixture = document();
        let bytes = build_posterior_svg(&fixture).unwrap();
        let text = std::str::from_utf8(&bytes).unwrap();
        assert!(text.starts_with("<svg"));
        assert!(text.contains("MH370 estimate"));
        for level in ["50", "90", "95", "99"] {
            assert!(text.contains(&format!("id=\"hpd-{level}-contour\"")));
            assert!(text.contains(&format!(">{level}% HPD</text>")));
        }
        assert!(text.contains(DISPLAY_KERNEL_NOTICE));
        assert!(text.contains("</svg>"));
        assert_eq!(bytes, build_posterior_svg(&fixture).unwrap());
    }

    #[test]
    fn display_density_is_normalized_and_all_hpd_contours_are_finite() {
        let grid = grid(&document().points, None).unwrap();
        let density = smooth_density(&grid);
        assert!((density.mass.iter().sum::<f64>() - 1.0).abs() < 1e-12);
        assert!(density.threshold_50 >= density.threshold_90);
        assert!(density.threshold_90 >= density.threshold_95);
        assert!(density.threshold_95 >= density.threshold_99);

        for (probability, threshold) in [
            (0.50, density.threshold_50),
            (0.90, density.threshold_90),
            (0.95, density.threshold_95),
            (0.99, density.threshold_99),
        ] {
            let enclosed = density
                .mass
                .iter()
                .filter(|value| **value >= threshold)
                .sum::<f64>();
            assert!(enclosed + 1e-12 >= probability);
            let segments = contour_segments(&grid, &density, threshold);
            assert!(!segments.is_empty());
            assert!(segments.iter().all(|segment| {
                [segment.start, segment.end].into_iter().all(|(x, y)| {
                    x.is_finite()
                        && y.is_finite()
                        && (0.0..=1.0).contains(&x)
                        && (0.0..=1.0).contains(&y)
                })
            }));
        }
    }

    #[test]
    fn common_raster_spatial_comparison_has_exact_probability_identities() {
        let first = document().points;
        let identical = compare_spatial_posteriors(&first, &first).unwrap();
        assert!((identical.overlap_coefficient - 1.0).abs() < 1e-12);
        assert!(identical.total_variation_distance.abs() < 1e-12);
        assert!(identical.jensen_shannon_divergence_nats.abs() < 1e-12);
        assert_eq!(identical.first_hpd_area_km2, identical.second_hpd_area_km2);
        assert!(identical.first_hpd_area_km2.mass_50 > 0.0);
        assert!(identical.first_hpd_area_km2.mass_50 <= identical.first_hpd_area_km2.mass_90);
        assert!(identical.first_hpd_area_km2.mass_90 <= identical.first_hpd_area_km2.mass_95);
        assert!(identical.first_hpd_area_km2.mass_95 <= identical.first_hpd_area_km2.mass_99);

        let shifted = first
            .iter()
            .map(|point| ReportPoint {
                longitude_deg: point.longitude_deg + 20.0,
                ..*point
            })
            .collect::<Vec<_>>();
        let separated = compare_spatial_posteriors(&first, &shifted).unwrap();
        assert!(separated.overlap_coefficient < 0.01);
        assert!(separated.total_variation_distance > 0.99);
        assert!(separated.jensen_shannon_divergence_nats > 0.68);
        assert!(
            (separated.overlap_coefficient + separated.total_variation_distance - 1.0).abs()
                < 1e-12
        );
    }

    #[test]
    fn requested_bounds_are_shared_by_pdf_and_svg() {
        let mut fixture = document();
        fixture.map_context = Some(ReportMapContext {
            bounds: ReportMapBounds {
                longitude_min_deg: 90.0,
                longitude_max_deg: 110.0,
                latitude_min_deg: -40.0,
                latitude_max_deg: -20.0,
            },
            references: Vec::new(),
            routes: Vec::new(),
        });
        let pdf = String::from_utf8(build_pdf(&fixture).unwrap()).unwrap();
        let svg = String::from_utf8(build_posterior_svg(&fixture).unwrap()).unwrap();
        for label in ["90.0 E", "110.0 E"] {
            assert!(pdf.contains(label));
            assert!(svg.contains(label));
        }
    }

    #[test]
    fn plot_bounds_expand_before_binning_outlying_positive_mass() {
        let points = vec![
            ReportPoint {
                latitude_deg: -31.0,
                longitude_deg: 96.0,
                weight: 0.8,
            },
            ReportPoint {
                latitude_deg: -35.0,
                longitude_deg: 101.0,
                weight: 0.2,
            },
        ];
        let grid = grid_with_bounds(
            &points,
            None,
            Some(ReportMapBounds {
                longitude_min_deg: 95.0,
                longitude_max_deg: 98.0,
                latitude_min_deg: -34.0,
                latitude_max_deg: -30.0,
            }),
        )
        .unwrap();
        assert!(grid.longitude_max > 101.0);
        assert!(grid.latitude_min < -35.0);
        assert!((grid.mass.iter().sum::<f64>() - 1.0).abs() < 1e-12);
        let edge_mass = (0..grid.rows)
            .flat_map(|row| {
                [
                    grid.mass[row * grid.columns],
                    grid.mass[row * grid.columns + grid.columns - 1],
                ]
            })
            .chain((0..grid.columns).flat_map(|column| {
                [
                    grid.mass[column],
                    grid.mass[(grid.rows - 1) * grid.columns + column],
                ]
            }))
            .sum::<f64>();
        assert_eq!(edge_mass, 0.0);
    }

    #[test]
    fn publication_density_bands_use_the_lighter_opacities() {
        let density = DensitySurface {
            mass: Vec::new(),
            threshold_50: 0.4,
            threshold_90: 0.3,
            threshold_95: 0.2,
            threshold_99: 0.1,
        };
        assert_eq!(density_band(0.5, &density), Some((HPD_50, 84)));
        assert_eq!(density_band(0.35, &density), Some((HPD_90, 62)));
        assert_eq!(density_band(0.25, &density), Some((HPD_95, 44)));
        assert_eq!(density_band(0.15, &density), Some((HPD_99, 28)));
        assert_eq!(density_band(0.05, &density), None);
    }

    #[test]
    fn long_pdf_header_wraps_without_dropping_words() {
        let mut fixture = document();
        fixture.title =
            "MH370 flaperon drift diagnostic - CMEMS GLORYS12V1 daily 1/12-degree currents"
                .to_string();
        fixture.subtitle = "Uncalibrated family-specific diagnostic; currents=cmems_glorys12_reanalysis | isotope=enabled conditional on represented Reunion arrival".to_string();

        let bytes = build_pdf(&fixture).unwrap();
        let text = std::str::from_utf8(&bytes).unwrap();

        assert!(text.contains("MH370 flaperon drift diagnostic - CMEMS"));
        assert!(text.contains("GLORYS12V1 daily 1/12-degree currents"));
        assert!(text.contains("represented Reunion arrival"));
        assert!(!text.contains("22.000 Tf (MH370 flaperon drift diagnostic"));
    }

    #[test]
    fn pdf_ascii_transliteration_preserves_scientific_symbols() {
        assert_eq!(
            ascii("8192 × 77; 0.20‰; 100 m²/s; ±1°"),
            "8192 x 77; 0.20 per mil; 100 m^2/s; +/-1 deg "
        );
    }
}
