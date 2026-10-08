//! The composer's acceptance tests (composer.md section 3), on synthetic impact samples with
//! known answers. Each fixture has the impacts.npy layout the composer reads: `weight`,
//! `parent`, `mode` (the stratum), `alternative`, `family`, `unix_s`, `latitude_deg`,
//! `longitude_deg`, then module log-likelihood columns named as `mh370 evaluate` names them.

use super::*;
use hypothesis::ImpactView;
use rand::SeedableRng;
use rand_chacha::ChaCha8Rng;
use rand_distr::{Distribution, Normal};

const LN_2PI: f64 = 1.837_877_066_409_345_5;

fn ln_normal(x: f64, mean: f64, sd: f64) -> f64 {
    -0.5 * ((x - mean) / sd).powi(2) - sd.ln() - 0.5 * LN_2PI
}

/// Per-mode evidence with posterior probabilities prior * exp(log_z), normalised. A mode with
/// zero prior is not run: log evidence minus infinity, probability zero.
fn modes(prior: [f64; 5], log_z: [f64; 5]) -> [Mode; 5] {
    let max = (0..5).filter(|&m| prior[m] > 0.0).map(|m| log_z[m]).fold(f64::NEG_INFINITY, f64::max);
    let un: [f64; 5] = std::array::from_fn(|m| if prior[m] > 0.0 { prior[m] * (log_z[m] - max).exp() } else { 0.0 });
    let total: f64 = un.iter().sum();
    std::array::from_fn(|m| Mode {
        prior_weight: prior[m],
        log_evidence: if prior[m] > 0.0 { log_z[m] } else { f64::NEG_INFINITY },
        posterior_probability: un[m] / total,
    })
}

fn one_mode() -> [Mode; 5] {
    modes([1.0, 0.0, 0.0, 0.0, 0.0], [0.0; 5])
}

/// Impact samples built column by column.
struct Fixture {
    columns: Vec<String>,
    rows: Vec<Vec<f64>>,
}

impl Fixture {
    /// Rows with these weights, strata and latitudes; each row its own parent, family 0,
    /// trajectory option 0, longitude 92 E, impact at unix time 0.
    fn new(weight: &[f64], mode: &[usize], lat: &[f64]) -> Self {
        let columns = [WEIGHT, PARENT, STRATUM, TRAJECTORY_OPTION, FAMILY, "unix_s", "latitude_deg", "longitude_deg"];
        let rows = (0..weight.len()).map(|r| vec![weight[r], r as f64, mode[r] as f64, 0.0, 0.0, 0.0, lat[r], 92.0]).collect();
        Fixture { columns: columns.iter().map(|c| c.to_string()).collect(), rows }
    }

    fn set(mut self, name: &str, value: impl Fn(usize, &[f64]) -> f64) -> Self {
        let k = match self.columns.iter().position(|c| c == name) {
            Some(k) => k,
            None => {
                self.columns.push(name.to_string());
                for row in &mut self.rows {
                    row.push(f64::NAN);
                }
                self.columns.len() - 1
            }
        };
        for (r, row) in self.rows.iter_mut().enumerate() {
            row[k] = value(r, &row[..]);
        }
        self
    }

    fn replicate(&self, seed: u64, modes: [Mode; 5]) -> Replicate {
        Replicate { seed, columns: self.columns.clone(), values: self.rows.concat(), modes }
    }
}

fn declaration(name: &str, observations: &[&str], alternatives: Vec<Alternatives>, absolute_scale: bool) -> Declaration {
    Declaration {
        name: name.to_string(),
        prefix: format!("{name}:loglik"),
        observations: observations.iter().map(|o| o.to_string()).collect(),
        alternatives,
        absolute_scale,
    }
}

fn close(a: f64, b: f64, tolerance: f64, what: &str) {
    assert!((a - b).abs() <= tolerance, "{what}: {a} vs {b} (tolerance {tolerance})");
}

fn ungated(id: &str, modules: &[&str]) -> Set {
    Set { ess_floor: 0.0, ..Set::new(id, modules) }
}

// ---------------------------------------------------------------------------------------------
// 1. Analytic composition: a Gaussian factor on a Gaussian prior.
// ---------------------------------------------------------------------------------------------

