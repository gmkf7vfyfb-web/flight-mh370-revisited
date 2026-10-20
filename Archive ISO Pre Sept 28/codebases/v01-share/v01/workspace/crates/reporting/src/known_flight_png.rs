use std::io::Cursor;

use fontdue::{Font, FontSettings};
use serde_json::Value;

use super::{
    contour_segments, density_band, density_sample, grid, grid_with_bounds, smooth_density,
    validate, validate_known_flight, DensitySurface, Grid, KnownFlightArcReport,
    KnownFlightControlReport, ReportDocument, ReportError, ReportMapContext, ReportMapReference,
    CONTOUR_50, CONTOUR_90, CONTOUR_95, CONTOUR_99, DISPLAY_KERNEL_NOTICE,
};

const IMAGE_WIDTH: usize = 2_800;
const IMAGE_HEIGHT: usize = 1_900;
const LAND_GEOJSON: &str = include_str!("../assets/ne_110m_land.geojson");
const REGULAR_FONT: &[u8] = include_bytes!("../assets/DejaVuSans.ttf");
const BOLD_FONT: &[u8] = include_bytes!("../assets/DejaVuSans-Bold.ttf");

const WHITE: [u8; 3] = [255, 255, 255];
const BLACK: [u8; 3] = [23, 23, 23];
const RED: [u8; 3] = [214, 39, 40];
const TRUTH_YELLOW: [u8; 3] = [255, 223, 0];
const MAP_CYAN: [u8; 3] = [0, 213, 255];
const GREY: [u8; 3] = [82, 82, 82];
const GRID_GREY: [u8; 3] = [222, 225, 228];
const COAST_GREY: [u8; 3] = [109, 106, 100];
const LAND: [u8; 3] = [246, 245, 242];
const OCEAN: [u8; 3] = [250, 252, 253];
const AIRWAY_BLUE: [u8; 3] = [52, 102, 164];
const CANDIDATE_BLUE: [u8; 3] = [188, 201, 217];
const ARC_GREY: [u8; 3] = [65, 65, 65];

#[derive(Clone, Copy)]
struct GeoPoint {
    longitude: f64,
    latitude: f64,
}

struct Fonts {
    regular: Font,
    bold: Font,
}

impl Fonts {
    fn new() -> Result<Self, ReportError> {
        Ok(Self {
            regular: Font::from_bytes(REGULAR_FONT, FontSettings::default())
                .map_err(|_| ReportError::InvalidReportFont)?,
            bold: Font::from_bytes(BOLD_FONT, FontSettings::default())
                .map_err(|_| ReportError::InvalidReportFont)?,
        })
    }

    fn face(&self, bold: bool) -> &Font {
        if bold {
            &self.bold
        } else {
            &self.regular
        }
    }
}

struct TextMask {
    width: usize,
    height: usize,
    alpha: Vec<u8>,
}

fn text_mask(font: &Font, value: &str, size_px: f32) -> TextMask {
    let baseline = (size_px * 1.08).ceil() as i32 + 4;
    let height = (size_px * 1.42).ceil() as usize + 8;
    let mut pen_x = 4.0_f32;
    let mut glyphs = Vec::new();
    for character in value.chars() {
        let (metrics, bitmap) = font.rasterize(character, size_px);
        glyphs.push((pen_x, metrics, bitmap));
        pen_x += metrics.advance_width;
    }
    let width = pen_x.ceil().max(1.0) as usize + 4;
    let mut alpha = vec![0_u8; width * height];
    for (pen, metrics, bitmap) in glyphs {
        let glyph_x = pen.round() as i32 + metrics.xmin;
        let glyph_y = baseline - metrics.height as i32 - metrics.ymin;
        for row in 0..metrics.height {
            for column in 0..metrics.width {
                let x = glyph_x + column as i32;
                let y = glyph_y + row as i32;
                if x >= 0 && y >= 0 && x < width as i32 && y < height as i32 {
                    let target = y as usize * width + x as usize;
                    alpha[target] = alpha[target].max(bitmap[row * metrics.width + column]);
                }
            }
        }
    }
    TextMask {
        width,
        height,
        alpha,
    }
}

fn fitted_text_mask(
    font: &Font,
    value: &str,
    preferred_size_px: f32,
    minimum_size_px: f32,
    maximum_width: usize,
) -> (TextMask, f32) {
    let mut size_px = preferred_size_px;
    loop {
        let mask = text_mask(font, value, size_px);
        if mask.width <= maximum_width {
            return (mask, size_px);
        }
        if size_px <= minimum_size_px {
            break;
        }
        size_px = (size_px - 1.0).max(minimum_size_px);
    }

    let characters = value.chars().collect::<Vec<_>>();
    for count in (0..characters.len()).rev() {
        let mut candidate = characters[..count].iter().collect::<String>();
        candidate.push('…');
        let mask = text_mask(font, &candidate, minimum_size_px);
        if mask.width <= maximum_width {
            return (mask, minimum_size_px);
        }
    }
    (text_mask(font, "", minimum_size_px), minimum_size_px)
}

struct Raster {
    width: usize,
    height: usize,
    pixels: Vec<u8>,
    clip: Option<(i32, i32, i32, i32)>,
}

impl Raster {
    fn new(width: usize, height: usize, color: [u8; 3]) -> Self {
        let mut pixels = vec![0; width * height * 3];
        for pixel in pixels.chunks_exact_mut(3) {
            pixel.copy_from_slice(&color);
        }
        Self {
            width,
            height,
            pixels,
            clip: None,
        }
    }

    fn blend_pixel(&mut self, x: i32, y: i32, color: [u8; 3], alpha: u8) {
        if x < 0 || y < 0 || x >= self.width as i32 || y >= self.height as i32 {
            return;
        }
        if let Some((left, top, right, bottom)) = self.clip {
            if x < left || x >= right || y < top || y >= bottom {
                return;
            }
        }
        let index = (y as usize * self.width + x as usize) * 3;
        let alpha = alpha as u16;
        for (channel, value) in color.iter().enumerate() {
            let old = self.pixels[index + channel] as u16;
            self.pixels[index + channel] =
                ((old * (255 - alpha) + *value as u16 * alpha + 127) / 255) as u8;
        }
    }

