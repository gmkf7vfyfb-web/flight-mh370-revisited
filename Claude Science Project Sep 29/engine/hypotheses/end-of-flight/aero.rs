//! The open-baseline 777-200ER point-mass energy budget: drag polar, drag rise, the named
//! uncertain drag increments, and a coarse thrust/flow model.
//!
//! ## What this is, and what it is not
//!
//! The brief specifies the Poll–Schumann B772 point-mass energy budget. The PS coefficient set
//! itself lives in `pycontrails`' `ps_model` and in the derived scripts that were to be supplied
//! under `data/external/papers/aero/ps_*.py`; **neither is present in this tree and this session
//! had no network access to them.** So what is implemented here is a model of the same *form* —
//! a two-term polar plus a Mach drag rise and named configuration increments, all referenced to
//! the wing area — whose constants are pinned to the PS-derived calibration targets the brief
//! quotes rather than lifted from PS:
//!
//! - clean `(L/D)max` is an **input**, sampled on `ld_max_clean` (default 20.8–21.4 at 174 t,
//!   the PS-derived band in the brief, against Boeing's ~20.7:1 from the Malaysian SIR
//!   Appendix 1.6E driftdown of 0.0034 NM per ft);
//! - the zero-lift coefficient is then *derived*, `c_d0 = (0.5 / (L/D)max)^2 / k`, so the
//!   calibration target cannot drift away from the polar;
//! - `k = 1 / (pi * AR * e)` with the published geometry (wing area 427.8 m^2, span 60.93 m,
//!   so AR = 8.678) and an Oswald efficiency parameter.
//!
//! Replacing this with the real PS coefficients is a one-file change and is listed as an open
//! item in `hypothesis.toml`.
//!
//! ## Provenance of every constant
//!
//! | quantity | value | where it comes from |
//! |---|---|---|
//! | wing area, span | 427.8 m^2, 60.93 m | Boeing 777 published geometry (airport planning / type certificate) |
//! | MMO | 0.87 | type certificate. OpenAP and Poll–Schumann both list 0.89; 0.87 is used |
//! | clean (L/D)max at 174 t | 20.8–21.4 | PS-derived band quoted in the brief; Boeing ~20.7:1 (SIR App. 1.6E) |
//! | Oswald efficiency | 0.80 | assumed, swept as a parameter |
//! | drag rise above M_cc | `k_w (M - M_cc)^4` | Lock's fourth-power law, `k_w` default 20. **EXTRAPOLATED**: the brief calls for the rise to be shaped from NASA Common Research Model data, which is not in this tree. Every model including Boeing's extrapolates beyond M0.87–0.91 |
//! | Mach tuck | `cl_shift_per_mach` | **EXTRAPOLATED**, same reason. Enters as a nose-down trim shift above M_cc, which is how a pitching-moment change appears in a point-mass model |
//! | windmilling increment, per engine | 0.0000–0.0015 | **uncertain parameter, not a constant.** There are no public Trent 892 figures. Ruled by Pete (9 Oct 2026): calibrated so the dual-flame-out (L/D)max, 18.5–21.0 at the band ends, brackets Boeing's 0.0034 NM/ft wings-level driftdown (SIR App. 1.6E) read as energy height (18.9) or altitude only (20.66). The former ESDU 81009/84004/84005-scale band, 0.0020–0.0060, gives 15–18 and is kept as `smoke/glide-esdu.toml`, a labelled sensitivity |
//! | RAT increment | 0.0001–0.0006 | **uncertain parameter**, same reasoning |
//! | speedbrake increment | 0.020–0.045 | **modelling parameter with a declared sensitivity.** Chosen so that the model's idle descent rates sit near the operational figures the brief quotes for sanity-checking. Those figures circulate in mirrored copies of copyrighted manuals, so they are used as a calibration target and **are not cited** |
//! | landing-configuration increment | 0.050–0.090 | **modelling parameter**, same provenance rule. Only reachable with power, see `Configuration` |
//! | per-engine sea-level static thrust | 415,450 N | Trent 892, 93,400 lbf, type certificate |
//! | idle thrust fraction | 0.03–0.10 | assumed, swept |
//! | TSFC | 1.4e-5–1.8e-5 kg/(N s) | assumed, swept. **This is not the core's fuel model.** The core's Boeing-calibrated FPPM tables are not reachable from a hypothesis; core request 3 asks for them |

