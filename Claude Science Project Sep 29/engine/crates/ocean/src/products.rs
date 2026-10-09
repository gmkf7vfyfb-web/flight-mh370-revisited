//! Product metadata (brief rule 2 and deliverable 3): for each candidate product, what its
//! "current" already contains, its units, time axis and depth convention, as machine-readable
//! records. A consumer composing velocity components checks [`Contents`] so that no component is
//! counted twice; the integrator does this itself for Stokes drift.
//!
//! Sources are the producers' own documentation, listed per record. Entries marked
//! `Inclusion::Unknown`, and every item in `verify_on_download`, are not yet confirmed against a
//! downloaded file and must be checked when the first file of that product arrives.

use serde::Serialize;

/// Whether a physical contribution is present in a product's velocity.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize)]
pub enum Inclusion {
    Included,
    /// Present but attenuated or partial (e.g. near-inertial motion in a daily mean).
    Partial,
    Excluded,
    /// Not established from the documentation; treated as a possible double count.
    Unknown,
    /// The product is not a current (a wave or wind product).
    NotApplicable,
}

/// What a velocity field already contains.
#[derive(Clone, Debug, PartialEq, Serialize)]
pub struct Contents {
    pub geostrophic: Inclusion,
    pub ekman: Inclusion,
    pub stokes: Inclusion,
    pub tides: Inclusion,
    pub inertial: Inclusion,
    pub note: String,
}

impl Contents {
    /// A closed-form field: contains exactly what its parameters say and nothing else.
    pub fn analytic() -> Self {
        use Inclusion::Excluded as X;
        Contents { geostrophic: X, ekman: X, stokes: X, tides: X, inertial: X, note: "analytic test field".into() }
    }
    /// For wave and wind products, which are not currents.
    pub fn not_a_current(note: &str) -> Self {
        use Inclusion::NotApplicable as N;
        Contents { geostrophic: N, ekman: N, stokes: N, tides: N, inertial: N, note: note.into() }
    }
}

/// How a product samples time.
#[derive(Clone, Debug, PartialEq, Serialize)]
pub enum TimeAxis {
    /// Steady field (analytic).
    Steady,
    /// Means over consecutive intervals of `interval_s`; `stamp` says where in the interval the
    /// file's time label sits. A loader must place each value at its interval centre.
    Mean { interval_s: f64, stamp: String },
    /// Instantaneous values every `interval_s`.
    Instantaneous { interval_s: f64 },
}

#[derive(Clone, Debug, Serialize)]
pub struct Variable {
    pub name: &'static str,
    pub meaning: &'static str,
    pub units: &'static str,
}

/// One candidate product.
#[derive(Clone, Debug, Serialize)]
pub struct ProductMeta {
    /// Value used for the `ocean-model` alternative and in run provenance.
    pub id: &'static str,
    pub name: &'static str,
    pub producer: &'static str,
    pub dataset: &'static str,
    pub access: &'static str,
    /// Name of the configured credential, if access needs one.
    pub credential: Option<&'static str>,
    pub horizontal_resolution_deg: f64,
    pub coverage: &'static str,
    /// Whether coverage spans drift's period, 8 Mar 2014 - 30 Sep 2016.
    pub covers_drift_period: Inclusion,
    pub time_axis: TimeAxis,
    pub depth: &'static str,
    pub variables: Vec<Variable>,
    /// What the velocity contains. `NotApplicable` throughout for wave and wind products.
    pub contents: Contents,
    pub temperature: &'static str,
    pub vertical_velocity: Inclusion,
    pub verify_on_download: Vec<&'static str>,
    pub sources: Vec<&'static str>,
    /// Terms of use as read from the distributor; see results/ocean-references.md.
    pub licence: &'static str,
}

const DAY: f64 = 86_400.0;

