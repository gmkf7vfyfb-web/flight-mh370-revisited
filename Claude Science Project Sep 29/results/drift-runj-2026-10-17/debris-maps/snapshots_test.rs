
/// UNTRACKED stand-in harness (architecture, 17 Oct 2026; NOT committed to hypothesis/debris-drift):
/// debris position snapshots for maps. Same classes, windage draws (incl. product offset), ocean-error and
/// diffusivity draws as `pilot`; no importance splitting, so every particle has weight 1.
/// Env: DRIFT_CONFIG, SNAP_SPEC (toml: releases = [[lon, lat, t0_unix], ...], times = [unix, ...]), SNAP_OUT.
/// Record per particle (little-endian): u8 release, u8 env, u8 class, u8 fate (0 afloat 1 beached 2 left 3 model error 4 on land),
/// f32 first-beaching day after release, f32 lon, f32 lat (NaN if none), then f32 lon, f32 lat per output time (NaN if not afloat).
#[test]
#[ignore]
fn snapshots() {
    use std::io::Write;
    let path = std::env::var("DRIFT_CONFIG").unwrap();
    let run: toml::Value = toml::from_str(&std::fs::read_to_string(&path).unwrap()).unwrap();
    let p: Params = run["hypotheses"]["debris-drift"].clone().try_into().unwrap();
    let spec: toml::Value = toml::from_str(&std::fs::read_to_string(std::env::var("SNAP_SPEC").unwrap()).unwrap()).unwrap();
    let rel: Vec<[f64; 3]> = spec["releases"].as_array().unwrap().iter().map(|r| { let a = r.as_array().unwrap(); [a[0].as_float().unwrap(), a[1].as_float().unwrap(), a[2].as_float().unwrap()] }).collect();
    let times: Vec<f64> = spec["times"].as_array().unwrap().iter().map(|t| t.as_float().unwrap()).collect();
    let domain = Domain { lon_min: p.domain[0], lon_max: p.domain[1], lat_min: p.domain[2], lat_max: p.domain[3] };
    let mut setup = OceanSetup::new(&p.transport, domain, p.dt_hours * 3600.0, p.threads, p.leeway_absorbs_stokes, p.explicit_residual, p.land_gap_is_beaching).unwrap();
    setup.refloat_per_day = p.refloat_per_day;
    if let Some(oe) = &p.ocean_error {
        setup.ocean_error = ocean::OceanErrorModel::eddying(oe.sigma_m_s, oe.length_scale_km * 1000.0, oe.time_scale_days * 86_400.0, oe.modes);
    }
    let prior = super::diffusivity_prior(&p);
    let envs: Vec<(u64, Diffusion)> = p.env_seeds.iter().map(|&s| (s, prior.draw(s))).collect();
    let mut f = std::io::BufWriter::new(std::fs::File::create(std::env::var("SNAP_OUT").unwrap()).unwrap());
    for (r, &[lon, lat, t0]) in rel.iter().enumerate() {
        for (e, &(seed, diffusion)) in envs.iter().enumerate() {
            for c in 0..p.classes.len() {
                let resp = super::class_responses(&p, c);
                let parts: Vec<Particle> = resp.iter().map(|&q| Particle::new([lon, lat], t0, q)).collect();
                let (fates, eps, pos, _) = setup.run_tracks_ep(&parts, seed, diffusion, &times).unwrap();
                for i in 0..parts.len() {
                    let code: u8 = match fates[i] { Fate::Afloat => 0, Fate::Beached { .. } => 1, Fate::LeftDomain => 2, Fate::ModelError => 3, Fate::ReleasedOnLand => 4 };
                    let (bt, bl) = match eps[i].first() { Some(ep) => (((ep.t - t0) / 86_400.0) as f32, [ep.at[0] as f32, ep.at[1] as f32]), None => (f32::NAN, [f32::NAN; 2]) };
                    let mut rec: Vec<u8> = vec![r as u8, e as u8, c as u8, code];
                    for v in [bt, bl[0], bl[1]] { rec.extend_from_slice(&v.to_le_bytes()); }
                    for k in 0..times.len() {
                        let q = pos[i][k].map(|x| [x[0] as f32, x[1] as f32]).unwrap_or([f32::NAN; 2]);
                        rec.extend_from_slice(&q[0].to_le_bytes()); rec.extend_from_slice(&q[1].to_le_bytes());
                    }
                    f.write_all(&rec).unwrap();
                }
                println!("release {r} env {e} class {c} done");
            }
        }
    }
}
