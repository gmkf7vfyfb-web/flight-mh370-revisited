//! Closed-form fields behind the same traits as real products. These replace the stubs drift and
//! settling wrote in their own directories. The isotropic random walk of known RMS is not a field:
//! it is `stochastic::Diffusion::RandomWalk`. The straight-line coast is `coast::StraightCoast`.

use crate::field::{Component, FieldGap, FieldMeta, VectorField};
use crate::products::{Contents, TimeAxis};
use crate::profile::{Profile, ProfileSource, Salinity, Temperature, VerticalVelocity};
use crate::{cross, dot, enu_basis, LonLat, EARTH_RADIUS_M};

fn analytic_meta(name: &str, component: Component, description: String) -> FieldMeta {
    FieldMeta {
        product: format!("analytic:{name}"),
        component,
        contents: Contents::analytic(),
        time_axis: TimeAxis::Steady,
        description,
    }
}

/// The same vector everywhere and always. Use for a current, a Stokes drift or a wind.
pub struct Uniform {
    pub value: [f64; 2],
    meta: FieldMeta,
}

impl Uniform {
    pub fn new(component: Component, east: f64, north: f64) -> Self {
        let meta = analytic_meta("uniform", component, format!("uniform ({east}, {north}) m/s"));
        Uniform { value: [east, north], meta }
    }
    pub fn current(east: f64, north: f64) -> Self {
        Self::new(Component::Current, east, north)
    }
    /// Override the declared contents, e.g. to test the double-count refusal.
    pub fn with_contents(mut self, contents: Contents) -> Self {
        self.meta.contents = contents;
        self
    }
}

impl VectorField for Uniform {
    fn sample(&self, _t: f64, _p: LonLat) -> Result<[f64; 2], FieldGap> {
        Ok(self.value)
    }
    fn meta(&self) -> &FieldMeta {
        &self.meta
    }
}

/// Solid-body rotation of the sphere's surface about the axis through `centre`, angular rate
/// `omega` rad/s, positive anticlockwise seen from above the centre. Exact on the sphere: the
/// great-circle distance to the centre is conserved and the period is 2*pi/omega.
pub struct SolidBodyGyre {
    pub centre: LonLat,
    pub omega: f64,
    axis: [f64; 3],
    meta: FieldMeta,
}

impl SolidBodyGyre {
    pub fn new(centre: LonLat, omega: f64) -> Self {
        let meta = analytic_meta(
            "solid-body-gyre",
            Component::Current,
            format!("solid-body gyre about ({}, {}), omega {omega} rad/s", centre[0], centre[1]),
        );
        SolidBodyGyre { centre, omega, axis: enu_basis(centre).0, meta }
    }
}

impl VectorField for SolidBodyGyre {
    fn sample(&self, _t: f64, p: LonLat) -> Result<[f64; 2], FieldGap> {
        let (r, e, n) = enu_basis(p);
        let v = cross(self.axis, r);
        let s = self.omega * EARTH_RADIUS_M;
        Ok([s * dot(v, e), s * dot(v, n)])
    }
    fn meta(&self) -> &FieldMeta {
        &self.meta
    }
}

/// A horizontally uniform, depth-uniform water column for settling's plumbing and tests.
/// `w_up = None` declares the vertical velocity absent; it is then never reported as zero.
pub struct UniformColumn {
    pub u_east: f64,
    pub v_north: f64,
    pub w_up: Option<f64>,
    pub potential_temperature_c: f64,
    pub practical_salinity: f64,
    pub levels_m: Vec<f64>,
    pub model_bottom_m: f64,
    meta: FieldMeta,
}

impl UniformColumn {
    pub fn new(u_east: f64, v_north: f64, w_up: Option<f64>, levels_m: Vec<f64>, model_bottom_m: f64) -> Self {
        let meta = analytic_meta("uniform-column", Component::Current, format!("uniform column ({u_east}, {v_north}) m/s"));
        UniformColumn {
            u_east,
            v_north,
            w_up,
            potential_temperature_c: 2.0,
            practical_salinity: 34.7,
            levels_m,
            model_bottom_m,
            meta,
        }
    }
}

impl ProfileSource for UniformColumn {
    fn profile(&self, _t: f64, p: LonLat) -> Result<Profile, FieldGap> {
        let n = self.levels_m.len();
        Ok(Profile {
            depth_m: self.levels_m.clone(),
            u_east: vec![self.u_east; n],
            v_north: vec![self.v_north; n],
            w_up: match self.w_up {
                Some(w) => VerticalVelocity::Present(vec![w; n]),
                None => VerticalVelocity::Absent,
            },
            temperature: Temperature::Potential(vec![self.potential_temperature_c; n]),
            salinity: Salinity::Practical(vec![self.practical_salinity; n]),
            pressure_dbar: self.levels_m.iter().map(|&z| crate::teos10::pressure_dbar(z, p[1])).collect(),
            model_bottom_m: self.model_bottom_m,
            time_axis: TimeAxis::Steady,
        })
    }
    fn meta(&self) -> &FieldMeta {
        &self.meta
    }
}