    fn fill_rect(&mut self, x: i32, y: i32, width: i32, height: i32, color: [u8; 3]) {
        let left = x.max(0);
        let top = y.max(0);
        let right = (x + width).min(self.width as i32);
        let bottom = (y + height).min(self.height as i32);
        for row in top..bottom {
            for column in left..right {
                self.blend_pixel(column, row, color, 255);
            }
        }
    }

    fn stroke_rect(
        &mut self,
        x: i32,
        y: i32,
        width: i32,
        height: i32,
        color: [u8; 3],
        thickness: i32,
    ) {
        self.fill_rect(x, y, width, thickness, color);
        self.fill_rect(x, y + height - thickness, width, thickness, color);
        self.fill_rect(x, y, thickness, height, color);
        self.fill_rect(x + width - thickness, y, thickness, height, color);
    }

    fn line(&mut self, x1: f64, y1: f64, x2: f64, y2: f64, color: [u8; 3], thickness: i32) {
        self.line_alpha(x1, y1, x2, y2, color, thickness, 255);
    }

    #[allow(clippy::too_many_arguments)]
    fn line_alpha(
        &mut self,
        x1: f64,
        y1: f64,
        x2: f64,
        y2: f64,
        color: [u8; 3],
        thickness: i32,
        alpha: u8,
    ) {
        let dx = x2 - x1;
        let dy = y2 - y1;
        let steps = dx.abs().max(dy.abs()).ceil().max(1.0) as usize;
        let radius = (thickness.max(1) - 1) / 2;
        for index in 0..=steps {
            let fraction = index as f64 / steps as f64;
            let x = (x1 + fraction * dx).round() as i32;
            let y = (y1 + fraction * dy).round() as i32;
            for oy in -radius..=radius {
                for ox in -radius..=radius {
                    if ox * ox + oy * oy <= radius * radius + 1 {
                        self.blend_pixel(x + ox, y + oy, color, alpha);
                    }
                }
            }
        }
    }

    fn begin_clip(&mut self, rect: (i32, i32, i32, i32)) -> Option<(i32, i32, i32, i32)> {
        let previous = self.clip;
        let (x, y, width, height) = rect;
        let requested = (x, y, x + width, y + height);
        self.clip = Some(if let Some((left, top, right, bottom)) = previous {
            (
                left.max(requested.0),
                top.max(requested.1),
                right.min(requested.2),
                bottom.min(requested.3),
            )
        } else {
            requested
        });
        previous
    }

    fn restore_clip(&mut self, previous: Option<(i32, i32, i32, i32)>) {
        self.clip = previous;
    }

    fn fill_polygon(&mut self, points: &[(f64, f64)], color: [u8; 3]) {
        if points.len() < 3 {
            return;
        }
        let minimum_y = points
            .iter()
            .map(|point| point.1)
            .fold(f64::INFINITY, f64::min)
            .floor()
            .max(0.0) as i32;
        let maximum_y = points
            .iter()
            .map(|point| point.1)
            .fold(f64::NEG_INFINITY, f64::max)
            .ceil()
            .min((self.height - 1) as f64) as i32;
        for y in minimum_y..=maximum_y {
            let scan_y = y as f64 + 0.5;
            let mut intersections = Vec::new();
            for index in 0..points.len() {
                let first = points[index];
                let second = points[(index + 1) % points.len()];
                if (first.1 > scan_y) != (second.1 > scan_y) {
                    let fraction = (scan_y - first.1) / (second.1 - first.1);
                    intersections.push(first.0 + fraction * (second.0 - first.0));
                }
            }
            intersections.sort_by(f64::total_cmp);
            for pair in intersections.chunks_exact(2) {
                let left = pair[0].ceil().max(0.0) as i32;
                let right = pair[1].floor().min((self.width - 1) as f64) as i32;
                for x in left..=right {
                    self.blend_pixel(x, y, color, 255);
                }
            }
        }
    }

    fn draw_text_mask(&mut self, x: i32, y: i32, color: [u8; 3], mask: &TextMask) {
        for row in 0..mask.height {
            for column in 0..mask.width {
                let alpha = mask.alpha[row * mask.width + column];
                if alpha > 0 {
                    self.blend_pixel(x + column as i32, y + row as i32, color, alpha);
                }
            }
        }
    }

    fn text(
        &mut self,
        fonts: &Fonts,
        x: i32,
        y: i32,
        size_px: f32,
        bold: bool,
        color: [u8; 3],
        value: &str,
    ) -> i32 {
        let mask = text_mask(fonts.face(bold), value, size_px);
        self.draw_text_mask(x, y, color, &mask);
        mask.width as i32
    }

    fn text_centered(
        &mut self,
        fonts: &Fonts,
        centre_x: i32,
        y: i32,
        size_px: f32,
        bold: bool,
        color: [u8; 3],
        value: &str,
    ) {
        let mask = text_mask(fonts.face(bold), value, size_px);
        self.draw_text_mask(centre_x - mask.width as i32 / 2, y, color, &mask);
    }

    #[allow(clippy::too_many_arguments)]
    fn text_centered_fitted(
        &mut self,
        fonts: &Fonts,
        centre_x: i32,
        y: i32,
        preferred_size_px: f32,
        minimum_size_px: f32,
        maximum_width: usize,
        bold: bool,
        color: [u8; 3],
        value: &str,
    ) {
        let (mask, _) = fitted_text_mask(
            fonts.face(bold),
            value,
            preferred_size_px,
            minimum_size_px,
            maximum_width,
        );
        self.draw_text_mask(centre_x - mask.width as i32 / 2, y, color, &mask);
    }

