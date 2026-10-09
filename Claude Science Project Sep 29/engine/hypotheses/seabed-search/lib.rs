//! Seabed search: the wreck was not found by the sonar searches of the seafloor.
//!
//! Assumption. Every unsuccessful seabed search is evidence against the wreck lying where
//! it looked. For an impact point y the probability of the observed outcome (no find) is
//!
//!   P(no find | y) = rho + (1 - rho) * prod_k (1 - q_k * c_k(y))
//!
//! - c_k(y): the fraction of the ground around y on which campaign k recorded valid sonar
//!   data. It is read from a 0.01 deg raster (`coverage/*.cov`, built by
//!   `prepare/build_coverage.py`) by bilinear interpolation between cell centres, so it is
//!   the covered fraction within about 1 km of y. That scale belongs to the data model,
//!   not to the sampler: a debris field is an extended target ("aircraft debris fields
//!   typically cover areas larger than 200 m by 200 m", ATSB 2017, p. 96), and averaging
//!   at 1 km conserves the uncovered area while the posterior varies over tens of km.
//!   Outside a raster c_k = 0: nobody searched there.
//! - q_k: the probability that data over the wreck would have led to it being found.
//! - rho: the probability that the wreck could not have been found by any of these
//!   searches wherever it lay (terrain, burial, a contact seen but misclassified). It is
//!   the shared part of the misses; given detectability, campaigns miss independently.
//!   rho is the model error: without it a covered cell would be ruled out to within 1 - q.
//!
//! The likelihood is on an absolute scale (`absolute_scale`): it is the probability of the
//! observed outcome, not a relative weight. It is linear in rho and, for each campaign, in q_k, so an
//! uncertain rho or q_k (with independent priors) enters only through its mean; the spread
//! does not move the estimate and needs no separate strata. The mean of rho does matter
//! and is shown as a labelled sensitivity (report.py).
//!
//! Observations: `search:<campaign name>` (e.g. `search:phase2-2014-2017`), one per enabled
//! campaign, declared through `observations`.
//!
//! Layers (areas from the prepare script, on the authalic sphere):
//! - `phase2`: ATSB-led underwater search, 2014-2017: the union of the valid 5 m pixels
//!   of Geoscience Australia's four backscatter mosaics (deep-tow side scan 103,922 km2,
//!   GO Phoenix synthetic aperture sonar 14,627, Dong Hai Jiu SAS 3,164, AUV side scan
//!   16,164), 120,487 km2 in all; ATSB: "in excess of 120,000 square kilometres" (The
//!   Operational Search for MH370, 3 Oct 2017, executive summary). Source: GA's MH370
//!   Phase 2 data release, CC BY 4.0, https://files.ausseabed.gov.au/survey/
//!   MH370-Phase2-SOnarImagery-Backscatter-5m-2018.zip. The deep-tow pixels agree with
//!   GA's vector L0 footprint (103,925 km2) to 100 km2 each way. For q, ATSB Fig. 73
//!   (p. 96) rates 97.4% of the area at > 95% confidence of detection, 2.1% at 70% on
//!   average and 0.5% as gaps at 0%. Gaps without data are already holes here (c = 0), so
//!   q = (0.974 x 0.95 + 0.021 x 0.70) / 0.995 = 0.945; ATSB also rated terrain-avoidance
//!   gaps that hold some data at 0%, so the conditional value lies between 0.940 and
//!   0.945. Regions range from 91.5% to 98.7% high confidence.
//! - `bluefin-2014`: the Bluefin-21 (Artemis AUV) search from Ocean Shield, April-May
//!   2014, near 21 S, 104 E: Geoscience Australia's two display polygons, 771 km2 (ATSB
//!   reports 860 km2), so display geometry, not swaths. q = 0.9, not assessed by ATSB.
//! - Ocean Infinity 2018, INFERRED and not in git (the tracing's licence is unclear). Ocean
//!   Infinity published no geometry for its 2018 search ("over 112,000 km2", 29 May 2018;
//!   120,000 km2 in its data donation). The prepare script turns a community tracing of the
//!   searched region (MH370-CAPTION search-areas KML, grade C, 148,993 km2) less the
//!   22,980 km2 of it that Phase 2 had covered, assuming OI did not survey that again,
//!   into `data/external/search-coverage/ocean-infinity-2018.cov` (126,009 km2). A campaign
//!   reads it with `layer_file` and must set `coverage_fraction`, the reported area over
//!   the layer's: 0.889-0.952. Reported only as a labelled variant, never as the base.
//! - Not used: the 2025-26 Ocean Infinity search (about 7,571 km2 surveyed, no geometry),
//!   the 2014 bathymetric survey (no debris detection), the 2014 surface search (belongs to
//!   a drift-dependent module).
//!
//! Departures from earlier work: the archived codebase used display geometry, omitted the
//! SAS and AUV data (GO Phoenix alone covers 13,446 km2 at 32.7-35.3 S outside the deep-tow
//! footprint) and applied a 94% detection probability that already counted the gaps over
//! a footprint that also excluded them. Here coverage is measured from the data and q is
//! conditional on data being present. The deep-tow footprint's own `area_km2` attribute
//! (130,961) is square degrees x 111.12^2, not an area.
//!
//! How it enters the estimate: as an impact module (named in a `[[compose]]` set). For each
//! impact sample `impact_log_likelihood` returns ln P(no find | impact position): exactly 0
//! outside every searched area (not searched is no information, however far beyond the arc
//! the impact lies), NaN only for a sample without a position. `predict` gives, per impact,
//! each campaign's covered fraction, the miss probability for a detectable wreck (the
//! product term) and P(no find). Phase 2 searched 25 NM either side of the 7th arc, widened
//! in places to 36 NM north-west and 41 NM south-east (ATSB 2017, pp. 76, 95), so the spread
//! of impacts about the arc decides how much the search moves the estimate.