/// Two strata, each a Gaussian prior in latitude discretised on a fine grid (so sums are the
/// integrals to ~1e-12), scored by one Gaussian measurement y = x + e. Closed forms: per stratum
/// the evidence ratio is N(y; mu, sqrt(s0^2 + s^2)), the posterior is Gaussian with precision
/// 1/s0^2 + 1/s^2, and the strata reweight by P(m) D_m. Then the same on Monte Carlo samples,
/// within four standard errors, and a factor sharp enough to leave the product unconverged.
#[test]
fn analytic_gaussian_factor_on_gaussian_prior() {
    let (y, s) = (-35.0, 0.6);
    let strata = [(0usize, -36.0, 1.5, 0.7), (4usize, -33.0, 0.8, 0.3)];
    let (mut weight, mut mode, mut lat) = (Vec::new(), Vec::new(), Vec::new());
    for &(m, mu, s0, p) in &strata {
        let n = 4001;
        let h = 24.0 * s0 / (n - 1) as f64;
        let x: Vec<f64> = (0..n).map(|k| mu - 12.0 * s0 + k as f64 * h).collect();
        let density: Vec<f64> = x.iter().map(|&x| ln_normal(x, mu, s0).exp()).collect();
        let total: f64 = density.iter().sum();
        weight.extend(density.iter().map(|d| p * d / total));
        mode.extend(std::iter::repeat_n(m, n));
        lat.extend(x);
    }
    let base_modes = modes([0.5, 0.0, 0.0, 0.0, 0.5], [0.7f64.ln(), 0.0, 0.0, 0.0, 0.3f64.ln()]);
    let fixture = Fixture::new(&weight, &mode, &lat).set("gauss:loglik", |_, row| ln_normal(y, row[6], s));
    let samples = vec![fixture.replicate(1, base_modes)];
    let base = Product::filter(&samples, vec![]).unwrap();
    let gauss = declaration("gauss", &["synthetic:y"], vec![], true);
    let product = compose(&base, &samples, &[gauss.clone()], &ungated("core+gauss", &["gauss"]), None).unwrap();

    let mut evidence = 0.0;
    let mut posterior = Vec::new();
    for &(m, mu, s0, p) in &strata {
        let d = ln_normal(y, mu, (s0 * s0 + s * s).sqrt()).exp();
        let precision = 1.0 / (s0 * s0) + 1.0 / (s * s);
        posterior.push((m, p * d, (mu / (s0 * s0) + y / (s * s)) / precision, 1.0 / precision));
        evidence += p * d;
        close(product.replicates[0].log_evidence_increment[m], d.ln(), 1e-9, "ln D per mode");
    }
    let mean: f64 = posterior.iter().map(|(_, pd, mean, _)| pd / evidence * mean).sum();
    let second: f64 = posterior.iter().map(|(_, pd, mean, var)| pd / evidence * (var + mean * mean)).sum();
    for &(m, pd, ..) in &posterior {
        close(product.replicates[0].modes[m].posterior_probability, pd / evidence, 1e-10, "P(mode | D)");
        close(product.replicates[0].modes[m].log_evidence, base_modes[m].log_evidence + (pd / strata.iter().find(|s| s.0 == m).unwrap().3).ln(), 1e-9, "ln Z' per mode");
    }
    close(product.log_evidence_increment, evidence.ln(), 1e-9, "pooled evidence increment");
    let (got_mean, got_sd) = product.moments(&samples, "latitude_deg").unwrap()[0];
    close(got_mean, mean, 1e-9, "posterior mean");
    close(got_sd, (second - mean * mean).sqrt(), 1e-9, "posterior sd");
    assert_eq!(product.contains, [FILTER, "gauss"]);
    assert_eq!(product.columns, ["gauss:loglik"]);

    // Monte Carlo: two replicates of 100,000 prior draws from stratum 0 alone.
    let (mu, s0) = (-36.0, 1.5);
    let draw = |seed: u64| {
        let mut rng = ChaCha8Rng::seed_from_u64(seed);
        let prior = Normal::new(mu, s0).unwrap();
        let n = 100_000;
        let lat: Vec<f64> = (0..n).map(|_| prior.sample(&mut rng)).collect();
        Fixture::new(&vec![1.0 / n as f64; n], &vec![0; n], &lat)
    };
    let fixtures = [draw(11), draw(12)];
    let precision = 1.0 / (s0 * s0) + 1.0 / (s * s);
    let exact_mean = (mu / (s0 * s0) + y / (s * s)) / precision;
    let exact_ln_d = ln_normal(y, mu, (s0 * s0 + s * s).sqrt());
    for (sd, converged) in [(s, true), (0.0005, false)] {
        let samples: Vec<Replicate> = fixtures.iter().enumerate().map(|(i, f)| f.clone_with(|_, row| ln_normal(y, row[6], sd)).replicate(i as u64 + 1, one_mode())).collect();
        let base = Product::filter(&samples, vec![]).unwrap();
        let product = compose(&base, &samples, &[gauss.clone()], &Set::new("core+gauss", &["gauss"]), None).unwrap();
        assert_eq!(product.status == Status::Converged, converged, "status {:?} at sd {sd}, ESS {:?}", product.status, product.ess);
        if !converged {
            continue;
        }
        for (i, (got_mean, got_sd)) in product.moments(&samples, "latitude_deg").unwrap().into_iter().enumerate() {
            let ess = product.ess[i].rows;
            close(got_mean, exact_mean, 4.0 * got_sd / ess.sqrt(), "Monte Carlo posterior mean");
            let w = &product.replicates[i].weights;
            let n = w.len() as f64;
            let se = ((n * w.iter().map(|v| v * v).sum::<f64>() - 1.0) / n).sqrt();
            close(product.replicates[i].log_evidence_increment[0], exact_ln_d, 4.0 * se, "Monte Carlo ln D");
        }
    }
}

impl Fixture {
    fn clone_with(&self, value: impl Fn(usize, &[f64]) -> f64) -> Fixture {
        Fixture { columns: self.columns.clone(), rows: self.rows.clone() }.set("gauss:loglik", value)
    }
}

// ---------------------------------------------------------------------------------------------
// 2. Joint marginalisation of an alternative two modules share by name.
// ---------------------------------------------------------------------------------------------