    fn text_right(
        &mut self,
        fonts: &Fonts,
        right_x: i32,
        y: i32,
        size_px: f32,
        bold: bool,
        color: [u8; 3],
        value: &str,
    ) {
        let mask = text_mask(fonts.face(bold), value, size_px);
        self.draw_text_mask(right_x - mask.width as i32, y, color, &mask);
    }

    fn text_rotated_ccw(
        &mut self,
        fonts: &Fonts,
        x: i32,
        y: i32,
        size_px: f32,
        bold: bool,
        color: [u8; 3],
        value: &str,
    ) {
        let mask = text_mask(fonts.face(bold), value, size_px);
        for row in 0..mask.height {
            for column in 0..mask.width {
                let alpha = mask.alpha[row * mask.width + column];
                if alpha > 0 {
                    self.blend_pixel(
                        x + row as i32,
                        y + mask.width as i32 - 1 - column as i32,
                        color,
                        alpha,
                    );
                }
            }
        }
    }
}
fn ring(value: &Value) -> Result<Vec<GeoPoint>, ReportError> {
    value
        .as_array()
        .ok_or(ReportError::InvalidMapBackground)?
        .iter()
        .map(|coordinate| {
            let coordinate = coordinate
                .as_array()
                .ok_or(ReportError::InvalidMapBackground)?;
            Ok(GeoPoint {
                longitude: coordinate
                    .first()
                    .and_then(Value::as_f64)
                    .ok_or(ReportError::InvalidMapBackground)?,
                latitude: coordinate
                    .get(1)
                    .and_then(Value::as_f64)
                    .ok_or(ReportError::InvalidMapBackground)?,
            })
        })
        .collect()
}

fn land_polygons() -> Result<Vec<Vec<GeoPoint>>, ReportError> {
    let root: Value =
        serde_json::from_str(LAND_GEOJSON).map_err(|_| ReportError::InvalidMapBackground)?;
    let features = root
        .get("features")
        .and_then(Value::as_array)
        .ok_or(ReportError::InvalidMapBackground)?;
    let mut polygons = Vec::new();
    for feature in features {
        let geometry = feature
            .get("geometry")
            .ok_or(ReportError::InvalidMapBackground)?;
        let geometry_type = geometry
            .get("type")
            .and_then(Value::as_str)
            .ok_or(ReportError::InvalidMapBackground)?;
        let coordinates = geometry
            .get("coordinates")
            .and_then(Value::as_array)
            .ok_or(ReportError::InvalidMapBackground)?;
        match geometry_type {
            "Polygon" => {
                if let Some(outer) = coordinates.first() {
                    polygons.push(ring(outer)?);
                }
            }
            "MultiPolygon" => {
                for polygon in coordinates {
                    let outer = polygon
                        .as_array()
                        .and_then(|rings| rings.first())
                        .ok_or(ReportError::InvalidMapBackground)?;
                    polygons.push(ring(outer)?);
                }
            }
            _ => return Err(ReportError::InvalidMapBackground),
        }
    }
    Ok(polygons)
}

#[derive(Clone, Copy)]
enum ClipEdge {
    LongitudeMinimum(f64),
    LongitudeMaximum(f64),
    LatitudeMinimum(f64),
    LatitudeMaximum(f64),
}

fn inside(point: GeoPoint, edge: ClipEdge) -> bool {
    match edge {
        ClipEdge::LongitudeMinimum(value) => point.longitude >= value,
        ClipEdge::LongitudeMaximum(value) => point.longitude <= value,
        ClipEdge::LatitudeMinimum(value) => point.latitude >= value,
        ClipEdge::LatitudeMaximum(value) => point.latitude <= value,
    }
}

fn intersection(first: GeoPoint, second: GeoPoint, edge: ClipEdge) -> GeoPoint {
    match edge {
        ClipEdge::LongitudeMinimum(value) | ClipEdge::LongitudeMaximum(value) => {
            let fraction = if (second.longitude - first.longitude).abs() < 1e-12 {
                0.0
            } else {
                (value - first.longitude) / (second.longitude - first.longitude)
            };
            GeoPoint {
                longitude: value,
                latitude: first.latitude + fraction * (second.latitude - first.latitude),
            }
        }
        ClipEdge::LatitudeMinimum(value) | ClipEdge::LatitudeMaximum(value) => {
            let fraction = if (second.latitude - first.latitude).abs() < 1e-12 {
                0.0
            } else {
                (value - first.latitude) / (second.latitude - first.latitude)
            };
            GeoPoint {
                longitude: first.longitude + fraction * (second.longitude - first.longitude),
                latitude: value,
            }
        }
    }
}

fn clip_polygon(mut polygon: Vec<GeoPoint>, grid: &Grid) -> Vec<GeoPoint> {
    for edge in [
        ClipEdge::LongitudeMinimum(grid.longitude_min),
        ClipEdge::LongitudeMaximum(grid.longitude_max),
        ClipEdge::LatitudeMinimum(grid.latitude_min),
        ClipEdge::LatitudeMaximum(grid.latitude_max),
    ] {
        if polygon.is_empty() {
            break;
        }
        let input = polygon;
        polygon = Vec::new();
        let mut previous = *input.last().expect("non-empty polygon");
        for current in input {
            let previous_inside = inside(previous, edge);
            let current_inside = inside(current, edge);
            if current_inside {
                if !previous_inside {
                    polygon.push(intersection(previous, current, edge));
                }
                polygon.push(current);
            } else if previous_inside {
                polygon.push(intersection(previous, current, edge));
            }
            previous = current;
        }
    }
    polygon
}

fn project(point: GeoPoint, grid: &Grid, rect: (i32, i32, i32, i32)) -> (f64, f64) {
    let (x, y, width, height) = rect;
    (
        x as f64
            + (point.longitude - grid.longitude_min) / (grid.longitude_max - grid.longitude_min)
                * width as f64,
        y as f64
            + (grid.latitude_max - point.latitude) / (grid.latitude_max - grid.latitude_min)
                * height as f64,
    )
}

