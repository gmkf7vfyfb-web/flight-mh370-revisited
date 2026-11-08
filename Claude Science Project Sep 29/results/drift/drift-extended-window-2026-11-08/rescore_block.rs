
// ---- Offline rescoring from the arrivals dump (write_arrivals) ------------------------------------------
// Re-runs the recovery layer on stored beachings with a new segment map, find list, window, periods, delay,
// freshness marks and bandwidths. It calls the same Recovery::coefficients and shadow_coefficients as a
// module run, so with the run's own settings it reproduces coefficients.jsonl (up to the f32 storage of
// particle weights). Entry: DRIFT_RESCORE=<config.toml> $BIN rescore_entry --ignored --nocapture.

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
struct RescoreFind {
    id: String,
    class: usize,
    lon: f64,
    lat: f64,
    t_start_days: f64,
    t_end_days: f64,
    #[serde(default)]
    fresh_days: Option<f64>,
}

#[derive(Deserialize, Clone, Debug)]
#[serde(deny_unknown_fields)]
struct RescoreConfig {
    arrivals: Vec<String>,
    output: String,
    n_classes: usize,
    /// Particles per class of the run (the halves split at n/2, as the module does).
    particles_per_class: usize,
    window_end_days: f64,
    period_breaks_days: Vec<f64>,
    delay_days: f64,
    /// First entry is the primary bandwidth (set 0), as in a module run.
    bandwidths_km: Vec<f64>,
    segments: Vec<Segment>,
    finds: Vec<RescoreFind>,
}

struct ArrBlock {
    node: u32,
    lat: f64,
    lon: f64,
    env_seed: u64,
    class: usize,
    released: usize,
    arrivals: Vec<(usize, Arrival)>,
}

fn read_arrival_blocks(path: &str, map: &SegmentMap, out: &mut Vec<ArrBlock>) -> Result<(), String> {
    let b = std::fs::read(path).map_err(|e| format!("rescore: {path}: {e}"))?;
    let u32_at = |o: usize| u32::from_le_bytes(b[o..o + 4].try_into().unwrap());
    let i32_at = |o: usize| i32::from_le_bytes(b[o..o + 4].try_into().unwrap());
    let u64_at = |o: usize| u64::from_le_bytes(b[o..o + 8].try_into().unwrap());
    let f64_at = |o: usize| f64::from_le_bytes(b[o..o + 8].try_into().unwrap());
    let f32_at = |o: usize| f32::from_le_bytes(b[o..o + 4].try_into().unwrap()) as f64;
    let mut o = 0usize;
    while o < b.len() {
        if o + 60 > b.len() || &b[o..o + 4] != b"ARV1" {
            return Err(format!("rescore: {path}: bad block header at byte {o}"));
        }
        let (node, lat, lon, env_seed) = (u32_at(o + 4), f64_at(o + 8), f64_at(o + 16), u64_at(o + 24));
        let (class, released, n) = (u32_at(o + 32) as usize, u32_at(o + 36) as usize, u32_at(o + 40) as usize);
        o += 60;
        if o + 52 * n > b.len() {
            return Err(format!("rescore: {path}: truncated block for node {node}"));
        }
        let mut arrivals = Vec::with_capacity(n);
        for r in 0..n {
            let q = o + 52 * r;
            let (lo, la, line, s) = (f64_at(q + 20), f64_at(q + 28), i32_at(q + 36), f64_at(q + 40));
            let place = if line >= 0 && s.is_finite() { Place::on_line(line as u32, s, [lo, la]) } else { Place::at([lo, la]) };
            arrivals.push((u32_at(q) as usize, Arrival { place, segment: map.locate([lo, la]), t_days: f64_at(q + 8), t_leave_days: f32_at(q + 16), w: f32_at(q + 4) }));
        }
        o += 52 * n;
        out.push(ArrBlock { node, lat, lon, env_seed, class, released, arrivals });
    }
    Ok(())
}

