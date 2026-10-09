//! The drift side of the shared transport boundary: builds the forcing and coastline the run
//! declares, calls `ocean::integrate`, and reduces each track to a fate. Nothing here advects,
//! interpolates a field or reads a product beyond `GridField::load`; that is the shared crate's.
//!
//! One provisional reading, declared: until the real coastline exists (ocean transport
//! deliverable 6), a `FieldGap::Land` event - stranding in a product's land mask - is read as a
//! beaching at the event's position, without chainage (`land_gap_is_beaching`). Every other
//! non-beaching end (left the domain, outside the time axis, non-finite, released on land) is
//! model error: it stays in the release count and is reported as a fraction, never dropped.

use ocean::{
    analytic::Uniform, integrate, Coastline, Component, Diffusion, Domain, Event, FieldGap, Forcing, GridField, NoCoast, ObjectResponse,
    OceanErrorModel, Particle, Refloat, RunSpec, Snapshot, StraightCoast, VectorField,
};
use serde::Deserialize;
use std::path::Path;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Fate {
    Afloat,
    Beached { t: f64, at: [f64; 2], line: Option<u32>, chainage_km: f64 },
    /// Left the integration domain: a physical non-arrival at the declared segments, kept in the
    /// release count and reported separately (e.g. east past 120 E along the southern route).
    LeftDomain,
    ReleasedOnLand,
    /// Outside a field's time axis, non-finite, or a non-land field gap.
    ModelError,
}

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields, tag = "kind", rename_all = "kebab-case")]
pub enum TransportParams {
    /// Closed-form fields from `ocean::analytic` and a straight coast: tests and synthetic studies.
    Analytic {
        current_mps: [f64; 2],
        #[serde(default)]
        wind10_mps: Option<[f64; 2]>,
        #[serde(default)]
        stokes_mps: Option<[f64; 2]>,
        /// Straight coast a -> b, [lon, lat]; land to the left when `land_left`.
        coast_a: [f64; 2],
        coast_b: [f64; 2],
        land_left: bool,
    },
    /// Gridded products written by `crates/ocean/prepare/netcdf_to_grid.py`.
    Grid {
        current_manifest: String,
        #[serde(default)]
        wind10_manifest: Option<String>,
        #[serde(default)]
        stokes_manifest: Option<String>,
    },
}

pub struct OceanSetup {
    current: Box<dyn VectorField>,
    wind10: Option<Box<dyn VectorField>>,
    stokes: Option<Box<dyn VectorField>>,
    coast: Box<dyn Coastline>,
    pub domain: Domain,
    pub step_s: f64,
    pub threads: usize,
    pub leeway_absorbs_stokes: bool,
    pub explicit_residual: bool,
    pub land_gap_is_beaching: bool,
    /// Transport-model error, one realisation per integration seed (environment realisation).
    /// Default none; see `[ocean_error]` in the run config.
    pub ocean_error: OceanErrorModel,
}

/// A `.series.json` manifest is a multi-file time series (`GridField::load_series`, which joins
/// file seams); any other manifest is one grid file (`GridField::load`).
fn load(path: &str) -> Result<Box<dyn VectorField>, String> {
    let p = Path::new(path);
    let f = if path.ends_with(".series.json") { GridField::load_series(p) } else { GridField::load(p) };
    Ok(Box::new(f.map_err(|e| format!("debris-drift: {e}"))?))
}

impl OceanSetup {
    #[allow(clippy::too_many_arguments)]
    pub fn new(p: &TransportParams, domain: Domain, step_s: f64, threads: usize, leeway_absorbs_stokes: bool, explicit_residual: bool, land_gap_is_beaching: bool) -> Result<Self, String> {
        let (current, wind10, stokes, coast): (Box<dyn VectorField>, Option<Box<dyn VectorField>>, Option<Box<dyn VectorField>>, Box<dyn Coastline>) = match p {
            TransportParams::Analytic { current_mps, wind10_mps, stokes_mps, coast_a, coast_b, land_left } => (
                Box::new(Uniform::current(current_mps[0], current_mps[1])),
                wind10_mps.map(|w| Box::new(Uniform::new(Component::Wind10m, w[0], w[1])) as Box<dyn VectorField>),
                stokes_mps.map(|s| Box::new(Uniform::new(Component::StokesDrift, s[0], s[1])) as Box<dyn VectorField>),
                Box::new(StraightCoast { a: *coast_a, b: *coast_b, segments: 1, first_id: 0, land_left: *land_left, line: 0 }),
            ),
            TransportParams::Grid { current_manifest, wind10_manifest, stokes_manifest } => (
                load(current_manifest)?,
                wind10_manifest.as_deref().map(load).transpose()?,
                stokes_manifest.as_deref().map(load).transpose()?,
                Box::new(NoCoast),
            ),
        };
        Ok(OceanSetup { current, wind10, stokes, coast, domain, step_s, threads, leeway_absorbs_stokes, explicit_residual, land_gap_is_beaching, ocean_error: OceanErrorModel::none() })
    }

