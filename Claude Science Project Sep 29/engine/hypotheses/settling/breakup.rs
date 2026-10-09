//! Element classes and breakup families (breakup.toml): which elements exist and in what state,
//! selected by the impact. The table is the module's only description of the breakup, kept in
//! one place so that it can become the shared breakup field without touching the physics.

use super::physics::Element;
use serde::Deserialize;

/// The families, in the order the selection rule produces them.
pub const FAMILIES: [&str; 3] = ["intact", "broken", "fragmented"];

/// The float/sink cut-off T_c (s): an element that would float longer than this before sinking
/// belongs to the surface-drift branch (its share is `stays_afloat`), not to settling's float
/// phase. Declared, not measured: results/breakup-field-candidate.md section 8 gives the reasons
/// (48 h). A table whose `float_s` range exceeds it is refused on load.
pub const FLOAT_CUTOFF_S: f64 = 48.0 * 3600.0;

#[derive(Clone)]
pub struct Breakup {
    pub classes: Vec<String>,
    pub selection: Selection,
    pub representatives_per_class: usize,
    /// [family][class], families in `FAMILIES` order.
    pub elements: Vec<Vec<Element>>,
}

/// P(family | impact) from the descent speed V_d and the speed V at first contact, both
/// recovered from the specific kinetic energies (V = sqrt(2 KE / m)), with
/// L(x) = 1 / (1 + exp(-x)):
///   P(intact) = L(ln(a / V_d) / s) L(ln(c / V) / s)
///   P(fragmented) = (1 - P(intact)) L(ln(V / b) / s)
///   P(broken) = the rest.
/// Smooth in both inputs (rule 5: no hard thresholds, no floors), and a probability for every
/// impact with a finite speed (the prior's support is covered).
#[derive(Debug, Clone, Copy, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Selection {
    /// a: the descent speed (m/s) at which an otherwise gentle contact is even odds intact.
    pub intact_descent_mps: f64,
    /// c: the speed (m/s) at which a shallow contact is even odds intact.
    pub intact_speed_mps: f64,
    /// b: the speed (m/s) at which a contact that is not intact is even odds fragmented.
    pub fragmented_speed_mps: f64,
    /// s: the width of each transition in ln(speed).
    pub log_width: f64,
}

impl Selection {
    /// From the specific kinetic energies (J/kg): total e and vertical e_v.
    pub fn from_energy(&self, specific_ke_j_kg: f64, specific_vertical_ke_j_kg: f64) -> Option<[f64; 3]> {
        if !(specific_ke_j_kg > 0.0 && specific_vertical_ke_j_kg >= 0.0 && specific_vertical_ke_j_kg <= specific_ke_j_kg * (1.0 + 1e-9)) {
            return None;
        }
        self.probabilities((2.0 * specific_vertical_ke_j_kg).sqrt(), (2.0 * specific_ke_j_kg).sqrt())
    }