pub fn rescore(config_path: &str) -> Result<(), String> {
    let cfg: RescoreConfig = toml::from_str(&std::fs::read_to_string(config_path).map_err(|e| format!("rescore: {config_path}: {e}"))?).map_err(|e| format!("rescore: {config_path}: {e}"))?;
    let map = SegmentMap::new(cfg.segments.clone())?;
    let ns = map.len();
    let mut obs = Vec::new();
    for f in &cfg.finds {
        let segment = map.locate([f.lon, f.lat]).ok_or(format!("rescore: find `{}` lies in no segment", f.id))?;
        if f.class >= cfg.n_classes || !(f.t_end_days > f.t_start_days) || f.t_end_days > cfg.window_end_days {
            return Err(format!("rescore: find `{}`: bad class or dates", f.id));
        }
        if f.fresh_days.is_some_and(|x| !(x > 0.0)) {
            return Err(format!("rescore: find `{}`: fresh_days must be positive", f.id));
        }
        obs.push(Observation { id: f.id.clone(), class: f.class, place: Place::at([f.lon, f.lat]), segment, t_start_days: f.t_start_days, t_end_days: f.t_end_days });
    }
    let by_class: Vec<Vec<usize>> = (0..cfg.n_classes).map(|c| (0..obs.len()).filter(|&j| obs[j].class == c).collect()).collect();
    let fresh: Vec<Option<f64>> = cfg.finds.iter().map(|f| f.fresh_days).collect();
    let base = Recovery { n_segments: ns, breaks_days: cfg.period_breaks_days.clone(), edges: Vec::new(), delay: Delay::Exponential { mean_days: cfg.delay_days }, bandwidth_km: cfg.bandwidths_km[0], window_end_days: cfg.window_end_days };
    let recs: Vec<Recovery> = cfg.bandwidths_km.iter().map(|&h| Recovery { bandwidth_km: h, ..base.clone() }).collect();
    let np = base.n_periods();
    let n = cfg.particles_per_class;
    let half = n / 2;
    let mut w = std::io::BufWriter::new(std::fs::File::create(&cfg.output).map_err(|e| format!("rescore: {}: {e}", cfg.output))?);
    for path in &cfg.arrivals {
        let mut blocks = Vec::new();
        read_arrival_blocks(path, &map, &mut blocks)?;
        let mut nodes: Vec<u32> = Vec::new();
        for b in &blocks {
            if !nodes.contains(&b.node) {
                nodes.push(b.node);
            }
        }
        for &k in &nodes {
            let nb: Vec<&ArrBlock> = blocks.iter().filter(|b| b.node == k).collect();
            let mut seeds: Vec<u64> = Vec::new();
            for b in &nb {
                if !seeds.contains(&b.env_seed) {
                    seeds.push(b.env_seed);
                }
            }
            // sets[bandwidth][part] -> [env][class]
            let mut sets: Vec<[Vec<Vec<Option<recovery::Coefficients>>>; 3]> = (0..recs.len()).map(|_| [Vec::new(), Vec::new(), Vec::new()]).collect();
            for &s in &seeds {
                let mut per: Vec<[Vec<Option<recovery::Coefficients>>; 3]> = (0..recs.len()).map(|_| [Vec::new(), Vec::new(), Vec::new()]).collect();
                for c in 0..cfg.n_classes {
                    let blk = nb.iter().find(|b| b.env_seed == s && b.class == c);
                    for (ri, rr) in recs.iter().enumerate() {
                        match blk {
                            None => per[ri].iter_mut().for_each(|v| v.push(None)),
                            Some(b) => {
                                if b.released != n {
                                    return Err(format!("rescore: node {k}: released {} but particles_per_class {n}", b.released));
                                }
                                let all: Vec<Arrival> = b.arrivals.iter().map(|x| x.1).collect();
                                let ha: Vec<Arrival> = b.arrivals.iter().filter(|x| x.0 < half).map(|x| x.1).collect();
                                let hb: Vec<Arrival> = b.arrivals.iter().filter(|x| x.0 >= half).map(|x| x.1).collect();
                                let so: Vec<&Observation> = by_class[c].iter().map(|&j| &obs[j]).collect();
                                let sf: Vec<Option<f64>> = by_class[c].iter().map(|&j| fresh[j]).collect();
                                per[ri][0].push(Some(shadow_coefficients(rr, &so, &sf, &all, n)));
                                per[ri][1].push(Some(shadow_coefficients(rr, &so, &sf, &ha, half)));
                                per[ri][2].push(Some(shadow_coefficients(rr, &so, &sf, &hb, n - half)));
                            }
                        }
                    }
                }
                for (ri, p3) in per.into_iter().enumerate() {
                    for (pi, v) in p3.into_iter().enumerate() {
                        sets[ri][pi].push(v);
                    }
                }
            }
            let (la, lo) = (nb[0].lat, nb[0].lon);
            let body: Vec<String> = sets
                .iter()
                .map(|s| format!("{{\"full\":{},\"half_a\":{},\"half_b\":{}}}", coef_json(&s[0], &by_class, &obs, np), coef_json(&s[1], &by_class, &obs, np), coef_json(&s[2], &by_class, &obs, np)))
                .collect();
            std::io::Write::write_all(&mut w, format!("{{\"node\":{k},\"lat\":{la:e},\"lon\":{lo:e},\"env_seeds\":[{}],\"sets\":[{}]}}\n", seeds.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(","), body.join(",")).as_bytes()).map_err(|e| e.to_string())?;
        }
        eprintln!("rescore: {path}: {} nodes", nodes.len());
    }
    std::io::Write::flush(&mut w).map_err(|e| e.to_string())?;
    Ok(())
}

#[cfg(test)]
mod rescore_entry {
    #[test]
    #[ignore]
    fn rescore() {
        super::rescore(&std::env::var("DRIFT_RESCORE").expect("DRIFT_RESCORE=<config.toml>")).unwrap();
    }
}