/// Two equally weighted samples; modules A and B both declare `ocean-model` {m1, m2}, priors
/// 1/2. Likelihoods (r1, r2): A|m1 (1, 0.2), A|m2 (0.2, 0.2), B|m1 (0.5, 0.05), B|m2 (0.1, 0.4).
/// By hand, jointly, per row sum_m P(m) L_A,m L_B,m = (0.5*0.5 + 0.5*0.02, 0.5*0.01 + 0.5*0.08)
/// = (0.26, 0.045). Marginalising each module separately and multiplying gives (0.6*0.3,
/// 0.2*0.225) = (0.18, 0.045): a different and wrong answer.
#[test]
fn shared_alternative_is_marginalised_jointly() {
    let ln = |v: [f64; 2]| move |r: usize, _: &[f64]| v[r].ln();
    let fixture = Fixture::new(&[0.5, 0.5], &[0, 0], &[-35.0, -36.0])
        .set("A:loglik:m1", ln([1.0, 0.2]))
        .set("A:loglik:m2", ln([0.2, 0.2]))
        .set("B:loglik:m1", ln([0.5, 0.05]))
        .set("B:loglik:m2", ln([0.1, 0.4]));
    let samples = vec![fixture.replicate(1, one_mode())];
    let base = Product::filter(&samples, vec![]).unwrap();
    let ocean = |p1: f64| vec![Alternatives::new("ocean-model", &[("m1", p1), ("m2", 1.0 - p1)])];
    let a = declaration("A", &["debris:a"], ocean(0.5), true);
    let b = declaration("B", &["debris:b"], ocean(0.5), true);
    let both = [a.clone(), b.clone()];

    // Joint: rows (0.5*(1*0.5 + 0.2*0.1), 0.5*(0.2*0.05 + 0.2*0.4)) = (0.26, 0.045).
    let product = compose(&base, &samples, &both, &ungated("A+B", &["A", "B"]), None).unwrap();
    let (r1, r2) = (0.26, 0.045);
    let w = &product.replicates[0].weights;
    close(w[0], r1 / (r1 + r2), 1e-12, "joint weight r1");
    close(w[1], r2 / (r1 + r2), 1e-12, "joint weight r2");
    // Z = 0.5*0.26 + 0.5*0.045 = 0.1525; Z_m1 = 0.5*0.5 + 0.5*0.01 = 0.255, Z_m2 = 0.5*0.02 + 0.5*0.08 = 0.05.
    close(product.log_evidence_increment, 0.1525f64.ln(), 1e-12, "joint evidence");
    let report = product.alternatives.iter().find(|x| x.name == "ocean-model").unwrap();
    assert_eq!(report.role, Role::Marginalised);
    assert_eq!(report.declared_by, ["A", "B"]);
    let p = report.posterior.as_ref().unwrap();
    close(p[0], 0.5 * 0.255 / 0.1525, 1e-12, "P(m1 | D)");
    close(p[1], 0.5 * 0.05 / 0.1525, 1e-12, "P(m2 | D)");
    // Separate marginalisation would give rows (0.6*0.3, 0.2*0.225) and evidence 0.5*(0.18+0.045).
    let separate = 0.18 / (0.18 + 0.045);
    assert!((w[0] - separate).abs() > 0.04, "joint {} must differ from separate {separate}", w[0]);
    assert!((product.log_evidence_increment - (0.5f64 * 0.225).ln()).abs() > 0.1);

    // Composing B after A had marginalised ocean-model alone would be the separate answer: refused.
    let after_a = compose(&base, &samples, &both, &ungated("A", &["A"]), None).unwrap();
    let error = compose(&after_a, &samples, &both, &ungated("A then B", &["B"]), None).unwrap_err();
    assert!(error.contains("ocean-model"), "{error}");

    // Conditional on m1: p(x | D, m1) with weights (0.5*0.5, 0.01*0.5)/0.255, labelled, and P(m1 | D) beside it.
    let mut given = ungated("A+B | m1", &["A", "B"]);
    given.given.insert("ocean-model".into(), "m1".into());
    let conditional = compose(&base, &samples, &both, &given, None).unwrap();
    close(conditional.replicates[0].weights[0], 0.25 / 0.255, 1e-12, "conditional weight");
    close(conditional.log_evidence_increment, 0.255f64.ln(), 1e-12, "conditional evidence");
    assert_eq!(conditional.conditional_on.get("ocean-model").map(String::as_str), Some("m1"));
    let report = conditional.alternatives.iter().find(|x| x.name == "ocean-model").unwrap();
    assert_eq!(report.role, Role::Given(0));
    close(report.posterior.as_ref().unwrap()[0], 0.5 * 0.255 / 0.1525, 1e-12, "P(m1 | D) beside the conditional");

    // A relative-scale B may not be mixed across ocean models, only composed within one,
    // and then no posterior probability of the options is reported.
    let relative = [a.clone(), declaration("B", &["debris:b"], ocean(0.5), false)];
    let error = compose(&base, &samples, &relative, &ungated("A+B", &["A", "B"]), None).unwrap_err();
    assert!(error.contains("absolute"), "{error}");
    let within = compose(&base, &samples, &relative, &given, None).unwrap();
    close(within.replicates[0].weights[0], 0.25 / 0.255, 1e-12, "relative scale within one option");
    assert!(within.alternatives.iter().find(|x| x.name == "ocean-model").unwrap().posterior.is_none());

    // The shared name must mean the same options; differing priors need an explicit override.
    let mislabelled = [a.clone(), declaration("B", &["debris:b"], vec![Alternatives::new("ocean-model", &[("m1", 0.5), ("m3", 0.5)])], true)];
    assert!(compose(&base, &samples, &mislabelled, &ungated("A+B", &["A", "B"]), None).is_err());
    let disagreeing = [a, declaration("B", &["debris:b"], ocean(0.4), true)];
    assert!(compose(&base, &samples, &disagreeing, &ungated("A+B", &["A", "B"]), None).is_err());
    let mut overridden = ungated("A+B", &["A", "B"]);
    overridden.priors.insert("ocean-model".into(), vec![0.25, 0.75]);
    let swept = compose(&base, &samples, &disagreeing, &overridden, None).unwrap();
    let p = swept.alternatives.iter().find(|x| x.name == "ocean-model").unwrap().posterior.clone().unwrap();
    close(p[0], 0.25 * 0.255 / (0.25 * 0.255 + 0.75 * 0.05), 1e-12, "P(m1 | D) under the overridden prior");

    // An alternative named like the run's trajectory alternative is followed, not marginalised:
    // r1 flew route p and r2 route q, so the weights are (0.5*1, 0.5*0.4)/0.7, whatever A says
    // about the other route, and no posterior of the routes is reported here.
    let routed = Fixture::new(&[0.5, 0.5], &[0, 0], &[-35.0, -36.0])
        .set(TRAJECTORY_OPTION, |r, _| r as f64)
        .set("A:loglik:p", ln([1.0, 0.01]))
        .set("A:loglik:q", ln([0.01, 0.4]));
    let samples = vec![routed.replicate(1, one_mode())];
    let base = Product::filter(&samples, vec![]).unwrap();
    let route = [declaration("A", &["debris:a"], vec![Alternatives::new("route", &[("p", 0.5), ("q", 0.5)])], true)];
    let followed = compose(&base, &samples, &route, &ungated("A", &["A"]), Some("route")).unwrap();
    close(followed.replicates[0].weights[0], 0.5 / 0.7, 1e-12, "trajectory option followed");
    let report = followed.alternatives.iter().find(|x| x.name == "route").unwrap();
    assert_eq!(report.role, Role::Trajectory);
    assert!(report.posterior.is_none());
    let mut fixed = ungated("A", &["A"]);
    fixed.given.insert("route".into(), "p".into());
    assert!(compose(&base, &samples, &route, &fixed, Some("route")).is_err(), "a trajectory option cannot be given");
}

