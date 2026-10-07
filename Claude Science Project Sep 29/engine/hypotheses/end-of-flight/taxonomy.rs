//! The descent taxonomy: a three-axis decomposition, not a flat family list.
//!
//! A flat list ("glide, ditching, spiral, dive") conflates three independent questions, and the
//! conflation is what makes results hard to read: "ditching" mixes a control objective with an
//! outcome, and "spiral" mixes a propulsion state with a control state. The three axes are:
//!
//! 1. **[`Initiation`]** — what started the descent. The three mechanisms are an anticipatory
//!    plan triggered on *predicted remaining endurance under continued cruise*, a response to a
//!    modelled low-fuel cue with recognition and response delay, and an onset associated with
//!    the flame-out itself.
//! 2. **[`Propulsion`]** — how many engines are producing thrust at onset: two, one or neither.
//!    Kept separate from fuel remaining throughout: fuel can be present but inaccessible,
//!    isolated, or unavailable to a particular engine.
//! 3. **[`Control`]** — what happens after onset: control maintained through an attempted
//!    ditching; control maintained and then lost; no effective intervention; or an upset
//!    followed by recovery.
//!
//! ## Onset is never defined from the realised flame-out
//!
//! "Flame-out minus an hour" is circular: it assumes foreknowledge no crew had, and it makes the
//! trigger depend on the very quantity the descent changes. Every mechanism here triggers on the
//! **predicted** exhaustion time under continued cruise, carried on the hand-off state. The
//! realised flame-out then emerges from the trajectory, and the two differ — that difference is
//! recorded as a latent rather than assumed away. See `onset.rs`.
//!
//! ## Mapping the project's own vocabulary onto the axes
//!
//! The words used in discussion are not axes; each is a projection of one or two of them, and
//! two of the five are *outcomes measured on the impact state*, not families to be sampled:
//!
//! - **"controlled"** — a [`Control`] value, either [`Control::DitchingAttempt`] or the
//!   maintained phase of [`Control::MaintainedThenLost`]. It says nothing about propulsion: a
//!   controlled glide and a controlled powered descent are the same control state with different
//!   [`Propulsion`].
//! - **"uncontrolled"** — [`Control::NoIntervention`], and the post-loss phase of
//!   [`Control::MaintainedThenLost`].
//! - **"arrested"** — an **outcome**, not a family: a low vertical speed at water contact. It is
//!   read off the impact state (the `impact_vertical_speed_mps` latent) by applying a threshold
//!   downstream, never asserted by choosing a family. This matters because defining a
//!   "controlled ditching" family by a successful low vertical speed silently discards every
//!   failed attempt, and the failed attempts are exactly the population the hypothesis has to be
//!   tested against. Hence [`Control::DitchingAttempt`] names the *objective*; whether contact
//!   was arrested is measured.
//! - **"unarrested"** — the complementary outcome: a high vertical speed at contact, which
//!   [`Control::NoIntervention`] usually but not always produces.
//! - **"phugoid"** — a *dynamic behaviour* of the integrator under fixed trim, not a family. It
//!   is what [`Control::NoIntervention`] exhibits when residual bank is small; with larger
//!   residual bank the same equations give the descending spiral. Neither is enumerated: both
//!   are integrated.
//!
//! ## Legality
//!
//! Not every cell of the 3 x 3 x 4 grid is meaningful, and the illegal ones are excluded rather
//! than given zero prior, so that `families()` is the list the composer reports over:
//!
//! - [`Initiation::FlameOutAssociated`] requires [`Propulsion::NeitherThrusting`] — that is what
//!   the mechanism means.
//! - [`Initiation::FuelCue`] requires at least one engine thrusting at onset: the `FUEL QTY LOW`
//!   caution necessarily precedes exhaustion, so a cue response begins with thrust available.
//!
//! That leaves 24 of 36 cells. [`Control::UpsetThenRecovery`] is legal in every cell it appears
//! in, but it must be **dynamically demonstrated** — the integrator has to show the recovery with
//! the altitude it actually had. A descent that fails the demonstration is relabelled
//! [`Control::MaintainedThenLost`] and records why; see `profile.rs`.

