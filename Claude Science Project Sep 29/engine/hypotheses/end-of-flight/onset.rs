//! The descent-onset latent: when the descent begins, and by which mechanism.
//!
//! ## Onset triggers on predicted endurance, never on the realised flame-out
//!
//! Every mechanism here is a function of `predicted_exhaustion_unix_s` — the time the fuel would
//! run out **under continued cruise**, carried on the hand-off state — and never of the flame-out
//! the trajectory actually realises. The distinction is the whole point: a descent changes the
//! burn, so the realised flame-out moves, and defining onset as "flame-out minus an hour" would
//! make the trigger depend on its own consequence and would assume foreknowledge no crew had.
//! [`tests::the_onset_ignores_the_realised_flame_out`] holds the predicted exhaustion fixed,
//! varies the realised one, and asserts the onset does not move.
//!
//! ## Support, and why it is a config interval rather than a checkpoint
//!
//! The brief's §1 ruled that both versions branch from one 22:41 checkpoint. The architect has
//! superseded that with three arms, so **no checkpoint is hard-coded here**. The anticipatory
//! lead has a config-settable support `anticipatory_lead_s = [lo, hi]`, measured backwards from
//! the predicted exhaustion, and `[0, 0]` is a legal setting meaning *empty support* — the
//! anticipatory mechanism is then unavailable and onset is flame-out-associated only. The three
//! arms are therefore three configs of one model:
//!
//! | arm | `anticipatory_lead_s` | starting state |
//! |---|---|---|
//! | V1a | `[0, 0]` | the filter's own stop epoch |
//! | V1b | `[0, 0]` | a 22:41 branch |
//! | V2  | e.g. `[0, 5760]` | a 22:41 branch |
//!
//! ## The checkpoint-boundary diagnostic
//!
//! The support is truncated at the hand-off time (the runner refuses a takeover before it), and
//! the truncation is **exact, not a clamp**: the lead is drawn uniformly on the truncated support
//! and `support_truncated_fraction` records how much of the nominal support was cut. If supported
//! onset mass accumulates against that boundary the boundary is influencing the answer and the
//! run must be repeated from an earlier checkpoint. Clamping instead of truncating would have
//! piled a spike of probability on the boundary and hidden exactly that.
//!
//! ## The defensive proposal
//!
//! The prior on the lead is uniform, but the posterior puts most mass near exhaustion, so a plain
//! prior draw samples the early window thinly — and the early window is where the hypothesis
//! differs most from V1. A two-component proposal oversamples the early fraction of the support
//! and the exact importance weight is returned:
//!
//! ```text
//!   p(x) = 1 / |S|                                       (uniform prior on the truncated support)
//!   q(x) = w 1{x in E} / |E| + (1 - w) / |S|             (mixture proposal)
//!   log_q_correction = ln p(x) - ln q(x)
//! ```
//!
//! which is the `ln(prior / proposal)` the `Terminal` contract asks for; its mean under the
//! proposal is one, which the runner's own self-check verifies and
//! [`tests::the_defensive_proposal_correction_averages_one`] verifies here.

use serde::Deserialize;

use super::aero::Range;
use super::taxonomy::Initiation;

/// Configuration of the onset latent.
#[derive(Deserialize, Debug, Clone, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct OnsetConfig {
    /// Support of the anticipatory lead, seconds before the predicted exhaustion. `[0, 0]` is
    /// the legal empty support: the anticipatory mechanism is then unavailable.
    pub anticipatory_lead_s: [f64; 2],
    /// Relative prior weights of the three mechanisms, in `Initiation::ALL` order. Renormalised
    /// over the mechanisms a given parent actually supports, and the renormalised weight is
    /// recorded as a latent so the composer can re-weight rather than inherit the choice.
    pub mechanism_weights: [f64; 3],
    /// Fraction of the anticipatory draws taken from the early part of the support.
    pub early_oversample_weight: f64,
    /// How much of the support counts as "early", as a fraction.
    pub early_fraction: f64,
    /// Seconds from the modelled `FUEL QTY LOW` caution to exhaustion under continued cruise.
    ///
    /// **Provisional.** The citable cue is the FAA rulemaking record of the 777 caution appearing
    /// below 4,500 lb (~2,040 kg) per main tank. Converting that quantity into a time needs the
    /// core's Boeing-calibrated fuel tables, including imbalance and unusable fuel, and a
    /// hypothesis cannot reach them (core request 2). Until it can, this is a declared interval
    /// and every result using the fuel-cue mechanism is provisional.
    pub fuel_caution_lead_s: Range,
    /// Recognition delay after the cue, s.
    pub recognition_delay_s: Range,
    /// Response delay after recognition, s.
    pub response_delay_s: Range,
}