// ---------------------------------------------------------------------------------------------
// 3. Rejection of an observation-ownership overlap.
// ---------------------------------------------------------------------------------------------

#[test]
fn observation_used_twice_is_refused() {
    let fixture = Fixture::new(&[0.5, 0.5], &[0, 0], &[-35.0, -36.0])
        .set("drift:loglik", |_, _| 0.0)
        .set("pleiades:loglik", |_, _| 0.0)
        .set("bfo-check:loglik", |_, _| 0.0)
        .set("loglik:R1200", |_, _| -1.0);
    let samples = vec![fixture.replicate(1, one_mode())];
    let base = Product::filter(&samples, vec!["m1941.bto".into(), "m1941.bfo".into()]).unwrap();
    let declarations = [
        declaration("drift", &["debris:flaperon-reunion", "debris:pemba"], vec![], true),
        declaration("pleiades", &["pleiades:objects", "debris:flaperon-reunion"], vec![], true),
        declaration("bfo-check", &["m0019b.bfo"], vec![], true),
        Declaration::terminal("R1200", &[], vec!["m0019b.bto".into(), "m0019b.bfo".into()]),
    ];
    let error = compose(&base, &samples, &declarations, &ungated("x", &["drift", "pleiades"]), None).unwrap_err();
    assert!(error.contains("debris:flaperon-reunion") && error.contains("drift") && error.contains("pleiades"), "{error}");

    // Against the base: the filter already used m1941.bfo.
    let reuse = [declaration("drift", &["m1941.bfo"], vec![], true)];
    let error = compose(&base, &samples, &reuse, &ungated("x", &["drift"]), None).unwrap_err();
    assert!(error.contains("m1941.bfo"), "{error}");

    // Against a factor composed earlier: the 00:19 data option took m0019b.bfo.
    let terminal = compose(&base, &samples, &declarations, &ungated("R1200", &["terminal:R1200"]), None).unwrap();
    assert_eq!(terminal.observations, ["m1941.bto", "m1941.bfo", "m0019b.bto", "m0019b.bfo"]);
    let error = compose(&terminal, &samples, &declarations, &ungated("x", &["bfo-check"]), None).unwrap_err();
    assert!(error.contains("m0019b.bfo") && error.contains("bfo-check"), "{error}");

    // Within one module.
    let twice = [declaration("drift", &["debris:pemba", "debris:pemba"], vec![], true)];
    assert!(compose(&base, &samples, &twice, &ungated("x", &["drift"]), None).is_err());
    // Disjoint sets compose.
    assert!(compose(&base, &samples, &declarations[..2].iter().map(|d| Declaration { observations: vec![format!("{}:own", d.name)], ..d.clone() }).collect::<Vec<_>>(), &ungated("x", &["drift", "pleiades"]), None).is_ok());
}

// ---------------------------------------------------------------------------------------------
// 4. 0.0 versus NaN, and the refusal threshold.
// ---------------------------------------------------------------------------------------------