use serde::Deserialize;

#[cfg(test)]
use super::atmos;

/// Sampled or fixed scalar. A single number is a point value; a pair is a uniform range the
/// module samples and records as a latent, so that "this is a parameter, not a constant" is
/// expressed in the config rather than in a comment.
#[derive(Deserialize, Debug, Clone, Copy, PartialEq)]
#[serde(untagged)]
pub enum Range {
    Fixed(f64),
    Uniform([f64; 2]),
}

impl Range {
    pub fn draw(&self, uniform: &mut dyn FnMut() -> f64) -> f64 {
        match *self {
            Range::Fixed(v) => v,
            Range::Uniform([lo, hi]) => lo + (hi - lo) * uniform(),
        }
    }

    pub fn check(&self, name: &str) -> Result<(), String> {
        match *self {
            Range::Fixed(v) if v.is_finite() => Ok(()),
            Range::Uniform([lo, hi]) if lo.is_finite() && hi.is_finite() && hi >= lo => Ok(()),
            _ => Err(format!("{name}: need a finite value or a finite [lo, hi] with hi >= lo")),
        }
    }
}

/// The aerodynamic parameters of one descent, after sampling.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Aero {
    pub wing_area_m2: f64,
    pub span_m: f64,
    pub oswald: f64,
    /// Clean maximum lift-to-drag ratio; `c_d0` is derived from it.
    pub ld_max_clean: f64,
    pub mach_crest: f64,
    /// Lock's fourth-power coefficient. EXTRAPOLATED above M_cc.
    pub wave_drag_coefficient: f64,
    /// Reduction in the crest Mach per unit lift coefficient above the reference `c_l` of 0.5.
    pub crest_cl_sensitivity: f64,
    /// Nose-down trim shift per unit Mach above the crest (Mach tuck). EXTRAPOLATED.
    pub tuck_cl_per_mach: f64,
    /// Maximum usable lift coefficient, clean. Caps the achievable load factor.
    pub c_l_max_clean: f64,
    pub windmilling_per_engine: f64,
    pub rat_increment: f64,
    pub speedbrake_increment: f64,
    pub landing_configuration_increment: f64,
    pub sea_level_static_thrust_n: f64,
    pub idle_thrust_fraction: f64,
    pub thrust_density_exponent: f64,
    pub tsfc_kg_per_n_s: f64,
    /// Idle fuel flow per engine at sea-level static ISA, kg/s; 0 switches the idle floor off (the
    /// pre-9-Oct burn, kept as the default so earlier runs reproduce). Reference value 0.30 kg/s:
    /// ICAO Aircraft Engine Emissions Databank, Trent 892, UID 2RR027 (data status C), idle mode
    /// (7 % of rated thrust); databank sha256 57a9ff57... as fetched from EASA on 9 Oct 2026.
    pub idle_fuel_flow_sl_kg_s: f64,
    /// Where between the two altitude scalings of that flow this descent sits, 0..1 in log space:
    /// 0 = corrected-flow scaling W_f = W_ref * delta * sqrt(theta) (the low end), 1 = Boeing Fuel Flow
    /// Method 2 form W_f = W_ref * delta / theta^3.8 * exp(-0.2 M^2) (DuBois & Paynter 2006, SAE 2006-01-1987;
    /// the high end). At FL350, M0.80 they give about 0.061 and 0.177 kg/s per engine.
    pub idle_flow_bffm2_weight: f64,
}

impl Aero {
    pub fn aspect_ratio(&self) -> f64 {
        self.span_m * self.span_m / self.wing_area_m2
    }

