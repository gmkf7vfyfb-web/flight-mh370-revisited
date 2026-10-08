//! The recovered-debris evidence table, `data/debris-evidence-audit.csv`: a byte-identical copy of
//! 'ISO Sept 28 Status/inputs/recovered-v01/.sources/ocean-drift-input-preparation/inputs/
//! debris-evidence-audit.csv' (sha256 f8ab96a9be107d2efa8968b17534f2e7d67daab45db8723ba3efa3045a332f69,
//! 41 rows), copied as ruled on 2026-10-08. The frozen original is untouched.
//!
//! Only the stringent identity set (`stringent_nine = yes`) is selected: the expanded set is
//! circular, 8 of its 11 additions citing agreement with CSIRO drift modelling in the
//! identification. Dates are DISCOVERY dates, never beaching dates. The Mossel Bay date conflict
//! is carried as recorded in the table (`decision` = primary_date_conflicts_with_summary); the
//! alternative date is a declared sensitivity, not reconciled here.

#[derive(Debug, Clone, PartialEq)]
pub struct Record {
    pub object_id: String,
    pub discovery_start: String,
    pub discovery_end: String,
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    pub motion_class: String,
    pub decision: String,
    pub stringent: bool,
}

/// Split one CSV line, honouring double quotes.
fn split_csv(line: &str) -> Vec<String> {
    let mut out = Vec::new();
    let mut cur = String::new();
    let mut quoted = false;
    let mut chars = line.chars().peekable();
    while let Some(c) = chars.next() {
        match (c, quoted) {
            ('"', true) if chars.peek() == Some(&'"') => { cur.push('"'); chars.next(); }
            ('"', _) => quoted = !quoted,
            (',', false) => out.push(std::mem::take(&mut cur)),
            _ => cur.push(c),
        }
    }
    out.push(cur);
    out
}

pub fn parse(text: &str) -> Result<Vec<Record>, String> {
    let mut lines = text.lines().filter(|l| !l.trim().is_empty());
    let header = split_csv(lines.next().ok_or("evidence: empty table")?);
    let col = |name: &str| header.iter().position(|h| h.trim() == name).ok_or(format!("evidence: no column `{name}`"));
    let (id, ds, de, la, lo, mc, dec, st) = (
        col("object_id")?, col("discovery_start")?, col("discovery_end")?, col("latitude_deg")?,
        col("longitude_deg")?, col("motion_class")?, col("decision")?, col("stringent_nine")?,
    );
    let mut out = Vec::new();
    for (n, line) in lines.enumerate() {
        let f = split_csv(line);
        if f.len() != header.len() {
            return Err(format!("evidence: row {} has {} fields, header {}", n + 2, f.len(), header.len()));
        }
        out.push(Record {
            object_id: f[id].trim().to_string(),
            discovery_start: f[ds].trim().to_string(),
            discovery_end: f[de].trim().to_string(),
            latitude_deg: f[la].trim().parse().unwrap_or(f64::NAN),
            longitude_deg: f[lo].trim().parse().unwrap_or(f64::NAN),
            motion_class: f[mc].trim().to_string(),
            decision: f[dec].trim().to_string(),
            stringent: f[st].trim() == "yes",
        });
    }
    Ok(out)
}

/// Days since 1970-01-01 for a proleptic Gregorian date (Hinnant's days_from_civil).
pub fn days_from_civil(y: i64, m: i64, d: i64) -> i64 {
    let y = if m <= 2 { y - 1 } else { y };
    let era = if y >= 0 { y } else { y - 399 } / 400;
    let yoe = y - era * 400;
    let mp = (m + 9) % 12;
    let doy = (153 * mp + 2) / 5 + d - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    era * 146_097 + doe - 719_468
}

/// Unix seconds at 00:00 UTC of an ISO date `YYYY-MM-DD`.
pub fn iso_date_unix_s(s: &str) -> Result<f64, String> {
    let p: Vec<i64> = s.split('-').map(|x| x.parse::<i64>()).collect::<Result<_, _>>().map_err(|_| format!("bad date `{s}`"))?;
    if p.len() != 3 {
        return Err(format!("bad date `{s}`"));
    }
    Ok(days_from_civil(p[0], p[1], p[2]) as f64 * 86_400.0)
}

pub const TABLE: &str = include_str!("data/debris-evidence-audit.csv");