/// Four equally weighted samples. A module returning 0.0 everywhere is selected and exact: it
/// is in the product and changes nothing. A module with likelihoods (2, 1, NaN, 0.5): by hand,
/// D = (0.5 + 0.25 + 0.125) / 0.75 = 7/6 over the computed rows, the NaN row is carried at D,
/// and the weights are (3/7, 3/14, 1/4, 3/28). Reading NaN as 0.0 would give the NaN row 2/9,
/// as minus infinity 0. The NaN row's share 1/4 exceeds the default tolerance: refused.
#[test]
fn zero_is_exact_and_nan_is_neither_zero_nor_impossible() {
    let fixture = Fixture::new(&[0.25; 4], &[0; 4], &[-34.0, -35.0, -36.0, -37.0])
        .set("calibrating:loglik", |_, _| 0.0)
        .set("partial:loglik", |r, _| [2.0f64.ln(), 0.0, f64::NAN, 0.5f64.ln()][r])
        .set("impossible-here:loglik", |r, _| if r == 3 { f64::NEG_INFINITY } else { -1.0 })
        .set("impossible:loglik", |_, _| f64::NEG_INFINITY)
        .set("overflow:loglik", |r, _| if r == 0 { f64::INFINITY } else { 0.0 });
    let samples = vec![fixture.replicate(1, one_mode())];
    let base = Product::filter(&samples, vec![]).unwrap();
    let declarations: Vec<Declaration> = ["calibrating", "partial", "impossible-here", "impossible", "overflow"]
        .iter()
        .map(|n| declaration(n, &[], vec![], true))
        .collect();

    let zero = compose(&base, &samples, &declarations, &ungated("zero", &["calibrating"]), None).unwrap();
    assert_eq!(zero.contains, [FILTER, "calibrating"]);
    assert_eq!(zero.replicates[0].weights, base.replicates[0].weights);
    assert_eq!(zero.log_evidence_increment, 0.0);
    assert_eq!(zero.replicates[0].log_evidence_increment[0], 0.0);

    let error = compose(&base, &samples, &declarations, &ungated("partial", &["partial"]), None).unwrap_err();
    assert!(error.contains("partial") && error.contains("not computed") && error.contains("0.25"), "{error}");

    let tolerant = Set { tolerance: 0.3, ..ungated("partial", &["partial"]) };
    let product = compose(&base, &samples, &declarations, &tolerant, None).unwrap();
    let w = &product.replicates[0].weights;
    for (got, want) in w.iter().zip([3.0 / 7.0, 3.0 / 14.0, 0.25, 3.0 / 28.0]) {
        close(*got, want, 1e-14, "weights with a NaN row");
    }
    assert!((w[2] - 2.0 / 9.0).abs() > 0.02 && w[2] > 0.0, "NaN read as zero or as impossible");
    close(product.log_evidence_increment, (7.0f64 / 6.0).ln(), 1e-14, "evidence over the computed rows");
    assert_eq!(product.factors[0].not_computed_rows, [1]);
    assert_eq!(product.factors[0].not_computed_weight, [0.25]);
    assert_eq!(product.replicates[0].not_computed_rows, 1);

    // Minus infinity is impossible, not missing: weight exactly zero, nothing reported as not computed.
    let product = compose(&base, &samples, &declarations, &ungated("x", &["impossible-here"]), None).unwrap();
    assert_eq!(product.replicates[0].weights[3], 0.0);
    assert_eq!(product.factors[0].not_computed_rows, [0]);
    close(product.replicates[0].weights[0], 1.0 / 3.0, 1e-15, "remaining rows");
    // Data impossible under every sample, and +inf, are refused.
    assert!(compose(&base, &samples, &declarations, &ungated("x", &["impossible"]), None).is_err());
    assert!(compose(&base, &samples, &declarations, &ungated("x", &["overflow"]), None).is_err());
}

// ---------------------------------------------------------------------------------------------
// 5. Double-application refusal.
// ---------------------------------------------------------------------------------------------

/// The residual-PDF view searched areas needs is two products from one base, with and without
/// its column. Composing a factor onto a product that already contains it is refused, and every
/// product says exactly what it contains.
#[test]
fn a_factor_is_never_applied_twice() {
    let fixture = Fixture::new(&[0.25; 4], &[0; 4], &[-34.0, -35.0, -36.0, -37.0])
        .set("drift:loglik", |r, _| -(r as f64))
        .set("searched:loglik", |r, _| if r == 1 { -3.0 } else { 0.0 });
    let samples = vec![fixture.replicate(1, one_mode())];
    let base = Product::filter(&samples, vec![]).unwrap();
    let declarations = [declaration("drift", &["debris:a"], vec![], true), declaration("searched", &["search:phase-2"], vec![], true)];

    let drift = compose(&base, &samples, &declarations, &ungated("core+drift", &["drift"]), None).unwrap();
    let error = compose(&drift, &samples, &declarations, &ungated("again", &["drift"]), None).unwrap_err();
    assert!(error.contains("drift") && error.contains("already"), "{error}");
    assert!(compose(&base, &samples, &declarations, &ungated("twice", &["drift", "drift"]), None).is_err());

    let with = compose(&drift, &samples, &declarations, &ungated("core+drift+searched", &["searched"]), None).unwrap();
    assert_eq!(with.contains, [FILTER, "drift", "searched"]);
    assert_eq!(with.columns, ["drift:loglik", "searched:loglik"]);
    assert_eq!(drift.contains, [FILTER, "drift"]);
    let error = compose(&with, &samples, &declarations, &ungated("again", &["searched"]), None).unwrap_err();
    assert!(error.contains("searched"), "{error}");

    // Composed in one set or in two steps: the same product.
    let together = compose(&base, &samples, &declarations, &ungated("all", &["drift", "searched"]), None).unwrap();
    for (a, b) in together.replicates[0].weights.iter().zip(&with.replicates[0].weights) {
        close(*a, *b, 1e-15, "one set versus two steps");
    }
    close(together.log_evidence_increment, drift.log_evidence_increment + with.log_evidence_increment, 1e-14, "evidence adds");
}

// ---------------------------------------------------------------------------------------------
// 6. Per-(replicate, mode) evidence pooling agrees with summary.rs.
// ---------------------------------------------------------------------------------------------