    /// Induced-drag factor k in `c_d = c_d0 + k c_l^2`.
    pub fn induced_factor(&self) -> f64 {
        1.0 / (std::f64::consts::PI * self.aspect_ratio() * self.oswald)
    }

    /// Zero-lift drag, *derived* from the clean (L/D)max so the calibration target holds exactly:
    /// `(L/D)max = 1 / (2 sqrt(k c_d0))`.
    pub fn c_d0(&self) -> f64 {
        let s = 0.5 / self.ld_max_clean;
        s * s / self.induced_factor()
    }

    /// Lift coefficient at which the clean polar attains (L/D)max.
    #[cfg_attr(not(test), allow(dead_code))] // model surface exercised by this module's tests
    pub fn c_l_at_ld_max(&self) -> f64 {
        (self.c_d0() / self.induced_factor()).sqrt()
    }

    /// The clean (L/D)max the polar actually attains. Equal to `ld_max_clean` by construction;
    /// kept as a function so the identity is a test rather than an assumption.
    #[cfg_attr(not(test), allow(dead_code))] // model surface exercised by this module's tests
    pub fn ld_max(&self) -> f64 {
        0.5 / (self.induced_factor() * self.c_d0()).sqrt()
    }

    /// (L/D)max of a configuration, re-optimising the lift coefficient against its added drag.
    #[cfg_attr(not(test), allow(dead_code))] // model surface exercised by this module's tests
    pub fn ld_max_in(&self, cfg: &Configuration) -> f64 {
        0.5 / (self.induced_factor() * (self.c_d0() + self.configuration_increment(cfg))).sqrt()
    }

    /// Lift coefficient at which a configuration attains its (L/D)max.
    pub fn c_l_at_ld_max_in(&self, cfg: &Configuration) -> f64 {
        ((self.c_d0() + self.configuration_increment(cfg)) / self.induced_factor()).sqrt()
    }

    /// Crest (drag-rise onset) Mach at a lift coefficient.
    pub fn mach_crest_at(&self, c_l: f64) -> f64 {
        self.mach_crest - self.crest_cl_sensitivity * (c_l - 0.5)
    }

    /// Compressibility drag increment. Zero at and below the crest Mach; `k_w (M - M_cc)^4`
    /// above it. **EXTRAPOLATED** above M0.87: no CRM data in this tree.
    pub fn wave_drag(&self, c_l: f64, mach: f64) -> f64 {
        let excess = mach - self.mach_crest_at(c_l);
        if excess <= 0.0 {
            0.0
        } else {
            self.wave_drag_coefficient * excess.powi(4)
        }
    }

    /// True where a Mach is in the extrapolated part of the model, so a descent can report the
    /// time it spent there instead of the fact being lost.
    pub fn is_extrapolated(&self, mach: f64) -> bool {
        mach > self.mach_crest
    }

    /// Nose-down trim shift from Mach tuck, subtracted from the trimmed lift coefficient of a
    /// fixed-trim (no-intervention) descent. EXTRAPOLATED above M0.87.
    pub fn tuck_cl_shift(&self, mach: f64) -> f64 {
        let excess = mach - self.mach_crest;
        if excess <= 0.0 {
            0.0
        } else {
            self.tuck_cl_per_mach * excess
        }
    }

    /// Total drag coefficient of a configuration at a lift coefficient and Mach.
    pub fn c_d(&self, c_l: f64, mach: f64, cfg: &Configuration) -> f64 {
        self.c_d0() + self.induced_factor() * c_l * c_l + self.wave_drag(c_l, mach) + self.configuration_increment(cfg)
    }

    /// The additive, lift-independent part of a configuration's drag.
    pub fn configuration_increment(&self, cfg: &Configuration) -> f64 {
        self.windmilling_per_engine * cfg.engines_windmilling as f64
            + if cfg.rat_deployed { self.rat_increment } else { 0.0 }
            + self.speedbrake_increment * cfg.speedbrake_fraction()
            + if cfg.landing_configuration { self.landing_configuration_increment } else { 0.0 }
    }