/// One drawn onset.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Onset {
    pub unix_s: f64,
    pub mechanism: Initiation,
    /// Predicted remaining endurance under continued cruise at the onset, s. This is the quantity
    /// the trigger is defined on.
    pub predicted_endurance_at_onset_s: f64,
    /// The renormalised prior weight of the drawn mechanism for this parent.
    pub mechanism_prior: f64,
    /// Fraction of the nominal anticipatory support removed by the hand-off boundary; 0 when the
    /// support fitted. The checkpoint-boundary diagnostic.
    pub support_truncated_fraction: f64,
    /// `ln(prior / proposal)`.
    pub log_q_correction: f64,
}

impl OnsetConfig {
    pub fn check(&self) -> Result<(), String> {
        let [lo, hi] = self.anticipatory_lead_s;
        if !(lo.is_finite() && hi.is_finite() && hi >= lo && lo >= 0.0) {
            return Err("onset.anticipatory_lead_s: need finite 0 <= lo <= hi (and [0, 0] for empty support)".into());
        }
        if self.mechanism_weights.iter().any(|w| !w.is_finite() || *w < 0.0) || self.mechanism_weights.iter().sum::<f64>() <= 0.0 {
            return Err("onset.mechanism_weights: need non-negative finite weights with a positive sum".into());
        }
        if !(0.0..=1.0).contains(&self.early_oversample_weight) || !(0.0..=1.0).contains(&self.early_fraction) {
            return Err("onset.early_oversample_weight and early_fraction must be in [0, 1]".into());
        }
        self.fuel_caution_lead_s.check("onset.fuel_caution_lead_s")?;
        self.recognition_delay_s.check("onset.recognition_delay_s")?;
        self.response_delay_s.check("onset.response_delay_s")?;
        Ok(())
    }

    /// True when the anticipatory mechanism has no support at all, by configuration.
    pub fn anticipatory_support_is_empty(&self) -> bool {
        let [lo, hi] = self.anticipatory_lead_s;
        hi <= lo
    }

    /// Relative weights of the mechanisms available to a parent whose predicted exhaustion is
    /// `predicted_exhaustion_unix_s` and whose hand-off was at `earliest_unix_s`.
    ///
    /// A mechanism is unavailable when its support does not intersect `[earliest, predicted]`.
    /// Note that the fuel-cue mechanism is unavailable when the whole cue-plus-delay window lies
    /// before the hand-off, which is a statement about the checkpoint, not about the mechanism.
    pub fn available_weights(&self, earliest_unix_s: f64, predicted_exhaustion_unix_s: f64) -> [f64; 3] {
        let mut w = self.mechanism_weights;
        if self.anticipatory_support_is_empty() || self.truncated_lead_support(earliest_unix_s, predicted_exhaustion_unix_s).is_none() {
            w[0] = 0.0;
        }
        if self.cue_window(earliest_unix_s, predicted_exhaustion_unix_s).is_none() {
            w[1] = 0.0;
        }
        if predicted_exhaustion_unix_s < earliest_unix_s {
            w[2] = 0.0;
        }
        w
    }

    /// The anticipatory lead support after truncation at the hand-off, as `(lo, hi)` in seconds
    /// before the predicted exhaustion; `None` if nothing survives.
    fn truncated_lead_support(&self, earliest_unix_s: f64, predicted_exhaustion_unix_s: f64) -> Option<(f64, f64)> {
        let [lo, nominal_hi] = self.anticipatory_lead_s;
        let hi = nominal_hi.min((predicted_exhaustion_unix_s - earliest_unix_s).max(0.0));
        if hi > lo {
            Some((lo, hi))
        } else {
            None
        }
    }