/// summary.rs `pooling()` at e149ff5, transcribed statement for statement because this crate
/// cannot depend on the runner crate. results/composer-summary-rs.patch adds the same check
/// inside summary.rs against the function itself.
fn summary_rs_pooling(reps: &[[Mode; 5]]) -> (Vec<[f64; 5]>, [f64; 5]) {
    let prior: [f64; 5] = std::array::from_fn(|m| reps[0][m].prior_weight);
    let log_z: Vec<[f64; 5]> = reps.iter().map(|r| std::array::from_fn(|m| r[m].log_evidence)).collect();
    let max = log_z.iter().flatten().copied().fold(f64::NEG_INFINITY, f64::max);
    let z: Vec<[f64; 5]> = log_z.iter().map(|row| std::array::from_fn(|m| (row[m] - max).exp())).collect();
    let mean: [f64; 5] = std::array::from_fn(|m| z.iter().map(|row| row[m]).sum::<f64>() / reps.len() as f64);
    let weighted: [f64; 5] = std::array::from_fn(|m| prior[m] * mean[m]);
    let total: f64 = weighted.iter().sum();
    let mode_probability: [f64; 5] = std::array::from_fn(|m| if total > 0.0 { weighted[m] / total } else { 0.0 });
    let column: [f64; 5] = std::array::from_fn(|m| z.iter().map(|row| row[m]).sum());
    let factors = (0..reps.len())
        .map(|i| {
            std::array::from_fn(|m| {
                let share = if column[m] > 0.0 { z[i][m] / column[m] } else { 0.0 };
                let within = reps[i][m].posterior_probability;
                mode_probability[m] * share / if within > 0.0 { within } else { 1.0 }
            })
        })
        .collect();
    (factors, mode_probability)
}

/// Four replicates with three strata run and differing filter evidence, two children per
/// parent, and a module with a two-option alternative. Pooling the composed product with
/// summary.rs (its per-(replicate, mode) evidence and composed weights) must equal reweighting
/// the pooled base sample directly; likewise P(mode | D), P(option | D) and the evidence.
#[test]
fn per_replicate_mode_evidence_pools_like_summary_rs() {
    let prior = [0.3, 0.3, 0.0, 0.4, 0.0];
    let run = [0usize, 1, 3];
    let mut rng = ChaCha8Rng::seed_from_u64(6);
    let unit = Normal::new(0.0, 1.0).unwrap();
    let mut samples = Vec::new();
    for i in 0..4 {
        let log_z: [f64; 5] = std::array::from_fn(|m| if prior[m] > 0.0 { -50.0 + 1.5 * unit.sample(&mut rng) } else { 0.0 });
        let filter = modes(prior, log_z);
        let (mut weight, mut mode, mut lat) = (Vec::new(), Vec::new(), Vec::new());
        for &m in &run {
            let k = 40 + 10 * i + 4 * m;
            for _ in 0..k {
                weight.push(filter[m].posterior_probability / k as f64);
                mode.push(m);
                lat.push(-37.0 + m as f64 + unit.sample(&mut rng));
            }
        }
        let fixture = Fixture::new(&weight, &mode, &lat)
            .set(PARENT, |r, _| (r / 2) as f64)
            .set(FAMILY, |r, _| (r % 2) as f64)
            .set("probe:loglik:a", |_, row| ln_normal(-34.5, row[6], 1.0))
            .set("probe:loglik:b", |_, row| ln_normal(-36.0, row[6], 0.7));
        samples.push(fixture.replicate(i as u64 + 1, filter));
    }
    let base = Product::filter(&samples, vec![]).unwrap();
    let probe = declaration("probe", &["synthetic:probe"], vec![Alternatives::new("ocean-model", &[("a", 0.6), ("b", 0.4)])], true);
    let product = compose(&base, &samples, &[probe], &ungated("core+probe", &["probe"]), None).unwrap();

    let base_modes: Vec<[Mode; 5]> = samples.iter().map(|s| s.modes).collect();
    let composed_modes: Vec<[Mode; 5]> = product.replicates.iter().map(|r| r.modes).collect();
    let (base_factors, _) = summary_rs_pooling(&base_modes);
    let (factors, mode_probability) = summary_rs_pooling(&composed_modes);

    // Direct: the pooled base sample times each row's likelihood, mixed over the alternative.
    let mut direct = Vec::new();
    let mut via_summary = Vec::new();
    let mut option_mass = [0.0; 2];
    for (i, s) in samples.iter().enumerate() {
        let (wc, mc, a, b) = (s.column(WEIGHT).unwrap(), s.column(STRATUM).unwrap(), s.column("probe:loglik:a").unwrap(), s.column("probe:loglik:b").unwrap());
        for r in 0..s.rows() {
            let m = s.get(r, mc) as usize;
            let pooled = s.get(r, wc) * base_factors[i][m];
            let (la, lb) = (0.6 * s.get(r, a).exp(), 0.4 * s.get(r, b).exp());
            direct.push((m, pooled * (la + lb)));
            option_mass[0] += pooled * la;
            option_mass[1] += pooled * lb;
            via_summary.push(product.replicates[i].weights[r] * factors[i][m]);
        }
    }
    let total: f64 = direct.iter().map(|d| d.1).sum();
    let pooled_total: f64 = via_summary.iter().sum();
    close(pooled_total, 1.0, 1e-12, "pooled composed weights sum");
    for ((_, d), v) in direct.iter().zip(&via_summary) {
        close(*v, d / total, 1e-12 * (d / total).max(1e-300).max(1e-6), "pooled composed weight");
    }
    for &m in &run {
        let mass: f64 = direct.iter().filter(|d| d.0 == m).map(|d| d.1).sum::<f64>() / total;
        close(mode_probability[m], mass, 1e-12, "P(mode | D) by summary.rs pooling");
    }
    let p = product.alternatives[0].posterior.clone().unwrap();
    close(p[0], option_mass[0] / total, 1e-12, "P(option | D) pooled");
    close(p[1], option_mass[1] / total, 1e-12, "P(option | D) pooled");
    close(product.log_evidence_increment, total.ln(), 1e-12, "pooled evidence increment");
    // Split-half agreement is reported, from replicates (1, 2) and (3, 4).
    let half = product.split_half.as_ref().unwrap();
    assert_eq!(half.alternatives[0].0, "ocean-model");
    assert!(half.max_probability_difference.is_finite());
    // Families come first and carry the family Bayes factor per replicate.
    assert_eq!(product.families.len(), 2);
    assert_eq!(product.families[0].log_bayes_factor.len(), 4);
}