    /// Lift-to-drag ratio of a configuration at a lift coefficient and Mach.
    #[cfg_attr(not(test), allow(dead_code))] // model surface exercised by this module's tests
    pub fn lift_to_drag(&self, c_l: f64, mach: f64, cfg: &Configuration) -> f64 {
        c_l / self.c_d(c_l, mach, cfg)
    }

    /// Net thrust, N. A simple density-ratio law on the static rating; coarse by design and
    /// swept through `idle_thrust_fraction` and the rating.
    /// The idle-flow floor for `engines` thrusting engines at a pressure altitude and Mach, kg/s.
    /// Zero when the floor is off. Pete, 9 Oct (architecture ~21:00 UTC): the descent must burn
    /// fuel at its own rate, and the thrust-scaled cruise-table burn understates idle flow.
    pub fn idle_fuel_floor_kg_s(&self, engines: u8, delta: f64, theta: f64, mach: f64) -> f64 {
        if !(self.idle_fuel_flow_sl_kg_s > 0.0) || engines == 0 {
            return 0.0;
        }
        let low = (delta * theta.sqrt()).ln();
        let high = (delta / theta.powf(3.8) * (-0.2 * mach * mach).exp()).ln();
        let w = self.idle_flow_bffm2_weight.clamp(0.0, 1.0);
        engines as f64 * self.idle_fuel_flow_sl_kg_s * ((1.0 - w) * low + w * high).exp()
    }

    pub fn thrust_n(&self, cfg: &Configuration, density_kg_m3: f64, setting: f64) -> f64 {
        if cfg.engines_thrusting == 0 {
            return 0.0;
        }
        let ratio = (density_kg_m3 / 1.225).max(0.0).powf(self.thrust_density_exponent);
        let fraction = setting.clamp(self.idle_thrust_fraction, 1.0);
        cfg.engines_thrusting as f64 * self.sea_level_static_thrust_n * ratio * fraction
    }

    /// Fuel flow, kg/s, from thrust via TSFC. Not the core's calibrated tables: see core request 3.
    pub fn fuel_flow_kg_s(&self, thrust_n: f64) -> f64 {
        (thrust_n * self.tsfc_kg_per_n_s).max(0.0)
    }
}

/// The airframe configuration during one integration step. Propulsion is an evolving state:
/// `engines_thrusting` and `engines_windmilling` are tracked separately, so "fuel remaining" and
/// "power available" never collapse into one flag.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Configuration {
    pub engines_thrusting: u8,
    pub engines_windmilling: u8,
    pub rat_deployed: bool,
    /// 0 = stowed, 1 = full.
    pub speedbrake_eighths: u8,
    pub landing_configuration: bool,
}

impl Configuration {
    /// Clean, both engines running.
    #[cfg_attr(not(test), allow(dead_code))] // model surface exercised by this module's tests
    pub fn powered() -> Self {
        Configuration {
            engines_thrusting: 2,
            engines_windmilling: 0,
            rat_deployed: false,
            speedbrake_eighths: 0,
            landing_configuration: false,
        }
    }

    /// Both engines failed: both windmilling, RAT out.
    pub fn glide() -> Self {
        Configuration {
            engines_thrusting: 0,
            engines_windmilling: 2,
            rat_deployed: true,
            speedbrake_eighths: 0,
            landing_configuration: false,
        }
    }

    pub fn speedbrake_fraction(&self) -> f64 {
        f64::from(self.speedbrake_eighths.min(8)) / 8.0
    }

    /// Flaps and gear need hydraulic and electrical power the RAT alone does not give: on RAT
    /// power the flaps do not respond to the handle. A landing configuration is therefore only
    /// reachable with an engine thrusting (the APU case is a deferred refinement, recorded in
    /// `hypothesis.toml`).
    pub fn can_reach_landing_configuration(&self) -> bool {
        self.engines_thrusting > 0
    }
}