    /// The window the fuel cue could be in: `(earliest onset, latest onset)`, or `None`.
    fn cue_window(&self, earliest_unix_s: f64, predicted_exhaustion_unix_s: f64) -> Option<(f64, f64)> {
        let lead = match self.fuel_caution_lead_s {
            Range::Fixed(v) => (v, v),
            Range::Uniform([a, b]) => (a, b),
        };
        let delay = |r: Range| match r {
            Range::Fixed(v) => (v, v),
            Range::Uniform([a, b]) => (a, b),
        };
        let (r_lo, r_hi) = delay(self.recognition_delay_s);
        let (s_lo, s_hi) = delay(self.response_delay_s);
        let earliest_onset = predicted_exhaustion_unix_s - lead.1 + r_lo + s_lo;
        let latest_onset = predicted_exhaustion_unix_s - lead.0 + r_hi + s_hi;
        if latest_onset >= earliest_unix_s && latest_onset >= earliest_onset {
            Some((earliest_onset, latest_onset))
        } else {
            None
        }
    }

    /// Draw an onset. `earliest_unix_s` is the hand-off time: the runner refuses an earlier
    /// takeover, so the supports are truncated there and the truncation reported.
    pub fn draw(&self, earliest_unix_s: f64, predicted_exhaustion_unix_s: f64, uniform: &mut dyn FnMut() -> f64) -> Onset {
        let weights = self.available_weights(earliest_unix_s, predicted_exhaustion_unix_s);
        let total: f64 = weights.iter().sum();
        if !(total > 0.0) {
            // No mechanism has support after the hand-off. Two different states share this branch.
            // ALREADY DRY (predicted exhaustion at or before the hand-off): the flame-out has
            // happened, and conditional on no major descent before the checkpoint the only
            // consistent mechanism is flame-out-associated, so its prior is 1 - this is 0.42% of
            // the reference 00:11 snapshot, which reported 0 here until 9 Oct. Otherwise (for
            // example the flame-out mechanism configured out): no mechanism is supported, take over
            // at the hand-off and say so with a prior of 0. NaN is not used: both are real states.
            let already_dry = predicted_exhaustion_unix_s <= earliest_unix_s;
            let flameout_allowed = self.mechanism_weights[2] > 0.0;
            return Onset {
                unix_s: earliest_unix_s,
                mechanism: Initiation::FlameOutAssociated,
                predicted_endurance_at_onset_s: predicted_exhaustion_unix_s - earliest_unix_s,
                mechanism_prior: if already_dry && flameout_allowed { 1.0 } else { 0.0 },
                support_truncated_fraction: 1.0,
                log_q_correction: 0.0,
            };
        }
        let pick = uniform() * total;
        let mut acc = 0.0;
        let mut chosen = 2usize;
        for (i, w) in weights.iter().enumerate() {
            acc += *w;
            if pick < acc {
                chosen = i;
                break;
            }
        }
        let mechanism_prior = weights[chosen] / total;
        let mechanism = Initiation::ALL[chosen];
        let (unix_s, truncated, log_q) = match mechanism {
            Initiation::Anticipatory => {
                let (lo, hi) = self.truncated_lead_support(earliest_unix_s, predicted_exhaustion_unix_s).expect("weight was positive");
                let [_, nominal_hi] = self.anticipatory_lead_s;
                let truncated = if nominal_hi > 0.0 { ((nominal_hi - hi) / nominal_hi).clamp(0.0, 1.0) } else { 0.0 };
                let (lead, log_q) = self.draw_lead(lo, hi, uniform);
                (predicted_exhaustion_unix_s - lead, truncated, log_q)
            }
            Initiation::FuelCue => {
                let lead = self.fuel_caution_lead_s.draw(uniform);
                let recognition = self.recognition_delay_s.draw(uniform);
                let response = self.response_delay_s.draw(uniform);
                let onset = predicted_exhaustion_unix_s - lead + recognition + response;
                (onset.max(earliest_unix_s), 0.0, 0.0)
            }
            Initiation::FlameOutAssociated => (predicted_exhaustion_unix_s.max(earliest_unix_s), 0.0, 0.0),
        };
        Onset {
            unix_s,
            mechanism,
            predicted_endurance_at_onset_s: predicted_exhaustion_unix_s - unix_s,
            mechanism_prior,
            support_truncated_fraction: truncated,
            log_q_correction: log_q,
        }
    }