// ---------------------------------------------------------------------------------------------
// 7. The synthetic hydroacoustic composer test.
// ---------------------------------------------------------------------------------------------

const EARTH_RADIUS_KM: f64 = 6371.0;
const SOUND_KM_PER_S: f64 = 1.48;
const KM_PER_DEG: f64 = EARTH_RADIUS_KM * std::f64::consts::PI / 180.0;
const CENTRE: (f64, f64) = (-35.0, 92.0);

fn range_km(lat1: f64, lon1: f64, lat2: f64, lon2: f64) -> f64 {
    let (p1, p2) = (lat1.to_radians(), lat2.to_radians());
    let (dp, dl) = (p2 - p1, (lon2 - lon1).to_radians());
    let a = (dp / 2.0).sin().powi(2) + p1.cos() * p2.cos() * (dl / 2.0).sin().powi(2);
    2.0 * EARTH_RADIUS_KM * a.sqrt().asin()
}

/// Local east and north offsets (km) from the centre, to latitude and longitude.
fn position(east_km: f64, north_km: f64) -> (f64, f64) {
    (CENTRE.0 + north_km / KM_PER_DEG, CENTRE.1 + east_km / (KM_PER_DEG * CENTRE.0.to_radians().cos()))
}

/// A synthetic single-station detection: arrival time = impact time + range / c, Gaussian
/// timing error. Geometry only — straight great-circle ranges at one sound speed; the station
/// positions are near H01, H08 and H04 but nothing here is their real propagation.
struct Station {
    name: &'static str,
    at: (f64, f64),
    observed_s: f64,
    sd_s: f64,
}

impl Station {
    fn arrival(&self, unix_s: f64, lat: f64, lon: f64) -> f64 {
        unix_s + range_km(lat, lon, self.at.0, self.at.1) / SOUND_KM_PER_S
    }
}

impl Hypothesis for Station {
    fn observations(&self) -> Vec<String> {
        vec![format!("hydro:{}.arrival", self.name)]
    }
    fn absolute_scale(&self) -> bool {
        true
    }
    fn impact_log_likelihood(&self, impact: &ImpactView, _choice: &[usize]) -> f64 {
        ln_normal(self.observed_s, self.arrival(impact.unix_s, impact.latitude_deg, impact.longitude_deg), self.sd_s)
    }
}

fn view(row: &[f64]) -> ImpactView<'static> {
    ImpactView {
        parent: row[1] as usize,
        unix_s: row[5],
        latitude_deg: row[6],
        longitude_deg: row[7],
        velocity_east_mps: f64::NAN,
        velocity_north_mps: f64::NAN,
        velocity_up_mps: f64::NAN,
        flight_path_angle_deg: f64::NAN,
        mass_kg: f64::NAN,
        kinetic_energy_j: f64::NAN,
        vertical_kinetic_energy_j: f64::NAN,
        family: row[4] as usize,
        takeover_unix_s: f64::NAN,
        takeover_latitude_deg: f64::NAN,
        takeover_longitude_deg: f64::NAN,
        takeover_altitude_ft: f64::NAN,
        mode: row[2] as usize,
        alternative: row[3] as usize,
        latents: &[],
    }
}