#[cfg(test)]
pub(super) mod tests {
    use super::*;

    pub fn reference() -> Aero {
        Aero {
            wing_area_m2: 427.8,
            span_m: 60.93,
            oswald: 0.80,
            ld_max_clean: 21.1,
            mach_crest: 0.87,
            wave_drag_coefficient: 20.0,
            crest_cl_sensitivity: 0.10,
            tuck_cl_per_mach: 0.30,
            c_l_max_clean: 1.30,
            windmilling_per_engine: 0.0040,
            rat_increment: 0.000_35,
            speedbrake_increment: 0.032,
            landing_configuration_increment: 0.070,
            sea_level_static_thrust_n: 415_450.0,
            idle_thrust_fraction: 0.06,
            thrust_density_exponent: 0.7,
            tsfc_kg_per_n_s: 1.6e-5,
            idle_fuel_flow_sl_kg_s: 0.0,
            idle_flow_bffm2_weight: 0.0,
        }
    }

    /// The idle floor's two scalings at FL350, M0.80 (delta 0.2353, theta 0.7594), and off by default.
    #[test]
    fn idle_floor_brackets_the_two_altitude_scalings() {
        let (d, t, m) = (0.235_33, 0.759_4, 0.80);
        assert_eq!(reference().idle_fuel_floor_kg_s(2, d, t, m), 0.0);
        let lo = Aero { idle_fuel_flow_sl_kg_s: 0.30, idle_flow_bffm2_weight: 0.0, ..reference() };
        let hi = Aero { idle_flow_bffm2_weight: 1.0, ..lo };
        assert!((lo.idle_fuel_floor_kg_s(1, d, t, m) - 0.30 * d * t.sqrt()).abs() < 1e-12);
        assert!((hi.idle_fuel_floor_kg_s(1, d, t, m) - 0.30 * d / t.powf(3.8) * (-0.128f64).exp()).abs() < 1e-12);
        assert!((lo.idle_fuel_floor_kg_s(1, d, t, m) - 0.0615).abs() < 1e-3 && (hi.idle_fuel_floor_kg_s(1, d, t, m) - 0.177).abs() < 2e-3);
        assert!((hi.idle_fuel_floor_kg_s(2, d, t, m) - 2.0 * hi.idle_fuel_floor_kg_s(1, d, t, m)).abs() < 1e-12);
        assert_eq!(hi.idle_fuel_floor_kg_s(0, d, t, m), 0.0);
    }

    /// Hand-computed fixture. AR = 60.93^2 / 427.8 = 3712.4649 / 427.8 = 8.67804;
    /// k = 1/(pi * 8.678039 * 0.80) = 0.04584992; c_d0 = (0.5/21.1)^2 / k = 0.01224719;
    /// c_l at (L/D)max = sqrt(c_d0/k) = 0.5168315.
    #[test]
    fn the_polar_is_pinned_to_the_calibration_target() {
        let a = reference();
        assert!((a.aspect_ratio() - 8.678_039).abs() < 1e-6, "AR {}", a.aspect_ratio());
        assert!((a.induced_factor() - 0.045_849_92).abs() < 1e-8, "k {}", a.induced_factor());
        assert!((a.c_d0() - 0.012_247_19).abs() < 1e-8, "c_d0 {}", a.c_d0());
        assert!((a.c_l_at_ld_max() - 0.516_831_5).abs() < 1e-6, "c_l* {}", a.c_l_at_ld_max());
        // The derived c_d0 reproduces the target exactly, and a numerical maximum of c_l/c_d
        // over the clean polar agrees with the analytic one.
        let clean = Configuration { engines_thrusting: 0, engines_windmilling: 0, rat_deployed: false, speedbrake_eighths: 0, landing_configuration: false };
        let mut best = (0.0, 0.0);
        let mut c_l = 0.05;
        while c_l < 1.2 {
            let ld = a.lift_to_drag(c_l, 0.60, &clean);
            if ld > best.0 {
                best = (ld, c_l);
            }
            c_l += 1e-4;
        }
        assert!((best.0 - 21.1).abs() < 1e-3, "numerical (L/D)max {}", best.0);
        assert!((best.1 - a.c_l_at_ld_max()).abs() < 2e-4, "numerical c_l* {}", best.1);
    }