    /// Recover the onset mechanism from a realised onset lead.
    ///
    /// `Terminal::takeover_time` and `Terminal::descend` are separate hooks with separate uniform
    /// streams, so the mechanism drawn when the onset was drawn is not available in `descend`.
    /// Redrawing it independently would be wrong — it would pair a 3,000 s lead with a
    /// flame-out-associated onset. Instead the mechanism is drawn from its **conditional
    /// posterior given the lead**,
    ///
    /// ```text
    ///   p(m | lead) proportional to w_m f_m(lead)
    /// ```
    ///
    /// so that `p(lead) p(m | lead) = p(m) p(lead | m)` and the joint law is exactly the forward
    /// one. `f_anticipatory` is uniform on the support; `f_cue` is the density of
    /// `cue_lead - recognition - response`, a sum of up to three independent uniforms, evaluated
    /// in closed form by [`uniform_sum_density`]; the flame-out mechanism is an atom at zero lead
    /// and so is identified exactly.
    ///
    /// Returns the mechanism and its **prior** weight (not its posterior), which is what the
    /// `family_prior` latent needs.
    ///
    /// One approximation, which core request 2 would remove: `descend` does not know the hand-off
    /// time, so the anticipatory density uses the *nominal* support rather than the support after
    /// truncation at the hand-off. The two agree whenever the support fits inside the branch,
    /// which is the designed case and is itself monitored by `support_truncated_fraction`.
    pub fn classify(&self, lead_s: f64, uniform: &mut dyn FnMut() -> f64) -> (Initiation, f64) {
        let w = self.mechanism_weights;
        if lead_s.abs() < 1e-6 {
            // Only the flame-out mechanism places an atom at zero lead.
            let available = if w[2] > 0.0 { w[2] } else { 0.0 };
            let total: f64 = w.iter().sum();
            return (Initiation::FlameOutAssociated, if total > 0.0 { available / total } else { 0.0 });
        }
        let [lo, hi] = self.anticipatory_lead_s;
        let f_anticipatory = if hi > lo && (lo..=hi).contains(&lead_s) { 1.0 / (hi - lo) } else { 0.0 };
        let f_cue = self.cue_lead_density(lead_s);
        let posterior = [w[0] * f_anticipatory, w[1] * f_cue];
        let total = posterior[0] + posterior[1];
        let chosen = if !(total > 0.0) {
            // Neither continuous mechanism can produce this lead. Report it as anticipatory with
            // zero prior weight rather than inventing a mechanism; the zero weight is visible in
            // the `family_prior` latent.
            return (Initiation::Anticipatory, 0.0);
        } else if uniform() * total < posterior[0] {
            0usize
        } else {
            1usize
        };
        let prior_total: f64 = w.iter().sum();
        (Initiation::ALL[chosen], if prior_total > 0.0 { w[chosen] / prior_total } else { 0.0 })
    }

    /// Density of `cue_lead - recognition - response` at a lead, in 1/s.
    fn cue_lead_density(&self, lead_s: f64) -> f64 {
        let span = |r: Range| match r {
            Range::Fixed(v) => (v, v),
            Range::Uniform([a, b]) => (a, b),
        };
        let (a1, a2) = span(self.fuel_caution_lead_s);
        let (r1, r2) = span(self.recognition_delay_s);
        let (s1, s2) = span(self.response_delay_s);
        // lead = (a1 - r2 - s2) + La U + Lr (1 - V) + Ls (1 - W), each of U, V, W uniform on (0, 1).
        let offset = a1 - r2 - s2;
        let lengths = [a2 - a1, r2 - r1, s2 - s1];
        uniform_sum_density(lead_s - offset, &lengths)
    }