use hypothesis::{Hypothesis, ImpactView};
use serde::Deserialize;

/// Embedded coverage layers, derived from CC BY 4.0 Geoscience Australia data (format
/// documented in `prepare/build_coverage.py::write_cov`).
/// `phase2` is the per-cell maximum of the four Phase 2 mosaics: one cumulative campaign, which
/// is what Davey eq. (11.1) assumes and what hides the ground swept more than once. The four
/// per-sensor layers are the same cells kept apart, so that repeat search can be modelled
/// (`prepare/build_per_sensor_layers.py`). Their sum is 137,877.1 km2 against a union of
/// 120,486.5: 17,390.6 km2 of repeat coverage, over 18,129.6 km2 of ground, is invisible in
/// `phase2`. Never list `phase2` and a per-sensor layer in the same run: that counts ground twice.
const LAYERS: [(&str, &[u8]); 6] = [
    ("phase2", include_bytes!("coverage/phase2.cov")),
    ("bluefin-2014", include_bytes!("coverage/bluefin-2014.cov")),
    ("phase2-deep-tow", include_bytes!("coverage/phase2-deep-tow.cov")),
    ("phase2-go-phoenix", include_bytes!("coverage/phase2-go-phoenix.cov")),
    ("phase2-dhj", include_bytes!("coverage/phase2-dhj.cov")),
    ("phase2-auv", include_bytes!("coverage/phase2-auv.cov")),
];