/// What started the descent. Every variant triggers on predicted endurance, never on the
/// realised flame-out.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum Initiation {
    /// Onset when estimated remaining endurance under continued cruise falls below a sampled
    /// threshold. The threshold's support is config-settable and may be empty.
    Anticipatory,
    /// Onset at a modelled low-fuel cue, plus sampled recognition and response delays.
    FuelCue,
    /// Onset associated with the flame-out itself.
    FlameOutAssociated,
}

/// Engines producing thrust at onset. An evolving state, not a label: the integrator moves it as
/// fuel is exhausted, and "fuel remaining" never implies "power available".
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum Propulsion {
    TwoThrusting,
    OneThrusting,
    NeitherThrusting,
}

/// What happens to control after onset.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum Control {
    /// Control maintained through an attempted ditching. The *objective*: whether contact was
    /// arrested is measured on the impact state, not assumed by the label.
    DitchingAttempt,
    /// Control maintained for a sampled interval, then lost.
    MaintainedThenLost,
    /// No effective intervention during the terminal descent.
    NoIntervention,
    /// Upset followed by recovery and renewed control. Must be dynamically demonstrated.
    UpsetThenRecovery,
}

impl Initiation {
    pub const ALL: [Initiation; 3] = [Initiation::Anticipatory, Initiation::FuelCue, Initiation::FlameOutAssociated];

    pub fn label(self) -> &'static str {
        match self {
            Initiation::Anticipatory => "anticipatory",
            Initiation::FuelCue => "fuel-cue",
            Initiation::FlameOutAssociated => "flame-out",
        }
    }

    pub fn code(self) -> f64 {
        match self {
            Initiation::Anticipatory => 0.0,
            Initiation::FuelCue => 1.0,
            Initiation::FlameOutAssociated => 2.0,
        }
    }
}

impl Propulsion {
    pub const ALL: [Propulsion; 3] = [Propulsion::TwoThrusting, Propulsion::OneThrusting, Propulsion::NeitherThrusting];

    pub fn label(self) -> &'static str {
        match self {
            Propulsion::TwoThrusting => "two-thrusting",
            Propulsion::OneThrusting => "one-thrusting",
            Propulsion::NeitherThrusting => "none-thrusting",
        }
    }

    pub fn engines_thrusting(self) -> u8 {
        match self {
            Propulsion::TwoThrusting => 2,
            Propulsion::OneThrusting => 1,
            Propulsion::NeitherThrusting => 0,
        }
    }

    #[cfg_attr(not(test), allow(dead_code))] // the family index carries the axis; the code is a latent convenience
    pub fn code(self) -> f64 {
        f64::from(self.engines_thrusting())
    }
}

impl Control {
    pub const ALL: [Control; 4] =
        [Control::DitchingAttempt, Control::MaintainedThenLost, Control::NoIntervention, Control::UpsetThenRecovery];

    pub fn label(self) -> &'static str {
        match self {
            Control::DitchingAttempt => "ditching-attempt",
            Control::MaintainedThenLost => "maintained-then-lost",
            Control::NoIntervention => "no-intervention",
            Control::UpsetThenRecovery => "upset-then-recovery",
        }
    }

    pub fn code(self) -> f64 {
        match self {
            Control::DitchingAttempt => 0.0,
            Control::MaintainedThenLost => 1.0,
            Control::NoIntervention => 2.0,
            Control::UpsetThenRecovery => 3.0,
        }
    }

    /// True where the project's word "controlled" applies at onset.
    #[cfg_attr(not(test), allow(dead_code))] // model surface exercised by this module's tests
    pub fn is_controlled_at_onset(self) -> bool {
        matches!(self, Control::DitchingAttempt | Control::MaintainedThenLost)
    }
}

/// One cell of the taxonomy: an (initiation, propulsion, control) triple.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct Family {
    pub initiation: Initiation,
    pub propulsion: Propulsion,
    pub control: Control,
}

impl Family {
    /// Whether the triple is meaningful. See the module doc comment for the two rules.
    pub fn is_legal(&self) -> bool {
        match self.initiation {
            Initiation::FlameOutAssociated => self.propulsion == Propulsion::NeitherThrusting,
            Initiation::FuelCue => self.propulsion != Propulsion::NeitherThrusting,
            Initiation::Anticipatory => true,
        }
    }

    pub fn label(&self) -> String {
        format!("{}/{}/{}", self.initiation.label(), self.propulsion.label(), self.control.label())
    }
}