    pub fn probabilities(&self, descent_mps: f64, speed_mps: f64) -> Option<[f64; 3]> {
        if !(descent_mps.is_finite() && speed_mps > 0.0 && speed_mps.is_finite()) {
            return None;
        }
        let logistic = |x: f64| 1.0 / (1.0 + (-x).exp());
        // A level contact counts as a descent of 1 cm/s.
        let descent = descent_mps.max(0.01);
        let intact = logistic((self.intact_descent_mps / descent).ln() / self.log_width)
            * logistic((self.intact_speed_mps / speed_mps).ln() / self.log_width);
        let fragmented = (1.0 - intact) * logistic((speed_mps / self.fragmented_speed_mps).ln() / self.log_width);
        Some([intact, 1.0 - intact - fragmented, fragmented])
    }
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Emission {
    representatives_per_class: usize,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Table {
    classes: Vec<String>,
    selection: Selection,
    emission: Emission,
    /// Per class: properties shared by every family.
    class: toml::Table,
    /// Per family and class: the properties that differ from the class's.
    family: toml::Table,
}

/// The occupants element class (architecture ruling 9 Oct ~04:15: settling's, config-gated,
/// default off; evidential only once drift has a 2014 surface-search model). Appended as class
/// `occupants`, its mass taken out of `cabin-contents`. Per-family fates are the declared
/// assumptions; AF447 (broken family) is the one calibration point: 50 of 228 recovered at the
/// surface within days, so stays_afloat >= 0.22 there (a lower bound: not every floating body was
/// recovered). Bodies are not modelled as carried inside sections (see `Implosion`).
#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct OccupantSpec {
    /// Share of impact mass in occupants, removed from cabin contents.
    pub mass_share: f64,
    /// Per family [intact, broken, fragmented].
    pub stays_afloat: [f64; 3],
    pub sinks_at_once: [f64; 3],
    /// Every other `Element` field (physics.rs), shared by the families; `pieces` = people aboard.
    pub element: toml::Table,
}

pub const OCCUPANTS_CLASS: &str = "occupants";

impl Breakup {
    /// Append the occupants class (see `OccupantSpec`).
    pub fn add_occupants(&mut self, spec: &OccupantSpec) -> Result<(), String> {
        if self.classes.iter().any(|c| c == OCCUPANTS_CLASS) {
            return Err("settling: occupants already present".into());
        }
        let cabin = self.classes.iter().position(|c| c == "cabin-contents").ok_or("settling: occupants need a cabin-contents class to take their mass from")?;
        for (f, row) in self.elements.iter_mut().enumerate() {
            let mut t = spec.element.clone();
            t.insert("mass_share".into(), toml::Value::Float(spec.mass_share));
            t.insert("stays_afloat".into(), toml::Value::Float(spec.stays_afloat[f]));
            t.insert("sinks_at_once".into(), toml::Value::Float(spec.sinks_at_once[f]));
            let e: Element = toml::Value::Table(t).try_into().map_err(|e| format!("settling: occupants: {e}"))?;
            e.check().map_err(|e| format!("settling: occupants {}: {e}", FAMILIES[f]))?;
            if e.float_s.hi > FLOAT_CUTOFF_S {
                return Err("settling: occupants float_s beyond the float/sink cut-off".into());
            }
            if row[cabin].mass_share < spec.mass_share {
                return Err(format!("settling: occupants mass share {} exceeds cabin contents' {} in {}", spec.mass_share, row[cabin].mass_share, FAMILIES[f]));
            }
            row[cabin].mass_share -= spec.mass_share;
            row.push(e);
        }
        self.classes.push(OCCUPANTS_CLASS.into());
        Ok(())
    }

    /// Scale every element's `stays_afloat` share by `f` (Pete, 9 Oct: keep the table, vary the
    /// floating share x0.5 and x1.5 as a declared sensitivity). The sinking remainder keeps its
    /// split between sinking at once and floating first. Shares are capped at one.
    pub fn scale_floating_share(&mut self, f: f64) -> Result<(), String> {
        if !(f >= 0.0 && f.is_finite()) {
            return Err("settling: floating_share_scale must be finite and non-negative".into());
        }
        for row in self.elements.iter_mut() {
            for e in row.iter_mut() {
                let afloat = (e.stays_afloat * f).min(1.0);
                let rest = 1.0 - e.stays_afloat;
                e.sinks_at_once = if rest > 0.0 { e.sinks_at_once * (1.0 - afloat) / rest } else { 0.0 };
                e.stays_afloat = afloat;
            }
        }
        Ok(())
    }