fn draw_background(
    raster: &mut Raster,
    grid: &Grid,
    rect: (i32, i32, i32, i32),
    polygons: &[Vec<GeoPoint>],
) {
    let (x, y, width, height) = rect;
    raster.fill_rect(x, y, width, height, OCEAN);
    for polygon in polygons {
        let latitude_min = polygon
            .iter()
            .map(|point| point.latitude)
            .fold(f64::INFINITY, f64::min);
        let latitude_max = polygon
            .iter()
            .map(|point| point.latitude)
            .fold(f64::NEG_INFINITY, f64::max);
        let longitude_min = polygon
            .iter()
            .map(|point| point.longitude)
            .fold(f64::INFINITY, f64::min);
        let longitude_max = polygon
            .iter()
            .map(|point| point.longitude)
            .fold(f64::NEG_INFINITY, f64::max);
        if latitude_max < grid.latitude_min
            || latitude_min > grid.latitude_max
            || longitude_max < grid.longitude_min
            || longitude_min > grid.longitude_max
        {
            continue;
        }
        let clipped = clip_polygon(polygon.clone(), grid);
        let screen = clipped
            .iter()
            .map(|point| project(*point, grid, rect))
            .collect::<Vec<_>>();
        raster.fill_polygon(&screen, LAND);
    }

    for index in 0..=4 {
        let fraction = index as f64 / 4.0;
        let px = x as f64 + fraction * width as f64;
        let py = y as f64 + fraction * height as f64;
        raster.line(px, y as f64, px, (y + height) as f64, GRID_GREY, 1);
        raster.line(x as f64, py, (x + width) as f64, py, GRID_GREY, 1);
    }
}

fn draw_density(
    raster: &mut Raster,
    grid: &Grid,
    density: &DensitySurface,
    rect: (i32, i32, i32, i32),
) {
    let (x, y, width, height) = rect;
    for row in 0..height {
        let latitude_fraction = 1.0 - (row as f64 + 0.5) / height as f64;
        for column in 0..width {
            let longitude_fraction = (column as f64 + 0.5) / width as f64;
            let value = density_sample(density, grid, longitude_fraction, latitude_fraction);
            if let Some((color, alpha)) = density_band(value, density) {
                raster.blend_pixel(x + column, y + row, color, alpha);
            }
        }
    }
}

fn draw_contour(
    raster: &mut Raster,
    grid: &Grid,
    density: &DensitySurface,
    rect: (i32, i32, i32, i32),
    threshold: f64,
    color: [u8; 3],
    thickness: i32,
) {
    let (x, y, width, height) = rect;
    for segment in contour_segments(grid, density, threshold) {
        raster.line(
            x as f64 + segment.start.0 * width as f64,
            y as f64 + (1.0 - segment.start.1) * height as f64,
            x as f64 + segment.end.0 * width as f64,
            y as f64 + (1.0 - segment.end.1) * height as f64,
            color,
            thickness,
        );
    }
}

fn draw_coastlines(
    raster: &mut Raster,
    grid: &Grid,
    rect: (i32, i32, i32, i32),
    polygons: &[Vec<GeoPoint>],
) {
    for polygon in polygons {
        let clipped = clip_polygon(polygon.clone(), grid);
        if clipped.len() < 2 {
            continue;
        }
        for pair in clipped.windows(2) {
            let first = project(pair[0], grid, rect);
            let second = project(pair[1], grid, rect);
            raster.line(first.0, first.1, second.0, second.1, COAST_GREY, 1);
        }
    }
}

fn coordinate_label(value: f64, latitude: bool) -> String {
    let direction = if latitude {
        if value < 0.0 {
            'S'
        } else {
            'N'
        }
    } else if value < 0.0 {
        'W'
    } else {
        'E'
    };
    format!("{:.1}°{direction}", value.abs())
}

fn draw_axes(raster: &mut Raster, fonts: &Fonts, grid: &Grid, rect: (i32, i32, i32, i32)) {
    let (x, y, width, height) = rect;
    for index in 0..=4 {
        let fraction = index as f64 / 4.0;
        let longitude = grid.longitude_min + fraction * (grid.longitude_max - grid.longitude_min);
        let latitude = grid.latitude_max - fraction * (grid.latitude_max - grid.latitude_min);
        raster.text_centered(
            fonts,
            x + (fraction * width as f64) as i32,
            y + height + 8,
            16.0,
            false,
            GREY,
            &coordinate_label(longitude, false),
        );
        raster.text_right(
            fonts,
            x - 8,
            y - 10 + (fraction * height as f64) as i32,
            16.0,
            false,
            GREY,
            &coordinate_label(latitude, true),
        );
    }
    raster.text_centered(
        fonts,
        x + width / 2,
        y + height + 34,
        18.0,
        false,
        BLACK,
        "Longitude (°E)",
    );
    raster.text_rotated_ccw(
        fonts,
        x - 108,
        y + height / 2 - 65,
        18.0,
        false,
        BLACK,
        "Latitude",
    );
    raster.stroke_rect(x, y, width, height, BLACK, 2);
}

fn nice_scale_nm(target: f64) -> f64 {
    [
        10.0, 20.0, 50.0, 100.0, 200.0, 500.0, 1_000.0, 2_000.0, 5_000.0,
    ]
    .into_iter()
    .filter(|value| *value <= target)
    .last()
    .unwrap_or(10.0)
}

fn draw_scale_bar(raster: &mut Raster, fonts: &Fonts, grid: &Grid, rect: (i32, i32, i32, i32)) {
    let (x, y, width, height) = rect;
    let midpoint_latitude = 0.5 * (grid.latitude_min + grid.latitude_max);
    let map_width_nm = (grid.longitude_max - grid.longitude_min)
        * 60.0
        * midpoint_latitude.to_radians().cos().abs().max(0.05);
    let scale_nm = nice_scale_nm(map_width_nm * 0.24);
    let scale_width = (scale_nm / map_width_nm * width as f64).round() as i32;
    let left = x + 18;
    let baseline = y + height - 22;
    raster.fill_rect(left - 8, baseline - 31, scale_width + 16, 47, WHITE);
    raster.line(
        left as f64,
        baseline as f64,
        (left + scale_width) as f64,
        baseline as f64,
        BLACK,
        4,
    );
    raster.line(
        left as f64,
        (baseline - 6) as f64,
        left as f64,
        (baseline + 6) as f64,
        BLACK,
        3,
    );
    raster.line(
        (left + scale_width) as f64,
        (baseline - 6) as f64,
        (left + scale_width) as f64,
        (baseline + 6) as f64,
        BLACK,
        3,
    );
    raster.text(
        fonts,
        left,
        baseline - 31,
        15.0,
        false,
        BLACK,
        &format!("{scale_nm:.0} NM"),
    );
}