/// The five candidate products of the brief, section 4. Native HYCOM is dropped by the brief.
pub fn catalogue() -> Vec<ProductMeta> {
    use Inclusion::*;
    vec![
        ProductMeta {
            id: "glorys12v1",
            name: "GLORYS12V1 global ocean physics reanalysis",
            producer: "Mercator Ocean International for the Copernicus Marine Service",
            dataset: "GLOBAL_MULTIYEAR_PHY_001_030 / cmems_mod_glo_phy_my_0.083deg_P1D-m",
            access: "Copernicus Marine Toolbox subset (server-side box, period, depth, variables)",
            credential: Some("COPERNICUS"),
            horizontal_resolution_deg: 1.0 / 12.0,
            coverage: "1993-01-01 onward (multiyear plus interim); 50 z-levels, 0.494 m to ~5728 m",
            covers_drift_period: Included,
            time_axis: TimeAxis::Mean {
                interval_s: DAY,
                stamp: "daily mean over 00-24 UTC; the 2017 manual says centred at noon, current Toolbox \
                        datasets may label it 00:00 - read the label from the file"
                    .into(),
            },
            depth: "geometric depth, metres, positive down, at T-level centres; top level 0.494 m; \
                    partial bottom cells; sea-floor depth variable deptho in the static dataset",
            variables: vec![
                Variable { name: "uo", meaning: "eastward sea water velocity", units: "m s-1" },
                Variable { name: "vo", meaning: "northward sea water velocity", units: "m s-1" },
                Variable { name: "thetao", meaning: "sea water potential temperature", units: "degC" },
                Variable { name: "so", meaning: "sea water salinity (practical)", units: "1e-3 (PSU)" },
                Variable { name: "zos", meaning: "sea surface height above geoid", units: "m" },
            ],
            contents: Contents {
                geostrophic: Included,
                ekman: Included,
                stokes: Excluded,
                tides: Excluded,
                inertial: Partial,
                note: "NEMO forced by ERA-Interim then ERA5, assimilating along-track SLA, SST, sea ice and \
                       in-situ T/S. Model current at 0.494 m includes the wind-driven (Ekman) response; no \
                       tidal forcing and no wave coupling (no Stokes drift, no Stokes-Coriolis); \
                       near-inertial motion is attenuated, not removed, by daily averaging."
                    .into(),
            },
            temperature: "potential temperature (thetao), degC; convert with TEOS-10 before density",
            vertical_velocity: Excluded,
            verify_on_download: vec![
                "time label position within the daily mean",
                "absence of wo in the multiyear daily dataset",
                "fill value and land mask variable",
            ],
            sources: vec![
                "https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description",
                "CMEMS-GLO-PUM-001-030 (product user manual)",
                "CMEMS-GLO-QUID-001-030 (quality information document)",
            ],
            licence: "Copernicus Marine Service product licence (free use with attribution)",
        },
        ProductMeta {
            id: "waverys",
            name: "WAVERYS global ocean waves reanalysis (MFWAM)",
            producer: "Mercator Ocean International / Meteo-France for the Copernicus Marine Service",
            dataset: "GLOBAL_MULTIYEAR_WAV_001_032 / cmems_mod_glo_wav_my_0.2deg_PT3H-i",
            access: "Copernicus Marine Toolbox subset",
            credential: Some("COPERNICUS"),
            horizontal_resolution_deg: 0.2,
            coverage: "1980 onward (multiyear plus interim)",
            covers_drift_period: Included,
            time_axis: TimeAxis::Instantaneous { interval_s: 3.0 * 3600.0 },
            depth: "surface (Stokes drift at the sea surface)",
            variables: vec![
                Variable { name: "VSDX", meaning: "sea surface Stokes drift, eastward", units: "m s-1" },
                Variable { name: "VSDY", meaning: "sea surface Stokes drift, northward", units: "m s-1" },
            ],
            contents: Contents::not_a_current(
                "Stokes drift of the total wave spectrum at the surface; forced by ERA5 winds and \
                 GLORYS12 currents. Surface Stokes overstates the transport of an object with draught; \
                 a_stokes absorbs that.",
            ),
            temperature: "n/a",
            vertical_velocity: NotApplicable,
            verify_on_download: vec!["VSDX/VSDY variable names and fill value"],
            sources: vec![
                "https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_WAV_001_032/description",
                "CMEMS-GLO-PUM-001-032",
            ],
            licence: "Copernicus Marine Service product licence (free use with attribution)",
        },
        ProductMeta {
            id: "oscar-v2-final",
            name: "OSCAR v2.0 Final 0.25 degree surface currents",
            producer: "Earth & Space Research (ESR), distributed by NASA PO.DAAC",
            dataset: "OSCAR_L4_OC_FINAL_V2.0 (doi:10.5067/OSCAR-25F20)",
            access: "PO.DAAC / Earthdata cloud, daily files oscar_currents_final_YYYYMMDD.nc",
            credential: Some("NASA_EARTHDATA"),
            horizontal_resolution_deg: 0.25,
            coverage: "1993-01-01 onward, final quality level about 1-1.5 years behind real time",
            covers_drift_period: Included,
            time_axis: TimeAxis::Mean { interval_s: DAY, stamp: "daily average; label to be read from the file".into() },
            depth: "average over an assumed well-mixed top 30 m (the geostrophic variables carry depth = 15 m)",
            variables: vec![
                Variable { name: "u", meaning: "total zonal current", units: "m s-1" },
                Variable { name: "v", meaning: "total meridional current", units: "m s-1" },
                Variable { name: "ug", meaning: "zonal geostrophic current", units: "m s-1" },
                Variable { name: "vg", meaning: "meridional geostrophic current", units: "m s-1" },
            ],
            contents: Contents {
                geostrophic: Included,
                ekman: Included,
                stokes: Excluded,
                tides: Excluded,
                inertial: Excluded,
                note: "Diagnostic model: geostrophic (DUACS SSH) + quasi-steady wind-driven (ERA5 stress \
                       with eddy viscosity) + thermal-wind adjustment. The wind-driven term is a 30 m layer \
                       average, so u - ug is the Ekman part; never add a separate Ekman term."
                    .into(),
            },
            temperature: "n/a (surface currents only)",
            vertical_velocity: NotApplicable,
            verify_on_download: vec!["array order (time, longitude, latitude) and longitude 0-360 convention"],
            sources: vec![
                "https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0",
                "OSCAR v2.0 User's Handbook (oscarv2guide.pdf)",
            ],
            licence: "NASA Earthdata open data (not downloaded)",
        },
        globcurrent("globcurrent-my-pt1h", "MULTIOBS_GLO_PHY_MYNRT_015_003 / cmems_obs-mob_glo_phy-cur_my_0.25deg_PT1H-i (v202411)", TimeAxis::Instantaneous { interval_s: 3600.0 }),
        globcurrent(
            "globcurrent-my-p1d",
            "MULTIOBS_GLO_PHY_MYNRT_015_003 / cmems_obs-mob_glo_phy-cur_my_0.25deg_P1D-m (v202411)",
            TimeAxis::Mean { interval_s: DAY, stamp: "daily mean labelled 00:00 UTC of the averaged day (as GLORYS12); placed at label + 12 h, PROVISIONAL".into() },
        ),
        ProductMeta {
            id: "bran2016",
            name: "Bluelink ReANalysis 2016 (OFAM3)",
            producer: "CSIRO Bluelink",
            dataset: "BRAN_2016 daily fields, NCI THREDDS gb6/BRAN/BRAN_2016",
            access: "NCI THREDDS / OPeNDAP, anonymous",
            credential: None,
            horizontal_resolution_deg: 0.1,
            coverage: "January 1994 to August 2016 (CSIRO; NCI catalogue files ocean_u_1994_01 .. ocean_u_2016_08, checked 9 Oct 2026)",
            covers_drift_period: Partial,
            time_axis: TimeAxis::Mean { interval_s: DAY, stamp: "daily mean; label to be read from the file".into() },
            depth: "z* levels of MOM (OFAM3), 5 m resolution near the surface (top cell centre 2.5 m)",
            variables: vec![
                Variable { name: "u", meaning: "eastward velocity", units: "m s-1" },
                Variable { name: "v", meaning: "northward velocity", units: "m s-1" },
                Variable { name: "temp", meaning: "temperature (potential or conservative: verify)", units: "degC" },
                Variable { name: "salt", meaning: "salinity", units: "psu" },
            ],
            contents: Contents {
                geostrophic: Included,
                ekman: Included,
                stokes: Excluded,
                tides: Excluded,
                inertial: Partial,
                note: "OFAM3 (MOM) forced by ERA-Interim 3-hourly fluxes, EnOI assimilation of altimetry, SST \
                       and in-situ T/S. No tides, no wave coupling. Does NOT reach drift's period end \
                       (30 Sep 2016) if the CSIRO end date is right."
                    .into(),
            },
            temperature: "verify on download whether temp is potential or conservative temperature",
            vertical_velocity: Included,
            verify_on_download: vec!["temperature variable definition", "licence eligibility (registration, government-funded research only)"],
            sources: vec![
                "https://research.csiro.au/bluelink/outputs/data-access/",
                "Chamberlain et al. 2021, ESSD 13, 5663 (BRAN2020, compares BRAN2016)",
            ],
            licence: "CSIRO Bluelink terms (gb6_license.txt): registration with CSIRO before access; government-funded research use only; acknowledgement required",
        },
        ProductMeta {
            id: "era5-wind10",
            name: "ERA5 single-level 10 m wind",
            producer: "ECMWF for the Copernicus Climate Change Service",
            dataset: "reanalysis-era5-single-levels: 10m_u_component_of_wind, 10m_v_component_of_wind",
            access: "ARCO-ERA5 public bucket gcp-public-data-arco-era5 (Google Research), anonymous; also the Copernicus Climate Data Store",
            credential: None,
            horizontal_resolution_deg: 0.25,
            coverage: "1940 onward",
            covers_drift_period: Included,
            time_axis: TimeAxis::Instantaneous { interval_s: 3600.0 },
            depth: "10 m above the surface",
            variables: vec![
                Variable { name: "u10", meaning: "10 m eastward wind (actual, not neutral)", units: "m s-1" },
                Variable { name: "v10", meaning: "10 m northward wind (actual, not neutral)", units: "m s-1" },
            ],
            contents: Contents::not_a_current(
                "Wind, used only through the per-object c_wind. u10n/v10n (neutral wind) are a different \
                 variable; a fitted leeway must say which it was fitted against.",
            ),
            temperature: "n/a",
            vertical_velocity: NotApplicable,
            verify_on_download: vec![],
            sources: vec![
                "Hersbach et al. 2020, QJRMS 146, 1999-2049",
                "https://gcp-public-data-arco-era5.storage.googleapis.com/ar/full_37-1h-0p25deg-chunk-1.zarr-v3",
            ],
            licence: "Copernicus (C3S) licence for ERA5, as redistributed in ARCO-ERA5",
        },
    ]
}