    fn forcing(&self) -> Forcing<'_> {
        Forcing { current: self.current.as_ref(), stokes: self.stokes.as_deref(), wind10: self.wind10.as_deref() }
    }

    /// The value of the `ocean-model` alternative for this setup.
    pub fn ocean_model(&self) -> String {
        self.forcing().ocean_model()
    }

    /// Integrate to `end_time` through one ocean realisation (`seed`, `diffusion`). Returns one
    /// fate per particle and the number of integrator steps taken.
    pub fn run(&self, particles: &[Particle], seed: u64, diffusion: Diffusion, end_time: f64) -> Result<(Vec<Fate>, f64), String> {
        let (fates, _, steps) = self.run_tracks(particles, seed, diffusion, &[end_time])?;
        Ok((fates, steps))
    }

    /// As [`run`](Self::run), with the afloat position of every particle at each of `output_times`
    /// (ascending; the run ends at the last). `None` where the particle was not afloat.
    pub fn run_tracks(&self, particles: &[Particle], seed: u64, diffusion: Diffusion, output_times: &[f64]) -> Result<(Vec<Fate>, Vec<Vec<Option<[f64; 2]>>>, f64), String> {
        let end_time = *output_times.last().ok_or("debris-drift: no output times")?;
        let spec = RunSpec {
            forcing: self.forcing(),
            coast: self.coast.as_ref(),
            domain: self.domain,
            step_s: self.step_s,
            output_times: output_times.to_vec(),
            diffusion,
            ocean_error: self.ocean_error,
            refloat: Refloat::Off,
            seed,
            leeway_absorbs_stokes: self.leeway_absorbs_stokes,
            accept_partial_stokes_overlap: false,
            explicit_residual: self.explicit_residual,
            threads: self.threads,
        };
        let out = integrate(&spec, particles).map_err(|e| format!("debris-drift: transport refused the composition: {e:?}"))?;
        let positions: Vec<Vec<Option<[f64; 2]>>> = if output_times.len() > 1 {
            out.tracks.iter().map(|tr| tr.snapshots.iter().map(|s| if let Snapshot::Afloat(at) = s { Some(*at) } else { None }).collect()).collect()
        } else {
            Vec::new()
        };
        let mut steps = 0.0;
        let fates = out
            .tracks
            .iter()
            .zip(particles)
            .map(|(tr, p)| {
                let mut fate = Fate::Afloat;
                let mut t_end = p.end_time.unwrap_or(end_time).min(end_time);
                for ev in &tr.events {
                    match *ev {
                        Event::Beached { t, at, line, chainage_m, .. } => {
                            fate = Fate::Beached { t, at, line: Some(line), chainage_km: chainage_m / 1000.0 };
                            t_end = t;
                            break;
                        }
                        Event::FieldGap { t, at, gap: FieldGap::Land, .. } if self.land_gap_is_beaching => {
                            fate = Fate::Beached { t, at, line: None, chainage_km: f64::NAN };
                            t_end = t;
                            break;
                        }
                        // A field's extent equals the domain, so an RK2 midpoint just outside it
                        // is the same physical event as leaving the domain.
                        Event::LeftDomain { t, .. } | Event::FieldGap { t, gap: FieldGap::OutsideDomain, .. } => {
                            fate = Fate::LeftDomain;
                            t_end = t;
                            break;
                        }
                        Event::ReleasedOnLand { t, .. } => {
                            fate = Fate::ReleasedOnLand;
                            t_end = t;
                            break;
                        }
                        Event::FieldGap { t, .. } | Event::NonFinitePosition { t } => {
                            fate = Fate::ModelError;
                            t_end = t;
                            break;
                        }
                        Event::Refloated { .. } => {}
                    }
                }
                steps += ((t_end - p.release_time) / self.step_s).max(0.0);
                fate
            })
            .collect();
        Ok((fates, positions, steps))
    }
}

pub fn response(a_stokes: f64, c_wind: f64, leeway_angle_deg: f64, leeway_speed_mps: f64) -> ObjectResponse {
    ObjectResponse { a_stokes, c_wind, leeway_angle_deg, leeway_speed_mps }
}