fn star_points(x: f64, y: f64, outer_radius: f64, inner_radius: f64) -> Vec<(f64, f64)> {
    (0..10)
        .map(|index| {
            let radius = if index % 2 == 0 {
                outer_radius
            } else {
                inner_radius
            };
            let angle = -std::f64::consts::FRAC_PI_2 + index as f64 * std::f64::consts::PI / 5.0;
            (x + radius * angle.cos(), y + radius * angle.sin())
        })
        .collect()
}

fn draw_star_marker(raster: &mut Raster, x: f64, y: f64, radius: f64) {
    let points = star_points(x, y, radius, radius * 0.43);
    raster.fill_polygon(&points, TRUTH_YELLOW);
    for index in 0..points.len() {
        let first = points[index];
        let second = points[(index + 1) % points.len()];
        raster.line(first.0, first.1, second.0, second.1, BLACK, 3);
    }
}

fn draw_x_marker(raster: &mut Raster, x: f64, y: f64, radius: f64) {
    for (color, thickness) in [(BLACK, 7), (MAP_CYAN, 4)] {
        raster.line(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            color,
            thickness,
        );
        raster.line(
            x - radius,
            y + radius,
            x + radius,
            y - radius,
            color,
            thickness,
        );
    }
}

fn draw_spatial_mode(
    raster: &mut Raster,
    grid: &Grid,
    density: &DensitySurface,
    rect: (i32, i32, i32, i32),
) {
    let index = density
        .mass
        .iter()
        .enumerate()
        .max_by(|first, second| first.1.total_cmp(second.1))
        .map(|item| item.0)
        .unwrap_or(0);
    let column = index % grid.columns;
    let row = index / grid.columns;
    let point = GeoPoint {
        longitude: grid.longitude_min
            + column as f64 / (grid.columns - 1) as f64 * (grid.longitude_max - grid.longitude_min),
        latitude: grid.latitude_min
            + row as f64 / (grid.rows - 1) as f64 * (grid.latitude_max - grid.latitude_min),
    };
    let mode = project(point, grid, rect);
    draw_x_marker(raster, mode.0, mode.1, 9.0);
}

fn draw_truth(
    raster: &mut Raster,
    grid: &Grid,
    rect: (i32, i32, i32, i32),
    arc: &KnownFlightArcReport,
) {
    let truth = project(
        GeoPoint {
            longitude: arc.truth_longitude_deg,
            latitude: arc.truth_latitude_deg,
        },
        grid,
        rect,
    );
    let heading = arc.truth_heading_true_deg.to_radians();
    let length = 62.0;
    let end = (
        truth.0 + length * heading.sin(),
        truth.1 - length * heading.cos(),
    );
    raster.line(truth.0, truth.1, end.0, end.1, RED, 5);
    for offset in [-0.50_f64, 0.50] {
        raster.line(
            end.0,
            end.1,
            end.0 - 13.0 * (heading + offset).sin(),
            end.1 + 13.0 * (heading + offset).cos(),
            RED,
            5,
        );
    }
    draw_star_marker(raster, truth.0, truth.1, 13.0);
}

fn draw_reference(
    raster: &mut Raster,
    fonts: &Fonts,
    grid: &Grid,
    rect: (i32, i32, i32, i32),
    reference: &ReportMapReference,
) {
    let point = project(
        GeoPoint {
            longitude: reference.longitude_deg,
            latitude: reference.latitude_deg,
        },
        grid,
        rect,
    );
    draw_star_marker(raster, point.0, point.1, 13.0);
    if let Some(heading_deg) = reference.heading_true_deg {
        let heading = heading_deg.to_radians();
        let length = 82.0;
        let end = (
            point.0 + length * heading.sin(),
            point.1 - length * heading.cos(),
        );
        raster.line(point.0, point.1, end.0, end.1, RED, 5);
        for offset in [-0.50_f64, 0.50] {
            raster.line(
                end.0,
                end.1,
                end.0 - 13.0 * (heading + offset).sin(),
                end.1 + 13.0 * (heading + offset).cos(),
                RED,
                5,
            );
        }
    }
    raster.text(
        fonts,
        point.0.round() as i32 + 18,
        point.1.round() as i32 - 28,
        17.0,
        true,
        BLACK,
        &truncate(&reference.label, 46),
    );
}

fn draw_map_context(
    raster: &mut Raster,
    fonts: &Fonts,
    grid: &Grid,
    rect: (i32, i32, i32, i32),
    context: &ReportMapContext,
) {
    let previous_clip = raster.begin_clip(rect);
    for route in &context.routes {
        for pair in route.coordinates_deg.windows(2) {
            let first = project(
                GeoPoint {
                    latitude: pair[0][0],
                    longitude: pair[0][1],
                },
                grid,
                rect,
            );
            let second = project(
                GeoPoint {
                    latitude: pair[1][0],
                    longitude: pair[1][1],
                },
                grid,
                rect,
            );
            match route.style.as_str() {
                "candidate" => {
                    raster.line_alpha(first.0, first.1, second.0, second.1, CANDIDATE_BLUE, 1, 140)
                }
                "arc" => {
                    raster.line(first.0, first.1, second.0, second.1, WHITE, 6);
                    raster.line(first.0, first.1, second.0, second.1, ARC_GREY, 3);
                }
                _ => {
                    raster.line(first.0, first.1, second.0, second.1, WHITE, 7);
                    raster.line(first.0, first.1, second.0, second.1, AIRWAY_BLUE, 4);
                }
            }
        }
        if !route.label.is_empty() {
            if let Some(coordinate) = route.coordinates_deg.get(route.coordinates_deg.len() / 2) {
                let label = project(
                    GeoPoint {
                        latitude: coordinate[0],
                        longitude: coordinate[1],
                    },
                    grid,
                    rect,
                );
                raster.text(
                    fonts,
                    label.0.round() as i32 + 10,
                    label.1.round() as i32 + 8,
                    18.0,
                    true,
                    AIRWAY_BLUE,
                    &route.label,
                );
            }
        }
    }
    for reference in &context.references {
        draw_reference(raster, fonts, grid, rect, reference);
    }
    raster.restore_clip(previous_clip);
}