    pub fn parse(text: &str) -> Result<Breakup, String> {
        let table: Table = toml::from_str(text).map_err(|e| format!("breakup table: {e}"))?;
        let s = table.selection;
        if ![s.intact_descent_mps, s.intact_speed_mps, s.fragmented_speed_mps, s.log_width].iter().all(|x| *x > 0.0) {
            return Err("breakup table: selection speeds and width must be positive".into());
        }
        if table.emission.representatives_per_class == 0 {
            return Err("breakup table: representatives_per_class must be at least one".into());
        }
        let unknown = |keys: Vec<&String>, known: &[&str], what: &str| match keys.iter().find(|k| !known.contains(&k.as_str())) {
            Some(k) => Err(format!("breakup table: unknown {what} `{k}`")),
            None => Ok(()),
        };
        let classes: Vec<&str> = table.classes.iter().map(String::as_str).collect();
        if classes.iter().enumerate().any(|(i, c)| c.is_empty() || c.contains([',', '/', ':', ' ']) || classes[..i].contains(c)) {
            return Err("breakup table: class names must be unique, non-empty, without spaces , / or :".into());
        }
        unknown(table.class.keys().collect(), &classes, "class")?;
        unknown(table.family.keys().collect(), &FAMILIES, "family")?;
        let mut elements = Vec::new();
        for family in FAMILIES {
            let overrides = match table.family.get(family) {
                Some(toml::Value::Table(t)) => t.clone(),
                None => toml::Table::new(),
                Some(_) => return Err(format!("breakup table: family.{family} must be a table")),
            };
            unknown(overrides.keys().collect(), &classes, &format!("class in family.{family}"))?;
            let mut row = Vec::new();
            for class in &table.classes {
                let mut merged = match table.class.get(class) {
                    Some(toml::Value::Table(t)) => t.clone(),
                    _ => return Err(format!("breakup table: class.{class} is missing")),
                };
                if let Some(toml::Value::Table(t)) = overrides.get(class) {
                    merged.extend(t.clone());
                }
                let element: Element = toml::Value::Table(merged)
                    .try_into()
                    .map_err(|e| format!("breakup table: {family} {class}: {e}"))?;
                element.check().map_err(|e| format!("breakup table: {family} {class}: {e}"))?;
                if element.float_s.hi > FLOAT_CUTOFF_S {
                    return Err(format!("breakup table: {family} {class}: float_s reaches {} s, beyond the float/sink cut-off {FLOAT_CUTOFF_S} s; that share is stays_afloat", element.float_s.hi));
                }
                row.push(element);
            }
            let total: f64 = row.iter().map(|e| e.mass_share).sum();
            if (total - 1.0).abs() > 1e-9 {
                return Err(format!("breakup table: mass shares in family {family} sum to {total}, not one"));
            }
            elements.push(row);
        }
        Ok(Breakup { classes: table.classes, selection: s, representatives_per_class: table.emission.representatives_per_class, elements })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn table() -> Breakup {
        Breakup::parse(include_str!("breakup.toml")).unwrap()
    }

    #[test]
    fn the_table_parses_and_its_shares_close() {
        let b = table();
        assert_eq!(b.classes.len(), 6);
        assert_eq!(b.elements.len(), 3);
    }

    #[test]
    fn the_float_sink_cut_off_is_enforced() {
        let text = include_str!("breakup.toml").replace("float_s = { log_uniform = [600.0, 86400.0] }", "float_s = { log_uniform = [600.0, 200000.0] }");
        assert!(text != include_str!("breakup.toml"));
        match Breakup::parse(&text) {
            Err(e) => assert!(e.contains("cut-off"), "{e}"),
            Ok(_) => panic!("a float_s range beyond the cut-off must be refused"),
        }
    }

    #[test]
    fn family_probabilities_are_a_smooth_partition() {
        let s = table().selection;
        for (vd, v) in [(0.0, 50.0), (3.8, 64.0), (55.0, 78.0), (100.0, 150.0), (250.0, 300.0)] {
            let p = s.probabilities(vd, v).unwrap();
            assert!(p.iter().all(|x| (0.0..=1.0).contains(x)), "{p:?}");
            assert!((p.iter().sum::<f64>() - 1.0).abs() < 1e-12);
        }
        // Energies and speeds agree: e = V^2 / 2.
        let (vd, v) = (55.0, 78.0);
        assert_eq!(s.from_energy(v * v / 2.0, vd * vd / 2.0), s.probabilities(vd, v));
        // Outside the domain: refuse rather than guess.
        assert!(s.from_energy(f64::NAN, 1.0).is_none());
        assert!(s.from_energy(10.0, 20.0).is_none());
    }

    /// Calibration anchors, not independent tests: they show the published numbers in
    /// breakup.toml's comments were transcribed into the rule correctly. Hand calculation for
    /// AF447 (V_d 55, V 78 m/s; a 8, c 100, b 110, s 0.2): P(intact) = L(ln(8/55)/0.2) L(ln(100/78)/0.2)
    /// = L(-9.640) L(1.242) = 6.5e-5 x 0.776 = 5.0e-5; P(fragmented) = (1 - 5.0e-5) L(ln(78/110)/0.2)
    /// = L(-1.719) = 0.1520; P(broken) = 0.8479.
    #[test]
    fn analogue_anchors() {
        let s = table().selection;
        let us1549 = s.probabilities(3.8, 64.0).unwrap();
        let af447 = s.probabilities(55.0, 78.0).unwrap();
        let sr111 = s.probabilities(154.0 * 20f64.to_radians().sin(), 154.0).unwrap();
        assert!((us1549[0] - 0.882).abs() < 0.005, "{us1549:?}");
        assert!((af447[1] - 0.8479).abs() < 5e-4 && (af447[2] - 0.1520).abs() < 5e-4, "{af447:?}");
        assert!((sr111[2] - 0.843).abs() < 0.005, "{sr111:?}");
    }
}