    /// The default band brackets Boeing's ~20.7:1 driftdown figure from above, as the brief says
    /// it should: the band is 20.8-21.4 and Boeing's value sits just below it.
    #[test]
    fn the_calibration_band_sits_just_above_the_boeing_driftdown_figure() {
        for ld in [20.8, 21.1, 21.4] {
            let a = Aero { ld_max_clean: ld, ..reference() };
            assert!((a.ld_max() - ld).abs() < 1e-9);
            assert!(a.ld_max() > 20.7, "the band must not fall below Boeing's 20.7:1");
        }
    }

    /// Lock's fourth-power law, hand-computed: at c_l = 0.5 the crest is 0.87, and at M0.90 the
    /// increment is 20 * 0.03^4 = 1.62e-5... which is small, so the rise is checked at M0.95
    /// too: 20 * 0.08^4 = 8.192e-4. The rise is zero at and below the crest.
    #[test]
    fn the_drag_rise_follows_the_fourth_power_law_and_is_zero_below_the_crest() {
        let a = reference();
        assert_eq!(a.wave_drag(0.5, 0.87), 0.0);
        assert_eq!(a.wave_drag(0.5, 0.50), 0.0);
        assert!((a.wave_drag(0.5, 0.90) - 20.0 * 0.03f64.powi(4)).abs() < 1e-12);
        assert!((a.wave_drag(0.5, 0.95) - 8.192e-4).abs() < 1e-12);
        // A higher lift coefficient lowers the crest, so the same Mach costs more.
        assert!(a.wave_drag(0.7, 0.90) > a.wave_drag(0.5, 0.90));
        assert!((a.mach_crest_at(0.7) - 0.85).abs() < 1e-12);
        assert!(a.is_extrapolated(0.88) && !a.is_extrapolated(0.86));
        assert_eq!(a.tuck_cl_shift(0.80), 0.0);
        // 0.30 per unit Mach over a 0.03 excess is a 0.009 nose-down shift in trimmed c_l.
        assert!((a.tuck_cl_shift(0.90) - 0.009).abs() < 1e-12, "{}", a.tuck_cl_shift(0.90));
    }