/// Every legal cell, in a fixed order. This is the index space of `Terminal::families` and of
/// the `family` column of `impacts.npy`, so the order must not change without a core review.
pub fn legal_families() -> Vec<Family> {
    let mut out = Vec::new();
    for initiation in Initiation::ALL {
        for propulsion in Propulsion::ALL {
            for control in Control::ALL {
                let f = Family { initiation, propulsion, control };
                if f.is_legal() {
                    out.push(f);
                }
            }
        }
    }
    out
}

/// The index of a family in [`legal_families`], or `None` if the triple is illegal.
pub fn index_of(family: &Family) -> Option<usize> {
    legal_families().iter().position(|f| f == family)
}

#[cfg(test)]
mod tests {
    use super::*;

    /// 3 x 3 x 4 = 36 cells; the two legality rules remove 12, leaving 24. Counted explicitly so
    /// a change to either rule shows up as a changed family count rather than silently.
    #[test]
    fn the_legal_cells_are_twenty_four_of_thirty_six() {
        let all = Initiation::ALL.len() * Propulsion::ALL.len() * Control::ALL.len();
        assert_eq!(all, 36);
        let legal = legal_families();
        assert_eq!(legal.len(), 24);
        // Anticipatory keeps all 12; fuel-cue keeps 8 (two propulsion states); flame-out keeps 4.
        let count = |i: Initiation| legal.iter().filter(|f| f.initiation == i).count();
        assert_eq!((count(Initiation::Anticipatory), count(Initiation::FuelCue), count(Initiation::FlameOutAssociated)), (12, 8, 4));
    }

    /// A flame-out-associated onset with an engine thrusting, and a cue response with neither
    /// thrusting, are both excluded rather than given zero prior.
    #[test]
    fn the_two_legality_rules_hold() {
        let bad = Family { initiation: Initiation::FlameOutAssociated, propulsion: Propulsion::OneThrusting, control: Control::NoIntervention };
        assert!(!bad.is_legal() && index_of(&bad).is_none());
        let bad = Family { initiation: Initiation::FuelCue, propulsion: Propulsion::NeitherThrusting, control: Control::DitchingAttempt };
        assert!(!bad.is_legal() && index_of(&bad).is_none());
        let good = Family { initiation: Initiation::Anticipatory, propulsion: Propulsion::NeitherThrusting, control: Control::DitchingAttempt };
        assert!(good.is_legal());
    }

    /// Indices are stable, unique, and round-trip through the labels, because the `family`
    /// column of `impacts.npy` is an index into exactly this list.
    #[test]
    fn family_indices_round_trip_and_labels_are_unique() {
        let legal = legal_families();
        for (i, f) in legal.iter().enumerate() {
            assert_eq!(index_of(f), Some(i));
        }
        let mut labels: Vec<String> = legal.iter().map(Family::label).collect();
        labels.sort();
        labels.dedup();
        assert_eq!(labels.len(), legal.len());
        // Column names may not contain `,` `/`... except that `/` is the axis separator chosen
        // here, so the separator is checked explicitly and the other forbidden characters are
        // checked to be absent.
        for label in &labels {
            assert_eq!(label.matches('/').count(), 2, "{label}");
            assert!(!label.contains(',') && !label.contains(':') && !label.contains('\n'), "{label}");
        }
        assert_eq!(legal[0].label(), "anticipatory/two-thrusting/ditching-attempt");
    }

    /// The vocabulary mapping is executable, not just prose: "controlled" is a control-axis
    /// predicate and says nothing about propulsion.
    #[test]
    fn the_vocabulary_maps_onto_the_control_axis_only() {
        assert!(Control::DitchingAttempt.is_controlled_at_onset());
        assert!(Control::MaintainedThenLost.is_controlled_at_onset());
        assert!(!Control::NoIntervention.is_controlled_at_onset());
        // A controlled glide and a controlled powered descent differ only in propulsion.
        let glide = Family { initiation: Initiation::Anticipatory, propulsion: Propulsion::NeitherThrusting, control: Control::DitchingAttempt };
        let powered = Family { propulsion: Propulsion::TwoThrusting, ..glide };
        assert_eq!(glide.control, powered.control);
        assert_ne!(index_of(&glide), index_of(&powered));
    }
}