/// An impact prior elongated along a synthetic arc (60 km east by 150 km north, standard
/// deviations), the true impact 30 km west and 120 km north of its centre, and noise-free
/// detections (O - C = 0 at the truth, 10 s timing error, i.e. 14.8 km in range) at one, two
/// or three stations. The composer must make the move of the impact PDF computable: its mean
/// agrees with an independent grid quadrature of prior x likelihood within four standard
/// errors, its evidence likewise, the PDF tightens with each station, three stations cover the
/// truth, composing stations together or one at a time gives one answer, and the halves agree.
#[test]
fn synthetic_hydroacoustic_detections_move_the_impact_pdf() {
    let (sd_east, sd_north) = (60.0, 150.0);
    let truth = position(-30.0, 120.0);
    let stations: Vec<Station> = [("S1", (-34.9, 114.1)), ("S2", (-7.6, 72.5)), ("S3", (-46.5, 52.0))]
        .into_iter()
        .map(|(name, at)| {
            let mut s = Station { name, at, observed_s: 0.0, sd_s: 10.0 };
            s.observed_s = s.arrival(0.0, truth.0, truth.1);
            s
        })
        .collect();
    let declarations: Vec<Declaration> = stations.iter().map(|s| Declaration::module(s.name, s)).collect();
    assert_eq!(declarations[0].observations, ["hydro:S1.arrival"]);

    let n = 200_000;
    let samples: Vec<Replicate> = (0..2u64)
        .map(|seed| {
            let mut rng = ChaCha8Rng::seed_from_u64(70 + seed);
            let (east, north) = (Normal::new(0.0, sd_east).unwrap(), Normal::new(0.0, sd_north).unwrap());
            let points: Vec<(f64, f64)> = (0..n).map(|_| position(east.sample(&mut rng), north.sample(&mut rng))).collect();
            let mut fixture = Fixture::new(&vec![1.0 / n as f64; n], &vec![0; n], &points.iter().map(|p| p.0).collect::<Vec<_>>())
                .set("longitude_deg", |r, _| points[r].1);
            for s in &stations {
                fixture = fixture.set(&format!("{}:loglik", s.name), |_, row| s.impact_log_likelihood(&view(row), &[]));
            }
            fixture.replicate(seed + 1, one_mode())
        })
        .collect();
    let base = Product::filter(&samples, vec![]).unwrap();
    let prior_mean = base.moments(&samples, "latitude_deg").unwrap();

    // Independent reference: prior x likelihood on a 2 km grid over +-6 sd.
    let reference = |k: usize| {
        let (mut mass, mut lat, mut lon, mut evidence) = (0.0, 0.0, 0.0, 0.0);
        let mut prior_mass = 0.0;
        for i in -180..=180 {
            for j in -450..=450 {
                let (e, nn) = (2.0 * i as f64, 2.0 * j as f64);
                let prior = (-0.5 * ((e / sd_east).powi(2) + (nn / sd_north).powi(2))).exp();
                let (la, lo) = position(e, nn);
                let ll: f64 = stations[..k].iter().map(|s| ln_normal(s.observed_s, s.arrival(0.0, la, lo), s.sd_s)).sum();
                let w = prior * ll.exp();
                prior_mass += prior;
                mass += w;
                lat += w * la;
                lon += w * lo;
                evidence += w;
            }
        }
        (lat / mass, lon / mass, (evidence / prior_mass).ln())
    };

    let mut spread = vec![f64::INFINITY];
    for k in 1..=3 {
        let names: Vec<&str> = stations[..k].iter().map(|s| s.name).collect();
        let set = Set { ess_floor: 1000.0, ..Set::new(&format!("core+{}", names.join("+")), &names) };
        let product = compose(&base, &samples, &declarations, &set, None).unwrap();
        let (ref_lat, ref_lon, ref_ln_z) = reference(k);
        let lat = product.moments(&samples, "latitude_deg").unwrap();
        let lon = product.moments(&samples, "longitude_deg").unwrap();
        for i in 0..2 {
            let ess = product.ess[i].rows;
            assert!(ess > 100.0, "{k} stations: ESS {ess}");
            close(lat[i].0, ref_lat, 4.0 * lat[i].1 / ess.sqrt(), "posterior mean latitude");
            close(lon[i].0, ref_lon, 4.0 * lon[i].1 / ess.sqrt(), "posterior mean longitude");
            let w = &product.replicates[i].weights;
            let se = ((n as f64 * w.iter().map(|v| v * v).sum::<f64>() - 1.0) / n as f64).sqrt();
            close(product.replicates[i].log_evidence_increment[0], ref_ln_z, 4.0 * se, "evidence");
            // The move of the impact PDF, in km, is computable from the product.
            let moved_north = (lat[i].0 - prior_mean[i].0) * KM_PER_DEG;
            assert!(moved_north.is_finite());
        }
        let east_km = |lon: f64| (lon - CENTRE.1) * KM_PER_DEG * CENTRE.0.to_radians().cos();
        eprintln!(
            "{k} station(s): mean moved {:+.1} km north, {:+.1} km east (truth {:+.1}, {:+.1}); sd {:.1} km north, {:.1} km east; ESS {:.0}; ln D {:.3} (grid {ref_ln_z:.3})",
            (lat[0].0 - prior_mean[0].0) * KM_PER_DEG,
            east_km(lon[0].0) - east_km(base.moments(&samples, "longitude_deg").unwrap()[0].0),
            (truth.0 - CENTRE.0) * KM_PER_DEG,
            east_km(truth.1),
            lat[0].1 * KM_PER_DEG,
            lon[0].1 * KM_PER_DEG * CENTRE.0.to_radians().cos(),
            product.ess[0].rows,
            product.replicates[0].log_evidence_increment[0],
        );
        let min_ess = product.ess.iter().map(|e| e.parents).fold(f64::INFINITY, f64::min);
        assert_eq!(product.status == Status::Converged, min_ess >= 1000.0, "status {:?}, ESS {min_ess}", product.status);
        let area = lat[0].1 * lon[0].1;
        assert!(area < *spread.last().unwrap(), "{k} stations: the PDF must tighten ({area} after {:?})", spread);
        spread.push(area);
        if k == 3 {
            for i in 0..2 {
                assert!((lat[i].0 - truth.0).abs() < 3.0 * lat[i].1, "truth latitude covered");
                assert!((lon[i].0 - truth.1).abs() < 3.0 * lon[i].1, "truth longitude covered");
            }
        }
        if k == 2 {
            let first = compose(&base, &samples, &declarations, &ungated("S1", &["S1"]), None).unwrap();
            let then = compose(&first, &samples, &declarations, &ungated("S1 then S2", &["S2"]), None).unwrap();
            for (a, b) in then.replicates[0].weights.iter().zip(&product.replicates[0].weights) {
                close(*a, *b, 1e-12 * b.max(1e-12), "stations together or one at a time");
            }
        }
        let half = product.split_half.as_ref().unwrap();
        let se: f64 = (0..2)
            .map(|i| {
                let w = &product.replicates[i].weights;
                (n as f64 * w.iter().map(|v| v * v).sum::<f64>() - 1.0) / n as f64
            })
            .sum::<f64>()
            .sqrt();
        close(half.log_evidence_increment[0], half.log_evidence_increment[1], 4.0 * se, "split-half evidence");
    }
}