fn truncate(value: &str, maximum: usize) -> String {
    let mut output = value.chars().take(maximum).collect::<String>();
    if value.chars().count() > maximum {
        output.pop();
        output.push('…');
    }
    output
}

fn draw_panel(
    raster: &mut Raster,
    fonts: &Fonts,
    arc: &KnownFlightArcReport,
    index: usize,
    panel: (i32, i32, i32, i32),
    polygons: &[Vec<GeoPoint>],
) -> Result<(), ReportError> {
    let grid = grid(
        &arc.points,
        Some((arc.truth_latitude_deg, arc.truth_longitude_deg)),
    )?;
    let density = smooth_density(&grid);
    let (panel_x, panel_y, panel_width, panel_height) = panel;
    raster.fill_rect(panel_x, panel_y, panel_width, panel_height, WHITE);
    let time = arc
        .time_utc
        .split('T')
        .nth(1)
        .and_then(|value| value.get(..5))
        .unwrap_or(arc.time_utc.as_str());
    raster.text_centered(
        fonts,
        panel_x + panel_width / 2,
        panel_y + 3,
        22.0,
        true,
        BLACK,
        &format!("{}. MH371 {time} UTC", index + 1),
    );
    let map = (
        panel_x + 110,
        panel_y + 52,
        panel_width - 128,
        panel_height - 154,
    );
    draw_background(raster, &grid, map, polygons);
    draw_density(raster, &grid, &density, map);
    draw_contour(
        raster,
        &grid,
        &density,
        map,
        density.threshold_99,
        CONTOUR_99,
        1,
    );
    draw_contour(
        raster,
        &grid,
        &density,
        map,
        density.threshold_95,
        CONTOUR_95,
        2,
    );
    draw_contour(
        raster,
        &grid,
        &density,
        map,
        density.threshold_90,
        CONTOUR_90,
        2,
    );
    draw_contour(
        raster,
        &grid,
        &density,
        map,
        density.threshold_50,
        CONTOUR_50,
        3,
    );
    draw_coastlines(raster, &grid, map, polygons);
    draw_spatial_mode(raster, &grid, &density, map);
    draw_truth(raster, &grid, map, arc);
    draw_scale_bar(raster, fonts, &grid, map);
    draw_axes(raster, fonts, &grid, map);

    let mean_error = arc
        .metrics
        .first()
        .map(|item| item.1.as_str())
        .unwrap_or("N/A");
    let mass_100_nm = arc
        .metrics
        .get(1)
        .map(|item| item.1.as_str())
        .unwrap_or("N/A");
    let metrics = format!("Mean-to-truth: {mean_error}   |   Mass within 100 NM: {mass_100_nm}");
    raster.text_centered(
        fonts,
        panel_x + panel_width / 2,
        panel_y + panel_height - 32,
        16.0,
        false,
        GREY,
        &metrics,
    );
    Ok(())
}

fn draw_legend(raster: &mut Raster, fonts: &Fonts) {
    let y = 116.0;
    draw_star_marker(raster, 285.0, y, 11.0);
    raster.text(fonts, 307, 102, 17.0, false, BLACK, "Actual state");

    draw_x_marker(raster, 520.0, y, 8.0);
    raster.text(fonts, 541, 102, 17.0, false, BLACK, "Spatial mode");

    raster.line(760.0, y, 810.0, y, RED, 4);
    raster.line(810.0, y, 797.0, y - 8.0, RED, 4);
    raster.line(810.0, y, 797.0, y + 8.0, RED, 4);
    raster.text(fonts, 827, 102, 17.0, false, BLACK, "True heading");

    raster.line(1_080.0, y, 1_125.0, y, CONTOUR_50, 4);
    raster.text(fonts, 1_140, 102, 17.0, false, BLACK, "50% HPD");

    raster.line(1_365.0, y, 1_410.0, y, CONTOUR_90, 3);
    raster.text(fonts, 1_425, 102, 17.0, false, BLACK, "90% HPD");

    raster.line(1_650.0, y, 1_695.0, y, CONTOUR_95, 3);
    raster.text(fonts, 1_710, 102, 17.0, false, BLACK, "95% HPD");

    raster.line(1_935.0, y, 1_980.0, y, CONTOUR_99, 2);
    raster.text(fonts, 1_995, 102, 17.0, false, BLACK, "99% HPD");
}

