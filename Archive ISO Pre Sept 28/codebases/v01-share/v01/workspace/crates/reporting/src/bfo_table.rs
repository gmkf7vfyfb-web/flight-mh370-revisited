use std::fmt::Write as _;

use serde::{Deserialize, Serialize};

use crate::ReportError;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BfoMatchTablePanel {
    pub title: String,
    pub epoch_utc: String,
    pub channel: String,
    pub observed_bfo_hz: f64,
    /// Rows are ascending vertical-speed buckets; columns are ascending
    /// true-heading buckets.
    pub counts: Vec<Vec<usize>>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct BfoMatchTables {
    pub title: String,
    pub systematic_sample_count: usize,
    pub heading_step_deg: f64,
    pub tolerance_sd: f64,
    pub tolerance_hz: f64,
    pub acknowledgement_elapsed_seconds: f64,
    pub heading_buckets_deg: Vec<[f64; 2]>,
    pub vertical_speed_buckets_fpm: Vec<[f64; 2]>,
    pub request: BfoMatchTablePanel,
    pub acknowledgement: BfoMatchTablePanel,
    pub counting_rule: String,
    pub limitation: String,
}

fn validate(document: &BfoMatchTables) -> Result<(), ReportError> {
    let values = [
        document.heading_step_deg,
        document.tolerance_sd,
        document.tolerance_hz,
        document.acknowledgement_elapsed_seconds,
        document.request.observed_bfo_hz,
        document.acknowledgement.observed_bfo_hz,
    ];
    let rows = document.vertical_speed_buckets_fpm.len();
    let columns = document.heading_buckets_deg.len();
    let panel_shape_is_valid = |panel: &BfoMatchTablePanel| {
        panel.counts.len() == rows
            && panel.counts.iter().all(|row| row.len() == columns)
            && panel
                .counts
                .iter()
                .flatten()
                .all(|count| *count <= document.systematic_sample_count)
    };
    if document.title.trim().is_empty()
        || document.systematic_sample_count == 0
        || rows == 0
        || columns == 0
        || !values.iter().all(|value| value.is_finite())
        || document.heading_step_deg <= 0.0
        || document.tolerance_sd <= 0.0
        || document.tolerance_hz <= 0.0
        || document.acknowledgement_elapsed_seconds <= 0.0
        || document
            .heading_buckets_deg
            .iter()
            .chain(document.vertical_speed_buckets_fpm.iter())
            .any(|bucket| {
                !bucket[0].is_finite() || !bucket[1].is_finite() || bucket[0] >= bucket[1]
            })
        || !panel_shape_is_valid(&document.request)
        || !panel_shape_is_valid(&document.acknowledgement)
    {
        return Err(ReportError::InvalidBfoTable);
    }
    Ok(())
}

fn fill(count: usize, sample_count: usize) -> (u8, u8, u8) {
    if count == 0 {
        return (255, 255, 255);
    }
    let t = (count as f64 / sample_count as f64).sqrt();
    let low = (237.0, 244.0, 250.0);
    let high = (20.0, 89.0, 148.0);
    (
        (low.0 * (1.0 - t) + high.0 * t).round() as u8,
        (low.1 * (1.0 - t) + high.1 * t).round() as u8,
        (low.2 * (1.0 - t) + high.2 * t).round() as u8,
    )
}

fn draw_panel(
    svg: &mut String,
    x: f64,
    panel: &BfoMatchTablePanel,
    document: &BfoMatchTables,
    cell_height: f64,
) {
    let table_y = 202.0;
    let label_width = 168.0;
    let cell_width = 100.0;
    let columns = document.heading_buckets_deg.len();
    let rows = document.vertical_speed_buckets_fpm.len();
    let table_width = label_width + columns as f64 * cell_width;
    let _ = writeln!(
        svg,
        "<text x=\"{x:.1}\" y=\"116\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"22\" font-weight=\"700\" fill=\"#0e1f35\">{}</text>",
        panel.title
    );
    let _ = writeln!(
        svg,
        "<text x=\"{x:.1}\" y=\"144\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"15\" fill=\"#59636f\">{} UTC | {} | raw BFO {:.0} Hz</text>",
        panel.epoch_utc, panel.channel, panel.observed_bfo_hz
    );
    let _ = writeln!(
        svg,
        "<text x=\"{:.1}\" y=\"174\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"14\" font-weight=\"700\" text-anchor=\"middle\" fill=\"#0e1f35\">true heading (deg)</text>",
        x + label_width + columns as f64 * cell_width / 2.0
    );
    let _ = writeln!(
        svg,
        "<text x=\"{:.1}\" y=\"197\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"13\" font-weight=\"700\" text-anchor=\"middle\" fill=\"#0e1f35\">vertical speed (ft/min)</text>",
        x + label_width / 2.0
    );
    for column in 0..columns {
        let bucket = document.heading_buckets_deg[column];
        let cell_x = x + label_width + column as f64 * cell_width;
        let _ = writeln!(
            svg,
            "<text x=\"{:.1}\" y=\"197\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"13\" text-anchor=\"middle\" fill=\"#59636f\">{:.0}-{:.0}</text>",
            cell_x + cell_width / 2.0,
            bucket[0],
            bucket[1]
        );
    }
    for display_row in 0..rows {
        let source_row = rows - 1 - display_row;
        let bucket = document.vertical_speed_buckets_fpm[source_row];
        let cell_y = table_y + display_row as f64 * cell_height;
        let _ = writeln!(
            svg,
            "<rect x=\"{x:.1}\" y=\"{cell_y:.1}\" width=\"{label_width:.1}\" height=\"{cell_height:.1}\" fill=\"#f4f6f8\" stroke=\"#cfd6dd\"/>"
        );
        let _ = writeln!(
            svg,
            "<text x=\"{:.1}\" y=\"{:.1}\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"13\" text-anchor=\"end\" fill=\"#0e1f35\">{:+.0} to {:+.0}</text>",
            x + label_width - 12.0,
            cell_y + cell_height * 0.58,
            bucket[0],
            bucket[1]
        );
        for column in 0..columns {
            let count = panel.counts[source_row][column];
            let fraction = count as f64 / document.systematic_sample_count as f64;
            let (red, green, blue) = fill(count, document.systematic_sample_count);
            let cell_x = x + label_width + column as f64 * cell_width;
            let text_color = if fraction > 0.48 {
                "#ffffff"
            } else {
                "#0e1f35"
            };
            let _ = writeln!(
                svg,
                "<rect x=\"{cell_x:.1}\" y=\"{cell_y:.1}\" width=\"{cell_width:.1}\" height=\"{cell_height:.1}\" fill=\"rgb({red},{green},{blue})\" stroke=\"#cfd6dd\"/>"
            );
            let label = if count == 0 {
                "-".to_string()
            } else {
                count.to_string()
            };
            let _ = writeln!(
                svg,
                "<text x=\"{:.1}\" y=\"{:.1}\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"19\" font-weight=\"700\" text-anchor=\"middle\" fill=\"{text_color}\">{label}</text>",
                cell_x + cell_width / 2.0,
                cell_y + cell_height * 0.43
            );
            if count > 0 {
                let _ = writeln!(
                    svg,
                    "<text x=\"{:.1}\" y=\"{:.1}\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"11\" text-anchor=\"middle\" fill=\"{text_color}\">{:.1}%</text>",
                    cell_x + cell_width / 2.0,
                    cell_y + cell_height * 0.72,
                    100.0 * fraction
                );
            }
        }
    }
    let _ = writeln!(
        svg,
        "<rect x=\"{x:.1}\" y=\"{table_y:.1}\" width=\"{table_width:.1}\" height=\"{:.1}\" fill=\"none\" stroke=\"#0e1f35\" stroke-width=\"1.5\"/>",
        rows as f64 * cell_height
    );
}

pub fn build_bfo_match_tables_svg(document: &BfoMatchTables) -> Result<Vec<u8>, ReportError> {
    validate(document)?;
    let row_count = document.vertical_speed_buckets_fpm.len();
    let cell_height = if row_count <= 6 { 74.0 } else { 48.0 };
    let table_bottom = 202.0 + row_count as f64 * cell_height;
    let footer_title_y = table_bottom + 36.0;
    let footer_rule_y = table_bottom + 60.0;
    let footer_limitation_y = table_bottom + 90.0;
    let svg_height = footer_limitation_y + 44.0;
    let mut svg = String::new();
    let _ = writeln!(
        svg,
        "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1720\" height=\"{svg_height:.0}\" viewBox=\"0 0 1720 {svg_height:.0}\">"
    );
    let _ = writeln!(
        svg,
        "<rect width=\"1720\" height=\"{svg_height:.0}\" fill=\"white\"/>"
    );
    let _ = writeln!(
        svg,
        "<text x=\"40\" y=\"48\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"27\" font-weight=\"700\" fill=\"#0e1f35\">{}</text>",
        document.title
    );
    let _ = writeln!(
        svg,
        "<text x=\"40\" y=\"78\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"15\" fill=\"#59636f\">Counts are unique weighted-posterior systematic samples (n={}); tolerance = +/-{:.0} Hz ({:.0} SD).</text>",
        document.systematic_sample_count, document.tolerance_hz, document.tolerance_sd
    );
    draw_panel(&mut svg, 40.0, &document.request, document, cell_height);
    draw_panel(
        &mut svg,
        900.0,
        &document.acknowledgement,
        document,
        cell_height,
    );
    let _ = writeln!(
        svg,
        "<text x=\"40\" y=\"{footer_title_y:.1}\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"14\" font-weight=\"700\" fill=\"#0e1f35\">Cell rule</text>"
    );
    let _ = writeln!(
        svg,
        "<text x=\"40\" y=\"{footer_rule_y:.1}\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"13\" fill=\"#59636f\">{}</text>",
        document.counting_rule
    );
    let _ = writeln!(
        svg,
        "<text x=\"40\" y=\"{footer_limitation_y:.1}\" font-family=\"Helvetica,Arial,sans-serif\" font-size=\"13\" fill=\"#59636f\">{}</text>",
        document.limitation
    );
    let _ = writeln!(svg, "</svg>");
    Ok(svg.into_bytes())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn renders_two_dynamic_tables() {
        let panel = BfoMatchTablePanel {
            title: "First transmission".to_string(),
            epoch_utc: "00:19:29".to_string(),
            channel: "R600".to_string(),
            observed_bfo_hz: 182.0,
            counts: vec![vec![1; 6]; 10],
        };
        let document = BfoMatchTables {
            title: "Raw BFO feasibility by heading and vertical speed".to_string(),
            systematic_sample_count: 2,
            heading_step_deg: 5.0,
            tolerance_sd: 2.0,
            tolerance_hz: 14.0,
            acknowledgement_elapsed_seconds: 8.027,
            heading_buckets_deg: (0..6)
                .map(|index| [index as f64 * 60.0, (index + 1) as f64 * 60.0])
                .collect(),
            vertical_speed_buckets_fpm: (0..10)
                .map(|index| {
                    [
                        -23_333.0 + index as f64 * 2_000.0,
                        -21_333.0 + index as f64 * 2_000.0,
                    ]
                })
                .collect(),
            request: panel.clone(),
            acknowledgement: panel,
            counting_rule: "fixture".to_string(),
            limitation: "fixture".to_string(),
        };
        let svg = build_bfo_match_tables_svg(&document).unwrap();
        let text = std::str::from_utf8(&svg).unwrap();
        assert!(text.starts_with("<svg"));
        assert!(text.contains("First transmission"));
        assert_eq!(text.matches("<rect x=").count(), 142);
    }
}