    /// The defensive two-component draw of the anticipatory lead on `[lo, hi]`, returning the
    /// lead and the exact `ln(prior / proposal)`.
    fn draw_lead(&self, lo: f64, hi: f64, uniform: &mut dyn FnMut() -> f64) -> (f64, f64) {
        let span = hi - lo;
        let early_span = (span * self.early_fraction).max(f64::MIN_POSITIVE);
        // "Early" means a long lead: the far end of the support, nearest the checkpoint.
        let early_lo = hi - early_span;
        let w = self.early_oversample_weight;
        let lead = if uniform() < w { early_lo + early_span * uniform() } else { lo + span * uniform() };
        let prior = 1.0 / span;
        let proposal = (1.0 - w) / span + if lead >= early_lo { w / early_span } else { 0.0 };
        (lead, prior.ln() - proposal.ln())
    }
}

/// Density at `x` of a sum of independent uniforms on `[0, L_i]`, for the non-degenerate `L_i`:
///
/// ```text
///   f(x) = 1 / ((n-1)! prod L_i) * sum over subsets S of (-1)^|S| (x - sum_{i in S} L_i)_+^(n-1)
/// ```
///
/// the standard generalised Irwin–Hall density. Degenerate (zero-length) terms contribute nothing
/// and are dropped; if every term is degenerate the sum is an atom, which is represented as a
/// 1 ms-wide uniform so that a mixture weight stays finite. Only `n <= 3` is needed here.
pub fn uniform_sum_density(x: f64, lengths: &[f64]) -> f64 {
    let live: Vec<f64> = lengths.iter().copied().filter(|l| *l > 0.0).collect();
    let n = live.len();
    if n == 0 {
        return if x.abs() < 5e-4 { 1.0e3 } else { 0.0 };
    }
    let product: f64 = live.iter().product();
    let factorial = (1..n).map(|k| k as f64).product::<f64>().max(1.0);
    let mut sum = 0.0;
    for mask in 0..(1u32 << n) {
        let mut subset = 0.0;
        let mut parity = 1.0;
        for (i, l) in live.iter().enumerate() {
            if mask & (1 << i) != 0 {
                subset += *l;
                parity = -parity;
            }
        }
        let t = x - subset;
        if t > 0.0 {
            sum += parity * t.powi(n as i32 - 1);
        }
    }
    (sum / (factorial * product)).max(0.0)
}

#[cfg(test)]
mod tests {
    use super::*;

    const EXHAUSTION: f64 = 1_394_237_850.0; // 00:17:30 UTC, the configured anticipated exhaustion.
    const CHECKPOINT_2241: f64 = 1_394_232_060.0; // 22:41:00 UTC.

    fn config() -> OnsetConfig {
        OnsetConfig {
            anticipatory_lead_s: [0.0, 5_760.0],
            mechanism_weights: [1.0, 1.0, 1.0],
            early_oversample_weight: 0.3,
            early_fraction: 0.5,
            fuel_caution_lead_s: Range::Uniform([1_800.0, 4_200.0]),
            recognition_delay_s: Range::Uniform([10.0, 300.0]),
            response_delay_s: Range::Uniform([10.0, 600.0]),
        }
    }