pub fn build_accident_panel_png(document: &ReportDocument) -> Result<Vec<u8>, ReportError> {
    validate(document)?;
    let grid = grid_with_bounds(
        &document.points,
        None,
        document.map_context.as_ref().map(|context| context.bounds),
    )?;
    let density = smooth_density(&grid);
    let polygons = land_polygons()?;
    let fonts = Fonts::new()?;
    let mut raster = Raster::new(IMAGE_WIDTH, IMAGE_HEIGHT, WHITE);
    raster.text_centered_fitted(
        &fonts,
        IMAGE_WIDTH as i32 / 2,
        18,
        38.0,
        28.0,
        IMAGE_WIDTH - 100,
        true,
        BLACK,
        &document.title.replace('_', " "),
    );
    raster.text_centered_fitted(
        &fonts,
        IMAGE_WIDTH as i32 / 2,
        70,
        20.0,
        15.0,
        IMAGE_WIDTH - 120,
        false,
        GREY,
        &document.subtitle.replace('_', " "),
    );
    let legend_y = 133.0;
    draw_x_marker(&mut raster, 430.0, legend_y, 9.0);
    raster.text(&fonts, 455, 118, 18.0, false, BLACK, "Spatial mode");
    for (x, color, thickness, label) in [
        (850.0, CONTOUR_50, 4, "50% HPD"),
        (1_210.0, CONTOUR_90, 3, "90% HPD"),
        (1_570.0, CONTOUR_95, 3, "95% HPD"),
        (1_930.0, CONTOUR_99, 2, "99% HPD"),
    ] {
        raster.line(x, legend_y, x + 55.0, legend_y, color, thickness);
        raster.text(&fonts, x as i32 + 70, 118, 18.0, false, BLACK, label);
    }
    let map = (
        165,
        185,
        IMAGE_WIDTH as i32 - 260,
        IMAGE_HEIGHT as i32 - 350,
    );
    draw_background(&mut raster, &grid, map, &polygons);
    draw_density(&mut raster, &grid, &density, map);
    draw_contour(
        &mut raster,
        &grid,
        &density,
        map,
        density.threshold_99,
        CONTOUR_99,
        2,
    );
    draw_contour(
        &mut raster,
        &grid,
        &density,
        map,
        density.threshold_95,
        CONTOUR_95,
        3,
    );
    draw_contour(
        &mut raster,
        &grid,
        &density,
        map,
        density.threshold_90,
        CONTOUR_90,
        3,
    );
    draw_contour(
        &mut raster,
        &grid,
        &density,
        map,
        density.threshold_50,
        CONTOUR_50,
        4,
    );
    draw_coastlines(&mut raster, &grid, map, &polygons);
    if let Some(context) = &document.map_context {
        draw_map_context(&mut raster, &fonts, &grid, map, context);
    }
    draw_spatial_mode(&mut raster, &grid, &density, map);
    draw_scale_bar(&mut raster, &fonts, &grid, map);
    draw_axes(&mut raster, &fonts, &grid, map);
    let condition = document
        .evidence_conditions
        .first()
        .map(String::as_str)
        .unwrap_or("Model-conditional MH370 estimate.");
    raster.text_centered_fitted(
        &fonts,
        IMAGE_WIDTH as i32 / 2,
        IMAGE_HEIGHT as i32 - 78,
        18.0,
        14.0,
        IMAGE_WIDTH - 120,
        false,
        GREY,
        condition,
    );
    raster.text_centered_fitted(
        &fonts,
        IMAGE_WIDTH as i32 / 2,
        IMAGE_HEIGHT as i32 - 45,
        15.0,
        12.0,
        IMAGE_WIDTH - 120,
        false,
        GREY,
        DISPLAY_KERNEL_NOTICE,
    );
    let mut output = Vec::new();
    {
        let cursor = Cursor::new(&mut output);
        let mut encoder = png::Encoder::new(cursor, IMAGE_WIDTH as u32, IMAGE_HEIGHT as u32);
        encoder.set_color(png::ColorType::Rgb);
        encoder.set_depth(png::BitDepth::Eight);
        encoder.set_compression(png::Compression::Balanced);
        let mut writer = encoder
            .write_header()
            .map_err(|error| ReportError::PngEncoding(error.to_string()))?;
        writer
            .write_image_data(&raster.pixels)
            .map_err(|error| ReportError::PngEncoding(error.to_string()))?;
    }
    Ok(output)
}