/// How misses on ground that more than one campaign covered are combined.
#[derive(Deserialize, Debug, Clone, Copy, PartialEq, Eq, Default)]
#[serde(rename_all = "kebab-case")]
pub enum Dependence {
    /// Default. Undetectability is a property of the site, drawn once: terrain that hid the
    /// wreck from one pass hides it from the next.
    ///   P(no find) = rho + (1 - rho) prod_k [1 - c_k q_k]
    #[default]
    Shared,
    /// Every campaign draws its own undetectability, so a second sweep of the same ground is a
    /// fresh chance to see a wreck the first sweep could not have seen.
    ///   P(no find) = prod_k [rho + (1 - rho)(1 - c_k q_k)]
    /// Reported beside `shared`, never as the default: it treats burial and terrain masking as
    /// if they were re-rolled between campaigns.
    Independent,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Params {
    /// rho: probability that the wreck was undetectable by every campaign.
    undetectable_probability: f64,
    /// `shared` (default) or `independent`; see [`Dependence`]. Identical wherever campaigns do
    /// not overlap, so it only acts on repeat-searched ground.
    #[serde(default)]
    miss_dependence: Dependence,
    campaigns: Vec<CampaignParams>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct CampaignParams {
    /// Observation name, e.g. "phase2-2014-2017" (observation `search:phase2-2014-2017`).
    name: String,
    /// One of the embedded coverage layers...
    layer: Option<String>,
    /// ...or a raster file outside git, relative to the runner's working directory (the
    /// repository root), for labelled variants such as the inferred Ocean Infinity 2018 layer.
    layer_file: Option<std::path::PathBuf>,
    /// q: probability that data over the wreck would have found it.
    detection_probability: f64,
    /// Share of the layer's marked ground that was actually covered: 1 for measured data,
    /// the reported area over the layer's area for an inferred layer.
    #[serde(default = "one")]
    coverage_fraction: f64,
}

fn one() -> f64 {
    1.0
}

/// A coverage fraction on a regular latitude/longitude grid.
#[derive(Debug, Clone, PartialEq)]
pub struct Raster {
    south: f64,
    west: f64,
    step: f64,
    rows: usize,
    cols: usize,
    /// Covered fraction x 255, row-major from the south-west cell.
    values: Vec<u8>,
}

impl Raster {
    pub fn decode(bytes: &[u8]) -> Result<Self, String> {
        let take = |at: usize, n: usize| bytes.get(at..at + n).ok_or("coverage raster is truncated");
        let u32_at = |at| -> Result<u32, String> { Ok(u32::from_le_bytes(take(at, 4)?.try_into().unwrap())) };
        let f64_at = |at| -> Result<f64, String> { Ok(f64::from_le_bytes(take(at, 8)?.try_into().unwrap())) };
        if take(0, 8)? != b"MH370COV" || u32_at(8)? != 1 {
            return Err("not a version-1 MH370COV raster".into());
        }
        let (south, west, step) = (f64_at(12)?, f64_at(20)?, f64_at(28)?);
        let (rows, cols, runs) = (u32_at(36)? as usize, u32_at(40)? as usize, u32_at(44)? as usize);
        let mut values = Vec::with_capacity(rows * cols);
        for run in take(48, 3 * runs)?.chunks_exact(3) {
            let count = u16::from_le_bytes([run[1], run[2]]) as usize;
            values.extend(std::iter::repeat(run[0]).take(count));
        }
        if values.len() != rows * cols || bytes.len() != 48 + 3 * runs || !(step > 0.0) {
            return Err("coverage raster size does not match its header".into());
        }
        Ok(Self { south, west, step, rows, cols, values })
    }

    fn cell(&self, row: isize, col: isize) -> f64 {
        if row < 0 || col < 0 || row as usize >= self.rows || col as usize >= self.cols {
            return 0.0;
        }
        f64::from(self.values[row as usize * self.cols + col as usize]) / 255.0
    }

    /// Covered fraction near (lat, lon): bilinear between cell centres, zero off the grid.
    pub fn coverage(&self, lat: f64, lon: f64) -> f64 {
        let y = (lat - self.south) / self.step - 0.5;
        let x = (lon - self.west) / self.step - 0.5;
        if !(y > -1.0 && x > -1.0 && y < self.rows as f64 && x < self.cols as f64) {
            return 0.0;
        }
        let (r, c) = (y.floor(), x.floor());
        let (fy, fx) = (y - r, x - c);
        let (r, c) = (r as isize, c as isize);
        (1.0 - fy) * ((1.0 - fx) * self.cell(r, c) + fx * self.cell(r, c + 1))
            + fy * ((1.0 - fx) * self.cell(r + 1, c) + fx * self.cell(r + 1, c + 1))
    }

    /// Covered area in km2 on the authalic sphere (as the prepare script computes it).
    pub fn area_km2(&self) -> f64 {
        const R_KM: f64 = 6371.0072;
        (0..self.rows)
            .map(|r| {
                let lat = |k: usize| (self.south + k as f64 * self.step).to_radians();
                let row_area = R_KM * R_KM * self.step.to_radians() * (lat(r + 1).sin() - lat(r).sin());
                let covered: f64 = self.values[r * self.cols..(r + 1) * self.cols].iter().map(|&v| f64::from(v)).sum();
                row_area * covered / 255.0
            })
            .sum()
    }
}

pub struct Campaign {
    pub name: String,
    /// q x coverage_fraction: detection probability where the layer marks full coverage.
    pub effective_detection: f64,
    pub raster: Raster,
}

pub struct SeabedSearch {
    pub undetectable: f64,
    pub dependence: Dependence,
    pub campaigns: Vec<Campaign>,
}

pub fn new(params: &toml::Value) -> Result<Box<dyn Hypothesis>, String> {
    Ok(Box::new(SeabedSearch::from_params(params)?))
}

impl SeabedSearch {
    pub fn from_params(params: &toml::Value) -> Result<Self, String> {
        let params: Params = params.clone().try_into().map_err(|e| format!("seabed-search: {e}"))?;
        let unit = |x: f64| (0.0..=1.0).contains(&x);
        let rho = params.undetectable_probability;
        if !unit(rho) {
            return Err("seabed-search: undetectable_probability must be in [0, 1]".into());
        }
        let mut campaigns = Vec::new();
        for c in params.campaigns {
            let raster = match (&c.layer, &c.layer_file) {
                (Some(layer), None) => {
                    let bytes = LAYERS.iter().find(|(name, _)| name == layer).map(|(_, b)| *b).ok_or_else(|| {
                        format!("seabed-search: unknown layer `{layer}`; known: {:?}", LAYERS.map(|(n, _)| n))
                    })?;
                    Raster::decode(bytes)?
                }
                (None, Some(path)) => {
                    let bytes = std::fs::read(path).map_err(|e| format!("seabed-search: {}: {e}", path.display()))?;
                    Raster::decode(&bytes).map_err(|e| format!("seabed-search: {}: {e}", path.display()))?
                }
                _ => return Err(format!("seabed-search: {}: set exactly one of layer and layer_file", c.name)),
            };
            let q = c.detection_probability * c.coverage_fraction;
            if !unit(c.detection_probability) || !unit(c.coverage_fraction) {
                return Err(format!("seabed-search: {}: probabilities must be in [0, 1]", c.name));
            }
            if rho == 0.0 && q == 1.0 {
                return Err(format!("seabed-search: {}: certain detection with rho = 0 rules out covered ground", c.name));
            }
            if c.name.is_empty() || c.name.contains([',', '/', ':', '\n', '\r']) {
                return Err(format!("seabed-search: campaign name {:?} must be non-empty, without , / : or line breaks", c.name));
            }
            if campaigns.iter().any(|k: &Campaign| k.name == c.name) {
                return Err(format!("seabed-search: campaign `{}` listed twice", c.name));
            }
            campaigns.push(Campaign { name: c.name, effective_detection: q, raster });
        }
        Ok(Self { undetectable: rho, dependence: params.miss_dependence, campaigns })
    }

    /// P(no find | impact at lat, lon, wreck detectable): every campaign misses independently.
    pub fn detectable_miss_probability(&self, lat: f64, lon: f64) -> f64 {
        self.campaigns.iter().map(|c| 1.0 - c.effective_detection * c.raster.coverage(lat, lon)).product()
    }

    /// P(no find | impact at lat, lon). Under `Shared` the wreck is undetectable or not, once,
    /// and the campaigns then miss independently; under `Independent` each campaign draws its
    /// own undetectability. A campaign with no coverage here contributes exactly 1 either way,
    /// so the two agree wherever campaigns do not overlap.
    pub fn miss_probability(&self, lat: f64, lon: f64) -> f64 {
        let rho = self.undetectable;
        match self.dependence {
            Dependence::Shared => rho + (1.0 - rho) * self.detectable_miss_probability(lat, lon),
            Dependence::Independent => self
                .campaigns
                .iter()
                .map(|c| rho + (1.0 - rho) * (1.0 - c.effective_detection * c.raster.coverage(lat, lon)))
                .product(),
        }
    }
}

/// The impact position, if the sample has one.
fn position(impact: &ImpactView) -> Option<(f64, f64)> {
    let (lat, lon) = (impact.latitude_deg, impact.longitude_deg);
    (lat.is_finite() && lon.is_finite()).then_some((lat, lon))
}

impl Hypothesis for SeabedSearch {
    fn observations(&self) -> Vec<String> {
        self.campaigns.iter().map(|c| format!("search:{}", c.name)).collect()
    }

    fn absolute_scale(&self) -> bool {
        true
    }

    fn prediction_columns(&self) -> Vec<String> {
        let mut columns: Vec<String> = self.campaigns.iter().map(|c| format!("covered_fraction_{}", c.name)).collect();
        columns.extend(["detectable_miss_probability".to_string(), "no_find_probability".to_string()]);
        columns
    }

    fn impact_log_likelihood(&self, impact: &ImpactView, _choice: &[usize]) -> f64 {
        position(impact).map_or(f64::NAN, |(lat, lon)| self.miss_probability(lat, lon).ln())
    }

    fn predict(&self, impact: &ImpactView, out: &mut [f64]) {
        let Some((lat, lon)) = position(impact) else {
            out.fill(f64::NAN);
            return;
        };
        let n = self.campaigns.len();
        for (slot, c) in out[..n].iter_mut().zip(&self.campaigns) {
            *slot = c.raster.coverage(lat, lon);
        }
        out[n] = self.detectable_miss_probability(lat, lon);
        out[n + 1] = self.miss_probability(lat, lon);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A raster from explicit cell values (fraction x 255), for fixtures.
    fn raster(south: f64, west: f64, step: f64, rows: usize, cols: usize, values: Vec<u8>) -> Raster {
        let mut bytes = b"MH370COV".to_vec();
        bytes.extend(1u32.to_le_bytes());
        for v in [south, west, step] {
            bytes.extend(v.to_le_bytes());
        }
        let runs: Vec<(u8, u16)> = values.iter().map(|&v| (v, 1)).collect();
        for n in [rows as u32, cols as u32, runs.len() as u32] {
            bytes.extend(n.to_le_bytes());
        }
        for (v, n) in runs {
            bytes.push(v);
            bytes.extend(n.to_le_bytes());
        }
        Raster::decode(&bytes).unwrap()
    }

    fn search(rho: f64, campaigns: Vec<(f64, Raster)>) -> SeabedSearch {
        with_dependence(rho, Dependence::Shared, campaigns)
    }

    fn with_dependence(rho: f64, dependence: Dependence, campaigns: Vec<(f64, Raster)>) -> SeabedSearch {
        SeabedSearch {
            undetectable: rho,
            dependence,
            campaigns: campaigns
                .into_iter()
                .enumerate()
                .map(|(i, (q, raster))| Campaign { name: format!("c{i}"), effective_detection: q, raster })
                .collect(),
        }
    }

    /// A 1 x 2 raster: the western cell (0-1 E) searched, the eastern (1-2 E) not.
    fn half() -> Raster {
        raster(0.0, 0.0, 1.0, 1, 2, vec![255, 0])
    }

    #[test]
    fn half_the_mass_covered_at_80_percent_leaves_one_sixth_inside() {
        // Archived fixture (search-evidence crate): equal prior mass at a searched and an
        // unsearched point, q = 0.8. Evidence Z = 0.5 x 0.2 + 0.5 x 1 = 0.6; the searched
        // point keeps 0.1 / 0.6 = 1/6 of the posterior.
        let s = search(0.0, vec![(0.8, half())]);
        let (inside, outside) = (s.miss_probability(0.5, 0.5), s.miss_probability(0.5, 1.5));
        let z = 0.5 * inside + 0.5 * outside;
        assert!((z - 0.6).abs() < 1e-12);
        assert!((0.5 * inside / z - 1.0 / 6.0).abs() < 1e-12);
    }

    #[test]
    fn limiting_cases_and_shared_versus_independent_misses() {
        let covered = |rho, q| search(rho, vec![(q, half())]).miss_probability(0.5, 0.5);
        assert_eq!(covered(1.0, 0.8), 1.0); // an undetectable wreck: no information
        assert_eq!(covered(0.3, 0.0), 1.0); // a useless sensor: no information
        assert_eq!(search(0.0, vec![(0.8, half())]).miss_probability(10.0, 10.0), 1.0); // off every raster
        assert!((covered(0.1, 0.8) - (0.1 + 0.9 * 0.2)).abs() < 1e-12);
        // Two campaigns over the same ground miss independently given detectability...
        let twice = |rho| search(rho, vec![(0.8, half()), (0.8, half())]).miss_probability(0.5, 0.5);
        assert!((twice(0.0) - 0.04).abs() < 1e-12);
        // ...and rho is the part of the miss they share.
        assert!((twice(0.25) - (0.25 + 0.75 * 0.04)).abs() < 1e-12);
    }

    /// Davey et al. (2016) §11.1, printed p. 101, eq. (11.1):
    ///   p(x_final | S, Z_K)  proportional to  [1 - P_D(x_final)] p(x_final | Z_K)
    /// with P_D "the probability that the cumulative search effort would have detected the
    /// aircraft at any particular location". Set rho = 0, take a point target (the impact
    /// position itself), and collapse the search to one cumulative campaign: this module's
    /// likelihood must then be exactly [1 - P_D], with P_D = c(x) q. The test computes P_D
    /// along an independent path and compares it with the full public hook, on the real
    /// Phase 2 layer, at points inside, outside and on the ragged edge of the coverage.
    #[test]
    fn reduces_to_davey_eq_11_1_for_a_point_target_one_campaign_and_rho_zero() {
        let q = 0.945;
        let params = format!(
            "undetectable_probability = 0.0\n\
             [[campaigns]]\nname = \"cumulative\"\nlayer = \"phase2\"\ndetection_probability = {q}\n"
        );
        let module = SeabedSearch::from_params(&toml::from_str(&params).unwrap()).unwrap();
        let layer = Raster::decode(LAYERS.iter().find(|(n, _)| *n == "phase2").unwrap().1).unwrap();
        let points = [
            (-38.0, 89.0),   // inside
            (-37.5, 88.6),   // inside
            (-36.0, 91.5),   // near the northern end
            (-39.9, 86.3),   // near the southern end
            (-34.0, 93.0),   // off the searched ground
            (-20.0, 110.0),  // far outside the raster
            (-38.2345, 88.7654), // between cell centres, where c is bilinear
        ];
        let mut covered = 0;
        for (lat, lon) in points {
            let p_d = layer.coverage(lat, lon) * q; // Davey's P_D, by an independent path
            let davey = (1.0 - p_d).ln();
            let ours = module.impact_log_likelihood(&impact(lat, lon), &[]);
            assert!((ours - davey).abs() < 1e-15, "({lat}, {lon}): {ours} vs {davey}");
            covered += usize::from(p_d > 0.0);
        }
        assert!(covered >= 4, "the test must exercise searched ground, not only empty raster");
    }

    #[test]
    fn repeat_search_dependence_acts_only_where_campaigns_overlap() {
        // Two campaigns over the same searched cell, q = 0.8, rho = 0.2. Shared: the wreck is
        // undetectable once, 0.2 + 0.8 x 0.2 x 0.2. Independent: each campaign re-rolls it,
        // (0.2 + 0.8 x 0.2)^2, which removes much more mass from doubly searched ground.
        let both = |d| with_dependence(0.2, d, vec![(0.8, half()), (0.8, half())]).miss_probability(0.5, 0.5);
        assert!((both(Dependence::Shared) - 0.232).abs() < 1e-12);
        assert!((both(Dependence::Independent) - 0.1296).abs() < 1e-12);
        // Disjoint campaigns: a campaign with no coverage contributes exactly 1 under either
        // rule, so the arms agree. West cell searched by one, east cell by the other.
        let east = raster(0.0, 0.0, 1.0, 1, 2, vec![0, 255]);
        let disjoint = |d| with_dependence(0.2, d, vec![(0.8, half()), (0.8, east.clone())]);
        let (s, i) = (disjoint(Dependence::Shared), disjoint(Dependence::Independent));
        for (lat, lon) in [(0.5, 0.5), (0.5, 1.5), (0.5, 10.0)] {
            assert!((s.miss_probability(lat, lon) - i.miss_probability(lat, lon)).abs() < 1e-12);
        }
        // On the cell boundary the bilinear coverage gives each campaign a half, so the ground
        // is modelled as searched twice and the arms separate: 0.2 + 0.8 x 0.6^2 = 0.488 against
        // (0.2 + 0.8 x 0.6)^2 = 0.4624. The grain of the raster, not the swaths, decides where
        // this happens, which is why the pair is reported rather than one being preferred here.
        assert!((s.miss_probability(0.5, 1.0) - 0.488).abs() < 1e-12);
        assert!((i.miss_probability(0.5, 1.0) - 0.4624).abs() < 1e-12);
    }

    #[test]
    fn the_marginal_depends_only_on_the_mean_of_rho_under_shared_but_not_independent() {
        // rho is 0 or 0.4 with equal probability, mean 0.2, over two overlapping campaigns.
        let at = |rho, d| with_dependence(rho, d, vec![(0.8, half()), (0.8, half())]).miss_probability(0.5, 0.5);
        for d in [Dependence::Shared, Dependence::Independent] {
            let averaged = 0.5 * at(0.0, d) + 0.5 * at(0.4, d);
            let at_the_mean = at(0.2, d);
            match d {
                // Linear in rho: a broad prior gives the same answer as a point mass at its mean.
                Dependence::Shared => assert!((averaged - at_the_mean).abs() < 1e-12),
                // Not linear: 0.1552 against 0.1296. The brief's mean-only property belongs to
                // the shared model and must not be carried across to this one.
                Dependence::Independent => {
                    assert!((averaged - 0.1552).abs() < 1e-12);
                    assert!((at_the_mean - 0.1296).abs() < 1e-12);
                }
            }
        }
    }

    #[test]
    fn coverage_is_bilinear_between_cell_centres_and_zero_off_the_grid() {
        let r = raster(-1.0, 10.0, 0.5, 2, 2, vec![0, 255, 51, 102]);
        assert_eq!(r.coverage(-0.75, 10.75), 1.0); // centre of the south-east cell
        assert!((r.coverage(-0.25, 10.25) - 0.2).abs() < 1e-12); // centre of the north-west cell
        assert!((r.coverage(-0.5, 10.5) - (0.0 + 1.0 + 0.2 + 0.4) / 4.0).abs() < 1e-12);
        // Beyond the outer cell centres the missing neighbours count as unsearched.
        assert!((r.coverage(-0.75, 11.0) - 0.5).abs() < 1e-12);
        assert_eq!(r.coverage(-2.0, 10.5), 0.0);
        assert_eq!(r.coverage(f64::NAN, 10.5), 0.0);
    }

    #[test]
    fn embedded_layers_match_the_prepare_script() {
        // Areas printed by prepare/build_coverage.py for the committed rasters.
        for (layer, km2) in [
            ("phase2", 120_489.94),
            ("bluefin-2014", 771.37),
            ("phase2-deep-tow", 103_921.877),
            ("phase2-go-phoenix", 14_630.442),
            ("phase2-dhj", 3_164.526),
            ("phase2-auv", 16_164.232),
        ] {
            let r = Raster::decode(LAYERS.iter().find(|(n, _)| *n == layer).unwrap().1).unwrap();
            assert!((r.area_km2() - km2).abs() < 0.01, "{layer}: {} km2", r.area_km2());
        }
    }

    /// An impact sample at (lat, lon); the fields this module ignores are left not given.
    fn impact(lat: f64, lon: f64) -> ImpactView<'static> {
        ImpactView {
            parent: usize::MAX,
            unix_s: f64::NAN,
            latitude_deg: lat,
            longitude_deg: lon,
            velocity_east_mps: f64::NAN,
            velocity_north_mps: f64::NAN,
            velocity_up_mps: f64::NAN,
            flight_path_angle_deg: f64::NAN,
            mass_kg: f64::NAN,
            kinetic_energy_j: f64::NAN,
            vertical_kinetic_energy_j: f64::NAN,
            family: usize::MAX,
            takeover_unix_s: f64::NAN,
            takeover_latitude_deg: f64::NAN,
            takeover_longitude_deg: f64::NAN,
            takeover_altitude_ft: f64::NAN,
            mode: usize::MAX,
            alternative: usize::MAX,
            latents: &[],
        }
    }

    #[test]
    fn impact_hooks_on_searched_ground_far_beyond_and_without_a_position() {
        let s = SeabedSearch::from_params(&toml::from_str(RUN_TOML_PARAMS).unwrap()).unwrap();
        assert_eq!(s.observations(), ["search:phase2-2014-2017", "search:bluefin-2014"]);
        let columns = s.prediction_columns();
        assert_eq!(columns.len(), 4);
        let mut out = vec![0.0; columns.len()];
        // Deep inside the Phase 2 coverage: rho + (1 - rho)(1 - q) = 0.05 + 0.95 x 0.055.
        let inside = impact(-38.0, 89.0);
        assert!((s.impact_log_likelihood(&inside, &[]) - (0.05 + 0.95 * 0.055f64).ln()).abs() < 1e-12);
        s.predict(&inside, &mut out);
        assert_eq!(out[..2], [1.0, 0.0]);
        assert!((out[2] - 0.055).abs() < 1e-12 && (out[3] - 0.10225).abs() < 1e-12);
        // 400 NM beyond the arc, outside every searched area: no information, exactly zero.
        let beyond = impact(-38.0, 80.5);
        assert_eq!(s.impact_log_likelihood(&beyond, &[]), 0.0);
        s.predict(&beyond, &mut out);
        assert_eq!(out, [0.0, 0.0, 1.0, 1.0]);
        // A sample without a position is not computed, not "not searched".
        assert!(s.impact_log_likelihood(&impact(f64::NAN, 89.0), &[]).is_nan());
        s.predict(&impact(-38.0, f64::NAN), &mut out);
        assert!(out.iter().all(|v| v.is_nan()));
    }

    /// The module's parameters in run.toml, so the tests exercise the configured search.
    const RUN_TOML_PARAMS: &str = "undetectable_probability = 0.05\n\
        [[campaigns]]\nname = \"phase2-2014-2017\"\nlayer = \"phase2\"\ndetection_probability = 0.945\n\
        [[campaigns]]\nname = \"bluefin-2014\"\nlayer = \"bluefin-2014\"\ndetection_probability = 0.9\n";

    #[test]
    fn parameters_are_checked() {
        let p = |text: &str| SeabedSearch::from_params(&toml::from_str(text).unwrap());
        let ok = "undetectable_probability = 0.05\n[[campaigns]]\nname = \"phase2\"\nlayer = \"phase2\"\ndetection_probability = 0.945";
        assert_eq!(p(ok).unwrap().campaigns[0].effective_detection, 0.945);
        assert!(p(&ok.replace("layer = \"phase2\"", "layer = \"phase3\"")).is_err());
        assert!(p(&ok.replace("layer = \"phase2\"", "")).is_err());
        // A layer outside git is read by path; it decodes like an embedded one.
        let file = std::env::temp_dir().join(format!("seabed-search-{}.cov", std::process::id()));
        std::fs::write(&file, LAYERS[1].1).unwrap();
        let external = p(&ok.replace("layer = \"phase2\"", &format!("layer_file = {:?}", file.display().to_string())));
        std::fs::remove_file(&file).unwrap();
        assert_eq!(external.unwrap().campaigns[0].raster, Raster::decode(LAYERS[1].1).unwrap());
        assert!(p(&ok.replace("0.945", "1.2")).is_err());
        assert!(p(&ok.replace("name = \"phase2\"", "name = \"phase2/2014\"")).is_err());
        assert!(p(&ok.replace("0.05", "0.0").replace("0.945", "1.0")).is_err());
    }

    /// Distribution check: simulate searches of synthetic wrecks and keep the unfound ones.
    /// Their distribution must equal prior x P(no find | y), normalised: the likelihood is
    /// the probability of the data under the generative model it claims.
    #[test]
    fn unfound_synthetic_wrecks_follow_the_posterior() {
        // Three strips of ground: covered by campaign A only, by A and B, by neither.
        let a = raster(0.0, 0.0, 1.0, 1, 3, vec![255, 255, 0]);
        let b = raster(0.0, 0.0, 1.0, 1, 3, vec![0, 255, 0]);
        let (rho, qa, qb) = (0.1, 0.9, 0.7);
        let s = search(rho, vec![(qa, a), (qb, b)]);
        let mut rng = 0x9E37_79B9_7F4A_7C15_u64;
        let mut uniform = move || {
            rng ^= rng << 13;
            rng ^= rng >> 7;
            rng ^= rng << 17;
            (rng >> 11) as f64 / (1u64 << 53) as f64
        };
        let (n, mut unfound) = (400_000, [0usize; 3]);
        for _ in 0..n {
            let strip = (3.0 * uniform()) as usize; // uniform prior over the strips
            let detectable = uniform() >= rho;
            let found_a = detectable && strip < 2 && uniform() < qa;
            let found_b = detectable && strip == 1 && uniform() < qb;
            if !(found_a || found_b) {
                unfound[strip] += 1;
            }
        }
        let like: Vec<f64> = (0..3).map(|k| s.miss_probability(0.5, k as f64 + 0.5)).collect();
        let total: usize = unfound.iter().sum();
        for k in 0..3 {
            let expected = like[k] / like.iter().sum::<f64>();
            let observed = unfound[k] as f64 / total as f64;
            let sd = (expected * (1.0 - expected) / total as f64).sqrt();
            assert!((observed - expected).abs() < 4.0 * sd, "strip {k}: {observed} vs {expected}");
        }
        // And the evidence: the fraction of synthetic wrecks never found.
        let z = like.iter().sum::<f64>() / 3.0;
        assert!((total as f64 / n as f64 - z).abs() < 4.0 * (z * (1.0 - z) / n as f64).sqrt());
    }
}