/// Copernicus-GlobCurrent, the observation-based second ocean model (multi-year, v202411).
fn globcurrent(id: &'static str, dataset: &'static str, time_axis: TimeAxis) -> ProductMeta {
    use Inclusion::*;
    ProductMeta {
        id,
        name: "Copernicus-GlobCurrent total surface current (geostrophic + Ekman + tide), 0 m",
        producer: "CLS for the Copernicus Marine Service",
        dataset,
        access: "Copernicus Marine Toolbox subset; prepare/fetch_globcurrent.py",
        credential: Some("COPERNICUS"),
        horizontal_resolution_deg: 0.25,
        coverage: "1993 onward (multi-year); 0 m and 15 m; this version is announced for retirement on 2026-11-24",
        covers_drift_period: Included,
        time_axis,
        depth: "surface (0 m) total current; a 15 m level also exists",
        variables: vec![
            Variable { name: "uo", meaning: "eastward total current (geostrophic + Ekman + tide)", units: "m s-1" },
            Variable { name: "vo", meaning: "northward total current", units: "m s-1" },
            Variable { name: "err_uo", meaning: "uncertainty of uo (daily dataset only)", units: "m s-1" },
            Variable { name: "err_vo", meaning: "uncertainty of vo (daily dataset only)", units: "m s-1" },
        ],
        contents: Contents {
            geostrophic: Included,
            ekman: Included,
            stokes: Partial,
            tides: Included,
            inertial: Partial,
            note: "Observation-based and independent of GLORYS12's model: altimetric geostrophy + empirical Ekman \
                   current from ERA5 wind stress + barotropic tide (QUID CMEMS-MOB-QUID-015-003). The Ekman \
                   transfer is fitted to drifters, and whether residual windage or Stokes drift is absorbed is \
                   not stated, so Stokes is declared Partial: an explicit-Stokes composition must opt in. Like \
                   GLORYS12 it already contains the wind-driven current; never add a second Ekman term."
                .into(),
        },
        temperature: "n/a (surface currents only)",
        vertical_velocity: NotApplicable,
        verify_on_download: vec!["time label convention of the daily mean", "land and coastal mask (NaN)"],
        sources: vec![
            "https://data.marine.copernicus.eu/product/MULTIOBS_GLO_PHY_MYNRT_015_003/description",
            "CMEMS-MOB-QUID-015-003 (quality information document)",
        ],
        licence: "Copernicus Marine Service product licence (free use with attribution)",
    }
}

pub fn product(id: &str) -> Option<ProductMeta> {
    catalogue().into_iter().find(|p| p.id == id)
}