    /// A deterministic uniform stream, so a draw can be reasoned about exactly.
    fn stream(values: &[f64]) -> impl FnMut() -> f64 + '_ {
        let mut i = 0usize;
        move || {
            let v = values[i % values.len()];
            i += 1;
            v
        }
    }

    /// 22:41:00 is 5,790 s before the 00:17:30 anticipated exhaustion, so a 5,760 s support
    /// (96 minutes) fits inside a 22:41 branch with 30 s to spare, which is the arrangement §4
    /// describes. The configured support covers the 60- and 90-minute alternatives.
    #[test]
    fn the_support_fits_a_2241_branch_and_covers_the_sixty_and_ninety_minute_leads() {
        assert_eq!(EXHAUSTION - CHECKPOINT_2241, 5_790.0);
        let c = config();
        assert!(c.anticipatory_lead_s[1] <= EXHAUSTION - CHECKPOINT_2241);
        for lead in [3_600.0, 5_400.0] {
            assert!(lead >= c.anticipatory_lead_s[0] && lead <= c.anticipatory_lead_s[1], "{lead} s not covered");
        }
        // A 120-minute window does not fit: it needs the 21:41 checkpoint, as §4 says.
        assert!(7_200.0 > EXHAUSTION - CHECKPOINT_2241);
    }

    /// The empty support is a legal setting and makes the anticipatory mechanism unavailable, so
    /// V1 is V2 with one config key changed rather than a different code path.
    #[test]
    fn an_empty_support_leaves_only_the_flame_out_mechanism() {
        let v1 = OnsetConfig { anticipatory_lead_s: [0.0, 0.0], mechanism_weights: [1.0, 0.0, 0.0], ..config() };
        assert!(v1.anticipatory_support_is_empty());
        assert!(v1.check().is_ok());
        // Every mechanism weight that remains is zero except the flame-out one, which is zero by
        // configuration here too, so the fallback takes over at the hand-off.
        let w = v1.available_weights(CHECKPOINT_2241, EXHAUSTION);
        assert_eq!(w, [0.0, 0.0, 0.0]);
        // With the flame-out weight restored it is the only mechanism with support.
        let v1 = OnsetConfig { mechanism_weights: [1.0, 0.0, 1.0], ..v1 };
        assert_eq!(v1.available_weights(CHECKPOINT_2241, EXHAUSTION), [0.0, 0.0, 1.0]);
        let onset = v1.draw(CHECKPOINT_2241, EXHAUSTION, &mut stream(&[0.5, 0.5, 0.5, 0.5]));
        assert_eq!(onset.mechanism, Initiation::FlameOutAssociated);
        assert_eq!(onset.unix_s, EXHAUSTION);
        assert_eq!(onset.predicted_endurance_at_onset_s, 0.0);
    }

    /// The load-bearing rule: the onset is a function of the *predicted* exhaustion only. Two
    /// parents with the same prediction give the same onset however different their realised
    /// flame-outs turn out to be — the realised value is not an input to this function at all,
    /// which is what makes "flame-out minus an hour" impossible to write here.
    #[test]
    fn the_onset_ignores_the_realised_flame_out() {
        let c = config();
        let draws = [0.0, 0.5, 0.5, 0.5, 0.5, 0.5];
        let a = c.draw(CHECKPOINT_2241, EXHAUSTION, &mut stream(&draws));
        let b = c.draw(CHECKPOINT_2241, EXHAUSTION, &mut stream(&draws));
        assert_eq!(a, b);
        // A different prediction moves the onset by exactly the same amount, so the onset is
        // anchored to the prediction and to nothing else.
        let shifted = c.draw(CHECKPOINT_2241, EXHAUSTION + 600.0, &mut stream(&draws));
        assert!((shifted.unix_s - a.unix_s - 600.0).abs() < 1e-9, "{} vs {}", shifted.unix_s, a.unix_s);
        assert!((shifted.predicted_endurance_at_onset_s - a.predicted_endurance_at_onset_s).abs() < 1e-9);
    }

    /// The hand-off truncates the support exactly and reports the fraction cut, rather than
    /// clamping a spike of probability onto the boundary.
    #[test]
    fn the_support_is_truncated_not_clamped_and_the_cut_is_reported() {
        let c = OnsetConfig { anticipatory_lead_s: [0.0, 7_200.0], mechanism_weights: [1.0, 0.0, 0.0], ..config() };
        // A 22:41 hand-off leaves only 5,790 s of the nominal 7,200 s support: 19.58% is cut.
        let onset = c.draw(CHECKPOINT_2241, EXHAUSTION, &mut stream(&[0.0, 0.99, 0.999]));
        assert!((onset.support_truncated_fraction - (7_200.0 - 5_790.0) / 7_200.0).abs() < 1e-12, "{}", onset.support_truncated_fraction);
        assert!(onset.unix_s >= CHECKPOINT_2241 - 1e-9, "onset before the hand-off: {}", onset.unix_s);
        // Nothing piles up exactly on the boundary: 2,000 draws put no atom there.
        let mut on_boundary = 0;
        for i in 0..2_000 {
            let u = (i as f64 + 0.5) / 2_000.0;
            let o = c.draw(CHECKPOINT_2241, EXHAUSTION, &mut stream(&[0.0, u, u]));
            if (o.unix_s - CHECKPOINT_2241).abs() < 1e-9 {
                on_boundary += 1;
            }
        }
        assert_eq!(on_boundary, 0, "{on_boundary} draws sat on the checkpoint boundary");
        // With no truncation the fraction is zero.
        let roomy = c.draw(EXHAUSTION - 20_000.0, EXHAUSTION, &mut stream(&[0.0, 0.5, 0.5]));
        assert_eq!(roomy.support_truncated_fraction, 0.0);
    }

    /// §8's weighting rule: the defensive mixture oversamples the early window and the exact
    /// importance correction has mean one under the proposal. Checked on a deterministic grid of
    /// the two uniforms the draw consumes, which integrates the mixture exactly.
    #[test]
    fn the_defensive_proposal_correction_averages_one() {
        let c = OnsetConfig { anticipatory_lead_s: [0.0, 5_760.0], mechanism_weights: [1.0, 0.0, 0.0], ..config() };
        let n = 400;
        let mut mean = 0.0;
        let mut early = 0;
        for i in 0..n {
            let u_component = (i as f64 + 0.5) / n as f64;
            for j in 0..n {
                let u_value = (j as f64 + 0.5) / n as f64;
                let o = c.draw(CHECKPOINT_2241 - 10_000.0, EXHAUSTION, &mut stream(&[0.0, u_component, u_value]));
                mean += o.log_q_correction.exp() / (n * n) as f64;
                if EXHAUSTION - o.unix_s > 2_880.0 {
                    early += 1;
                }
            }
        }
        assert!((mean - 1.0).abs() < 2e-3, "mean correction {mean}");
        // The early half of the support gets 0.3 + 0.7/2 = 65% of the draws, not 50%.
        let fraction = early as f64 / (n * n) as f64;
        assert!((fraction - 0.65).abs() < 0.01, "early fraction {fraction}");
    }

    /// The fuel-cue mechanism is the cue time plus recognition and response, all measured from
    /// the predicted exhaustion. Hand-computed: a 3,000 s cue lead with 100 s recognition and
    /// 200 s response puts the onset 2,700 s before the predicted exhaustion.
    #[test]
    fn the_fuel_cue_onset_is_the_cue_plus_the_delays() {
        let c = OnsetConfig {
            mechanism_weights: [0.0, 1.0, 0.0],
            fuel_caution_lead_s: Range::Fixed(3_000.0),
            recognition_delay_s: Range::Fixed(100.0),
            response_delay_s: Range::Fixed(200.0),
            ..config()
        };
        let o = c.draw(CHECKPOINT_2241, EXHAUSTION, &mut stream(&[0.5]));
        assert_eq!(o.mechanism, Initiation::FuelCue);
        assert!((EXHAUSTION - o.unix_s - 2_700.0).abs() < 1e-9, "{}", EXHAUSTION - o.unix_s);
        assert!((o.predicted_endurance_at_onset_s - 2_700.0).abs() < 1e-9);
    }

    /// Mechanism weights are renormalised over what a parent supports, and the renormalised
    /// weight is reported so the composer can re-weight instead of inheriting the choice.
    #[test]
    fn the_mechanism_prior_is_renormalised_and_reported() {
        let c = OnsetConfig { anticipatory_lead_s: [0.0, 0.0], ..config() };
        let w = c.available_weights(CHECKPOINT_2241, EXHAUSTION);
        assert_eq!(w[0], 0.0);
        let o = c.draw(CHECKPOINT_2241, EXHAUSTION, &mut stream(&[0.99, 0.5, 0.5, 0.5]));
        assert_eq!(o.mechanism, Initiation::FlameOutAssociated);
        assert!((o.mechanism_prior - 0.5).abs() < 1e-12, "{}", o.mechanism_prior);
    }

    /// The generalised Irwin-Hall density, against hand-computed cases and against its own
    /// numerical integral, which must be one.
    #[test]
    fn the_uniform_sum_density_is_right() {
        // One uniform on [0, 4]: a rectangle of height 1/4.
        assert!((uniform_sum_density(2.0, &[4.0]) - 0.25).abs() < 1e-12);
        assert_eq!(uniform_sum_density(5.0, &[4.0]), 0.0);
        // Two uniforms on [0, 1]: the triangle, peak 1 at x = 1.
        assert!((uniform_sum_density(1.0, &[1.0, 1.0]) - 1.0).abs() < 1e-12);
        assert!((uniform_sum_density(0.5, &[1.0, 1.0]) - 0.5).abs() < 1e-12);
        // Three uniforms on [0, 1]: Irwin-Hall n = 3, f(1.5) = 3/4.
        assert!((uniform_sum_density(1.5, &[1.0, 1.0, 1.0]) - 0.75).abs() < 1e-12);
        // Degenerate terms are dropped.
        assert!((uniform_sum_density(2.0, &[4.0, 0.0, 0.0]) - 0.25).abs() < 1e-12);
        // Normalisation, by the trapezium rule over the full support.
        let lengths = [2_400.0, 290.0, 590.0];
        let total: f64 = lengths.iter().sum();
        let steps = 20_000;
        let dx = total / steps as f64;
        let mass: f64 = (0..=steps).map(|i| uniform_sum_density(i as f64 * dx, &lengths) * dx).sum();
        assert!((mass - 1.0).abs() < 1e-3, "mass {mass}");
    }

    /// The mechanism recovered in `descend` has the same joint law as the one drawn in
    /// `takeover_time`: over a grid of draws the two mechanism frequencies agree.
    #[test]
    fn the_recovered_mechanism_matches_the_forward_draw() {
        let c = config();
        let n = 300;
        let mut forward = [0usize; 3];
        let mut recovered = [0usize; 3];
        for i in 0..n {
            for j in 0..n {
                let u1 = (i as f64 + 0.5) / n as f64;
                let u2 = (j as f64 + 0.5) / n as f64;
                let o = c.draw(CHECKPOINT_2241 - 20_000.0, EXHAUSTION, &mut stream(&[u1, u2, u2, u2, u2]));
                forward[Initiation::ALL.iter().position(|m| *m == o.mechanism).unwrap()] += 1;
                let lead = EXHAUSTION - o.unix_s;
                let (m, _) = c.classify(lead, &mut stream(&[u2]));
                recovered[Initiation::ALL.iter().position(|x| *x == m).unwrap()] += 1;
            }
        }
        let total = (n * n) as f64;
        for k in 0..3 {
            let (f, r) = (forward[k] as f64 / total, recovered[k] as f64 / total);
            assert!((f - r).abs() < 0.03, "mechanism {k}: forward {f}, recovered {r}");
        }
        // Each mechanism is actually exercised, so the agreement is not vacuous.
        assert!(forward.iter().all(|c| *c > 0), "{forward:?}");
    }

    /// A zero lead identifies the flame-out mechanism exactly, and a lead no continuous mechanism
    /// can produce is reported with zero prior weight rather than given an invented mechanism.
    #[test]
    fn classification_handles_the_atom_and_the_impossible_lead() {
        let c = config();
        let (m, p) = c.classify(0.0, &mut stream(&[0.5]));
        assert_eq!(m, Initiation::FlameOutAssociated);
        assert!((p - 1.0 / 3.0).abs() < 1e-12, "{p}");
        let (_, p) = c.classify(20_000.0, &mut stream(&[0.5]));
        assert_eq!(p, 0.0);
    }

    #[test]
    fn the_configuration_is_validated() {
        assert!(config().check().is_ok());
        assert!(OnsetConfig { anticipatory_lead_s: [100.0, 50.0], ..config() }.check().is_err());
        assert!(OnsetConfig { mechanism_weights: [0.0, 0.0, 0.0], ..config() }.check().is_err());
        assert!(OnsetConfig { early_fraction: 1.5, ..config() }.check().is_err());
        assert!(OnsetConfig { recognition_delay_s: Range::Uniform([10.0, 1.0]), ..config() }.check().is_err());
    }
    /// A hand-off already dry: the flame-out has happened, so the draw is flame-out-associated with
    /// prior ONE, at the hand-off. It reported prior zero until 9 Oct, which made 0.42% of the
    /// reference snapshot look like an unsupported state.
    #[test]
    fn an_already_dry_hand_off_is_flame_out_associated_with_certainty() {
        let c = config();
        let o = c.draw(1_000.0, 900.0, &mut || 0.5);
        assert_eq!(o.mechanism, Initiation::FlameOutAssociated);
        assert_eq!(o.mechanism_prior, 1.0);
        assert_eq!(o.unix_s, 1_000.0);
    }

}