pub fn build_known_flight_panel_png(
    document: &KnownFlightControlReport,
) -> Result<Vec<u8>, ReportError> {
    validate_known_flight(document)?;
    if document.arcs.len() != 6 {
        return Err(ReportError::InvalidPosterior);
    }
    let polygons = land_polygons()?;
    let fonts = Fonts::new()?;
    let mut raster = Raster::new(IMAGE_WIDTH, IMAGE_HEIGHT, WHITE);
    raster.text_centered(
        &fonts,
        IMAGE_WIDTH as i32 / 2,
        12,
        35.0,
        true,
        BLACK,
        "MH371 truth-blind cruise control: posterior density by BTO arc",
    );
    raster.text_centered_fitted(
        &fonts,
        IMAGE_WIDTH as i32 / 2,
        59,
        20.0,
        15.0,
        IMAGE_WIDTH - 120,
        false,
        GREY,
        &document.subtitle.replace('_', " "),
    );
    draw_legend(&mut raster, &fonts);

    let margin_x = 55;
    let right_margin = 55;
    let top = 150;
    let gap_x = 42;
    let gap_y = 40;
    let bottom = 70;
    let panel_width = (IMAGE_WIDTH as i32 - margin_x - right_margin - 2 * gap_x) / 3;
    let panel_height = (IMAGE_HEIGHT as i32 - top - bottom - gap_y) / 2;
    for (index, arc) in document.arcs.iter().enumerate() {
        let column = index % 3;
        let row = index / 3;
        draw_panel(
            &mut raster,
            &fonts,
            arc,
            index,
            (
                margin_x + column as i32 * (panel_width + gap_x),
                top + row as i32 * (panel_height + gap_y),
                panel_width,
                panel_height,
            ),
            &polygons,
        )?;
    }
    raster.text_centered(
        &fonts,
        IMAGE_WIDTH as i32 / 2,
        IMAGE_HEIGHT as i32 - 48,
        16.0,
        false,
        GREY,
        "[CONTROL] Equal-weight deterministic seed replicates; 5-cell display kernel. Held-back truth enters only during scoring. Not an MH370 accident-flight result.",
    );

    let mut output = Vec::new();
    {
        let cursor = Cursor::new(&mut output);
        let mut encoder = png::Encoder::new(cursor, IMAGE_WIDTH as u32, IMAGE_HEIGHT as u32);
        encoder.set_color(png::ColorType::Rgb);
        encoder.set_depth(png::BitDepth::Eight);
        encoder.set_compression(png::Compression::Balanced);
        let mut writer = encoder
            .write_header()
            .map_err(|error| ReportError::PngEncoding(error.to_string()))?;
        writer
            .write_image_data(&raster.pixels)
            .map_err(|error| ReportError::PngEncoding(error.to_string()))?;
    }
    Ok(output)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{ReportMapBounds, ReportMapReference, ReportMapRoute, ReportPoint};

    #[test]
    fn fitted_text_respects_the_available_pixel_width() {
        let fonts = Fonts::new().unwrap();
        let (mask, size) = fitted_text_mask(
            fonts.face(true),
            &"long publication title ".repeat(40),
            38.0,
            28.0,
            900,
        );
        assert!(mask.width <= 900);
        assert_eq!(size, 28.0);
    }

    #[test]
    fn map_context_overlays_are_clipped_to_the_plot_rectangle() {
        let fonts = Fonts::new().unwrap();
        let mut raster = Raster::new(220, 180, WHITE);
        let grid = Grid {
            longitude_min: 0.0,
            longitude_max: 10.0,
            latitude_min: 0.0,
            latitude_max: 10.0,
            columns: 2,
            rows: 2,
            mass: vec![0.25; 4],
        };
        let rect = (40, 30, 100, 80);
        let context = ReportMapContext {
            bounds: ReportMapBounds {
                longitude_min_deg: 0.0,
                longitude_max_deg: 10.0,
                latitude_min_deg: 0.0,
                latitude_max_deg: 10.0,
            },
            routes: vec![
                ReportMapRoute {
                    label: "candidate label crossing the frame".to_string(),
                    style: "candidate".to_string(),
                    coordinates_deg: vec![[-5.0, -5.0], [5.0, 9.5], [15.0, 15.0]],
                },
                ReportMapRoute {
                    label: String::new(),
                    style: "arc".to_string(),
                    coordinates_deg: vec![[12.0, 2.0], [-2.0, 8.0]],
                },
                ReportMapRoute {
                    label: String::new(),
                    style: String::new(),
                    coordinates_deg: vec![[5.0, -5.0], [5.0, 15.0]],
                },
            ],
            references: vec![ReportMapReference {
                label: "edge reference".to_string(),
                latitude_deg: 5.0,
                longitude_deg: 9.9,
                heading_true_deg: Some(90.0),
            }],
        };

        draw_map_context(&mut raster, &fonts, &grid, rect, &context);
        assert_eq!(raster.clip, None);

        let (left, top, width, height) = rect;
        let right = left + width;
        let bottom = top + height;
        let mut changed_inside = false;
        for y in 0..raster.height as i32 {
            for x in 0..raster.width as i32 {
                let index = (y as usize * raster.width + x as usize) * 3;
                let pixel = &raster.pixels[index..index + 3];
                if x >= left && x < right && y >= top && y < bottom {
                    changed_inside |= pixel != WHITE;
                } else {
                    assert_eq!(pixel, WHITE, "overlay escaped at ({x}, {y})");
                }
            }
        }
        assert!(changed_inside);
    }

    #[test]
    fn six_panel_output_is_a_png() {
        let arc = KnownFlightArcReport {
            label: "fixture".to_string(),
            time_utc: "2014-03-07T03:00:00Z".to_string(),
            truth_latitude_deg: 2.0,
            truth_longitude_deg: 103.0,
            truth_heading_true_deg: 12.0,
            points: vec![
                ReportPoint {
                    latitude_deg: 1.0,
                    longitude_deg: 102.0,
                    weight: 0.25,
                },
                ReportPoint {
                    latitude_deg: 2.0,
                    longitude_deg: 103.0,
                    weight: 0.50,
                },
                ReportPoint {
                    latitude_deg: 3.0,
                    longitude_deg: 104.0,
                    weight: 0.25,
                },
            ],
            metrics: vec![("Mean error".to_string(), "1 NM".to_string())],
        };
        let document = KnownFlightControlReport {
            title: "fixture".to_string(),
            subtitle: "deterministic".to_string(),
            summary: Vec::new(),
            arcs: vec![arc; 6],
            evidence_conditions: Vec::new(),
            limitations: Vec::new(),
        };
        let bytes = build_known_flight_panel_png(&document).unwrap();
        assert!(bytes.starts_with(&[137, 80, 78, 71, 13, 10, 26, 10]));
        assert!(bytes.len() > 10_000);
    }

    #[test]
    fn accident_panel_output_is_a_deterministic_publication_png() {
        let document = ReportDocument {
            title: "MH370 posterior fixture".to_string(),
            subtitle: "display-only rendering fixture".to_string(),
            summary: Vec::new(),
            points: vec![
                ReportPoint {
                    latitude_deg: -30.0,
                    longitude_deg: 95.0,
                    weight: 0.2,
                },
                ReportPoint {
                    latitude_deg: -31.0,
                    longitude_deg: 96.0,
                    weight: 0.5,
                },
                ReportPoint {
                    latitude_deg: -32.0,
                    longitude_deg: 97.0,
                    weight: 0.3,
                },
            ],
            diagnostics: Vec::new(),
            evidence_conditions: vec!["SATCOM-only fixture".to_string()],
            limitations: Vec::new(),
            map_context: Some(ReportMapContext {
                bounds: ReportMapBounds {
                    longitude_min_deg: 90.0,
                    longitude_max_deg: 105.0,
                    latitude_min_deg: -38.0,
                    latitude_max_deg: -25.0,
                },
                references: Vec::new(),
                routes: Vec::new(),
            }),
        };
        let bytes = build_accident_panel_png(&document).unwrap();
        assert!(bytes.starts_with(&[137, 80, 78, 71, 13, 10, 26, 10]));
        assert_eq!(u32::from_be_bytes(bytes[16..20].try_into().unwrap()), 2_800);
        assert_eq!(u32::from_be_bytes(bytes[20..24].try_into().unwrap()), 1_900);
        assert_eq!(bytes, build_accident_panel_png(&document).unwrap());
    }
}