    /// Each named increment enters additively and only when its configuration is set.
    #[test]
    fn the_configuration_increments_are_additive_and_named() {
        let a = reference();
        let clean = Configuration { engines_thrusting: 0, engines_windmilling: 0, rat_deployed: false, speedbrake_eighths: 0, landing_configuration: false };
        assert_eq!(a.configuration_increment(&clean), 0.0);
        let glide = Configuration::glide();
        assert!((a.configuration_increment(&glide) - (2.0 * 0.0040 + 0.000_35)).abs() < 1e-12);
        let braked = Configuration { speedbrake_eighths: 8, ..glide };
        assert!((a.configuration_increment(&braked) - (2.0 * 0.0040 + 0.000_35 + 0.032)).abs() < 1e-12);
        let half = Configuration { speedbrake_eighths: 4, ..glide };
        assert!((a.configuration_increment(&half) - (2.0 * 0.0040 + 0.000_35 + 0.016)).abs() < 1e-12);
        // Arithmetic check at the fixture's (former ESDU-scale) increments: two windmilling engines
        // plus the RAT take the re-optimised (L/D)max from 21.1 to 0.5/sqrt(k (c_d0 + 0.00835)) =
        // 16.270, so a still-air glide from 35,000 ft (5.757 NM) runs 93.7 NM. That band is
        // inconsistent with Boeing's driftdown and is no longer the default (see below).
        assert!((a.ld_max_in(&glide) - 16.270).abs() < 1e-3, "glide (L/D)max {}", a.ld_max_in(&glide));
        let distance_nm = 35_000.0 * atmos::M_PER_FT / atmos::M_PER_NM * a.ld_max_in(&glide);
        assert!((distance_nm - 93.7).abs() < 0.5, "{distance_nm} NM");
        // The former ESDU-scale band (smoke/glide-esdu.toml) runs 85-105 NM.
        for (w, r, lo, hi) in [(0.0020, 0.0001, 104.0, 106.0), (0.0060, 0.0006, 84.0, 86.0)] {
            let b = Aero { windmilling_per_engine: w, rat_increment: r, ..reference() };
            let d = 35_000.0 * atmos::M_PER_FT / atmos::M_PER_NM * b.ld_max_in(&glide);
            assert!(d > lo && d < hi, "{w}/{r}: {d} NM");
        }
        // The default band, calibrated to Boeing's 0.0034 NM/ft dual-flame-out driftdown (SIR App.
        // 1.6E): the band ends give (L/D)max 21.01 and 18.55, bracketing Boeing read as altitude only
        // (20.66) and as energy height (120 NM over 35,000 ft plus the 3,623 ft kinetic term: 18.88).
        let ends: Vec<f64> = [(0.0, 0.0001), (0.0015, 0.0006)].iter()
            .map(|&(w, r)| Aero { windmilling_per_engine: w, rat_increment: r, ..reference() }.ld_max_in(&glide))
            .collect();
        assert!((ends[0] - 21.014).abs() < 2e-3 && (ends[1] - 18.549).abs() < 2e-3, "{ends:?}");
        assert!(ends[1] < 18.88 && 20.66 < ends[0]);
        let d = |ld: f64| 35_000.0 * atmos::M_PER_FT / atmos::M_PER_NM * ld;
        assert!((d(ends[1]) - 106.85).abs() < 0.1 && (d(ends[0]) - 121.05).abs() < 0.1);
        // A landing configuration is unreachable with no engine thrusting.
        assert!(!glide.can_reach_landing_configuration());
        assert!(Configuration::powered().can_reach_landing_configuration());
    }

    /// Thrust is zero with no engine thrusting, scales with the engine count, and falls with
    /// density; the flow follows TSFC.
    #[test]
    fn thrust_and_flow_behave() {
        let a = reference();
        assert_eq!(a.thrust_n(&Configuration::glide(), 0.38, 1.0), 0.0);
        let two = a.thrust_n(&Configuration::powered(), 1.225, 1.0);
        assert!((two - 2.0 * 415_450.0).abs() < 1e-6, "{two}");
        let one = a.thrust_n(&Configuration { engines_thrusting: 1, ..Configuration::powered() }, 1.225, 1.0);
        assert!((one - 415_450.0).abs() < 1e-6);
        let high = a.thrust_n(&Configuration::powered(), 0.3796, 1.0);
        assert!(high < two && high > 0.0, "{high}");
        // The idle floor applies: a setting below idle still gives idle thrust.
        let idle = a.thrust_n(&Configuration::powered(), 1.225, 0.0);
        assert!((idle - 2.0 * 415_450.0 * 0.06).abs() < 1e-6, "{idle}");
        assert!((a.fuel_flow_kg_s(100_000.0) - 1.6).abs() < 1e-12);
    }

    #[test]
    fn a_range_draws_within_itself_and_rejects_nonsense() {
        let r = Range::Uniform([2.0, 6.0]);
        assert_eq!(r.draw(&mut || 0.25), 3.0);
        assert_eq!(Range::Fixed(7.0).draw(&mut || 0.9), 7.0);
        assert!(r.check("r").is_ok());
        assert!(Range::Uniform([6.0, 2.0]).check("bad").is_err());
        assert!(Range::Fixed(f64::NAN).check("bad").is_err());
    }
}
