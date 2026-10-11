"""Composer pass 1 (run C): build the row-aligned factor columns for one (stratum, seed) of core run C.

run C NOT CONVERGED; EoF physics provisional, no structural limit (G13); hydro predictive, not calibrated; drift GLORYS12
only, current nodes; GlobCurrent excluded (F1). Architecture stand-in glue: an adaptation of results/composer-pass0/prep_inputs.py
to run C's compact layout. Every factor is its owner's own arithmetic, imported read-only, or (searched areas) a validated
transcription (seabed_loglik.py). Columns are stored float32 (the run C sources are float32), read as f64 by the driver.

Columns (one row per impacts32.npy row, same order):
  weight, parent, mode (core autopilot mode, from parents32.npy), family (EoF family_code 1-6), family4 (EoF family4_code),
  latitude_deg, longitude_deg, speed_mps (contact speed |v|)
  loglik:<opt>+unpowered and loglik:<opt>+unpowered-v212, opt in heldout / r600-bto / r600-bfo:
      EoF derived_logliks (r600-bto), loglik:r600/no-offset (r600-bfo, 00:19 R600 BTO + Raw BFO), 0 (Held Out),
      + constraint_log_factor(..., 'other', 'unpowered'); -v212 adds -inf where speed > 212 m/s (ruling 8dbefed2 / 20:35 -0600)
  debris-drift:loglik:<GLORYS>        drift run C export, lnL_glorys12_h50 where state == 1, else NaN (not computed)
  hydroacoustics:loglik               stand-in L_hyd (lhyd.Model.station_terms total, scenario A) with audit F8: IMS SNR uses
                                      Blackman App. B noise (proxy 3376 + per-station offset, module's offsets file)
  pleiades:loglik:H/rho4-0/equal/<GLORYS>        lnL_pleiades_glorys12, NaN where not_computed
  pleiades-cosmo:loglik:H/rho4-0/equal/<GLORYS>  lnL_both_glorys12 (Pléiades + four COSMO contacts)
  pleiades-rho0:..., pleiades-rho05:...          reader.load_rho(seed, 0 / 0.5, model 0): P + C4, correlated transport errors
  seabed-search:loglik                searched areas, point target, rho 0.05 (seabed_loglik.py)
Usage: python prep_inputs_c.py <stratum> <seed> <out_dir>
"""
import hashlib, importlib.util, json, pathlib, sys, time
import numpy as np

EXCH = pathlib.Path("/Users/pete/Downloads/mh370-exchange")
EOF_RUN = EXCH / "end-of-flight/next-run-c"
DRIFT = EXCH / "debris-drift/next-run-c"
PLEI = EXCH / "pleiades/hydro-test/next-run-c"
HERE = pathlib.Path(__file__).resolve().parent
REPO = ((pathlib.Path(__file__).resolve().parent.parent / "repo/Claude Science Project Sep 29" if (pathlib.Path(__file__).resolve().parent.parent / "repo").exists() else pathlib.Path(__file__).resolve().parents[2]) if (pathlib.Path(__file__).resolve().parent.parent / "repo").exists() else pathlib.Path(__file__).resolve().parents[2])
EOF_SMOKE = REPO / "engine/hypotheses/end-of-flight/smoke"
SATCOM = REPO / "engine/data/satcom-observations.csv"
HYDRO_MOD = pathlib.Path("/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/d74bf70e-a424-46a9-8149-902d027e782a/hydro-wt/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics")
HYDRO_SCRIPTS = REPO / "results/hydroacoustics-pleiades-test-standin/standin-scripts"
HYDRO_EVENTS = REPO / "results/hydroacoustics-pleiades-test-standin/imos_events_searched.json"
KADRI_CSV = HYDRO_MOD / "results-data/kadri2a/kadri_table1_geometry.csv"
BN_OFF = json.loads((HYDRO_MOD / "results-data/blackman_noise/blackman_noise_offsets.json").read_text())
STRATA = ["next-c-free", "next-c-repro-radar", "next-c-descent-climb", "next-c-routes"]   # core order = hydro rng stream index
GLORYS = "glorys12v1+era5-wind10"
SPEED_CAP = 212.0
CHUNK = 400_000


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): h.update(b)
    return h.hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def main(stratum, seed, outd):
    t0 = time.time()
    assert sha(HYDRO_SCRIPTS / "lhyd.py").startswith("5000c56e")
    outd = pathlib.Path(outd); outd.mkdir(parents=True, exist_ok=True)
    try:                     # one writer per seed file (two orchestrators were started by mistake; see results note, deviations)
        (outd / f"seed-{seed}.lock").mkdir()
    except FileExistsError:
        while not (outd / f"seed-{seed}.json").exists():
            time.sleep(10)
        return
    sd = EOF_RUN / stratum / f"seed-{seed}"
    sys.path.insert(0, str(EOF_SMOKE))
    ci = load_module("compact_impacts", EOF_SMOKE / "compact_impacts.py")
    dh = load_module("eof_dh", EOF_SMOKE / "displacement_hist.py"); dh.SATCOM_CSV = SATCOM
    meta, g = ci.load(sd); n = int(meta["compact"]["rows"])
    w = g("weight"); par = g("parent"); lat, lon = g("latitude_deg"), g("longitude_deg")
    assert w.size == n
    P = np.load(sd / "parents32.npy"); pidx = np.searchsorted(P[:, 0], par); assert np.array_equal(P[pidx, 0], par)
    mode = P[pidx, 2].astype(float)
    fam, fam4 = g("family_code"), g("family4_code")
    speed = np.sqrt(g("velocity_east_mps") ** 2 + g("velocity_north_mps") ** 2 + g("velocity_up_mps") ** 2)
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]
    der = dh.derived_logliks(meta, g, present)
    unp = dh.constraint_log_factor(g, logon, "other", "unpowered")
    cap = np.where(speed <= SPEED_CAP, 0.0, -np.inf)
    fin = lambda x: np.where(np.isfinite(x), x, -np.inf)
    term = {"heldout": np.zeros(n), "r600-bto": fin(der["r600-bto"]), "r600-bfo": fin(g("loglik:r600/no-offset"))}
    C = {"weight": w, "parent": par, "mode": mode, "family": np.nan_to_num(fam, nan=0.0), "family4": np.nan_to_num(fam4, nan=0.0),
         "latitude_deg": lat, "longitude_deg": lon, "speed_mps": speed}
    for k, v in term.items():
        C[f"loglik:{k}+unpowered"] = v + unp
        C[f"loglik:{k}+unpowered-v212"] = v + unp + cap
    # drift (run C export, row-aligned)
    D = np.load(DRIFT / stratum / f"seed-{seed}" / "drift-lnL.npy", mmap_mode="r")
    assert len(D) == n and np.array_equal(np.asarray(D["row"]), np.arange(n)) and np.array_equal(np.asarray(D["parent"]).astype(float), par)
    st = np.asarray(D["state_glorys12_h50"])
    C[f"debris-drift:loglik:{GLORYS}"] = np.where(st == 1, np.asarray(D["lnL_glorys12_h50"], float), np.nan)
    # Pléiades v2 (run C)
    Pd = PLEI / stratum / f"seed-{seed}"
    Q = np.load(Pd / "pleiades-lnL.npy", mmap_mode="r")
    assert len(Q) == n and np.array_equal(np.asarray(Q["row"]), np.arange(n)) and np.array_equal(np.asarray(Q["parent"]).astype(float), par)
    nc = np.asarray(Q["not_computed"]).astype(bool)
    C[f"pleiades:loglik:H/rho4-0/equal/{GLORYS}"] = np.where(nc, np.nan, np.asarray(Q["lnL_pleiades_glorys12"], float))
    C[f"pleiades-cosmo:loglik:H/rho4-0/equal/{GLORYS}"] = np.where(nc, np.nan, np.asarray(Q["lnL_both_glorys12"], float))
    sys.path.insert(0, str(PLEI)); import reader
    C[f"pleiades-rho0:loglik:H/rho4-0/equal/{GLORYS}"] = reader.load_rho(Pd, 0, model=0)
    C[f"pleiades-rho05:loglik:H/rho4-0/equal/{GLORYS}"] = reader.load_rho(Pd, 0.5, model=0)
    # searched areas
    sys.path.insert(0, str(HERE)); import seabed_loglik
    C["seabed-search:loglik"] = seabed_loglik.loglik(lat, lon)
    # hydro stand-in + F8
    sys.path.insert(0, str(HYDRO_SCRIPTS)); import lhyd

    class ModelF8(lhyd.Model):
        def _snr0(self, lat_, E_, nu_, tab, noise_key):
            v = lhyd.Model._snr0(self, lat_, E_, nu_, tab, noise_key)
            for stn in ("H01W", "H08S"):
                if tab is self.tl_ims.get(stn):
                    v = v - BN_OFF[stn]          # audit F8: Blackman App. B noise = proxy 3376 + offset
            return v

    m = ModelF8(str(HYDRO_MOD), str(HYDRO_EVENTS), str(KADRI_CSV))
    th = m.station_terms(g("unix_s"), lat, lon, g("kinetic_energy_j"), np.random.default_rng([20261010, STRATA.index(stratum), seed]), "A")
    C["hydroacoustics:loglik"] = np.asarray(th["total"], float)
    names = list(C)
    with open(outd / f"seed-{seed}.f32", "wb") as f:
        for s in range(0, n, CHUNK):
            np.stack([C[k][s:s + CHUNK] for k in names], axis=1).astype("<f4").tofile(f)
    mass = np.bincount(mode.astype(int), weights=w, minlength=5)
    hdr = {"stratum": stratum, "seed": seed, "rows": n, "columns": names,
           "modes": [{"prior_weight": 1.0, "log_evidence": (float(np.log(mass[k])) if mass[k] > 0 else None),
                      "posterior_probability": float(mass[k] / mass.sum())} for k in range(5)],
           "counts": {"family4_rows": {str(int(v)): int((C["family4"] == v).sum()) for v in np.unique(C["family4"])},
                      "family_rows": {str(int(v)): int((C["family"] == v).sum()) for v in np.unique(C["family"])},
                      "drift_state_rows": {str(k): int((st == k).sum()) for k in (0, 1, 2)}, "pleiades_not_computed_rows": int(nc.sum()),
                      "rho_nan_rows": int(np.isnan(C[f"pleiades-rho05:loglik:H/rho4-0/equal/{GLORYS}"]).sum()),
                      "hydro_nonfinite_rows": int((~np.isfinite(C["hydroacoustics:loglik"])).sum()),
                      "seabed_nan_rows": int(np.isnan(C["seabed-search:loglik"]).sum()),
                      "unpowered_excluded_rows": int(np.isinf(unp).sum()), "over_212_rows": int((speed > SPEED_CAP).sum())},
           "hydro_station_means": {k: float(np.mean(v)) for k, v in th.items()},
           "provenance": {"impacts32_sha256_listed": (sd / "SHA256SUMS").read_text().split()[0],
                          "compact_impacts_sha256": sha(EOF_SMOKE / "compact_impacts.py"), "displacement_hist_sha256": sha(EOF_SMOKE / "displacement_hist.py"),
                          "drift_SHA256SUMS": (DRIFT / stratum / f"seed-{seed}" / "SHA256SUMS").read_text().split()[0],
                          "pleiades_reader_sha256": sha(PLEI / "reader.py"), "lhyd_sha256": sha(HYDRO_SCRIPTS / "lhyd.py"),
                          "hydro_module_commit": "3b5b4446 (hydro-wt worktree, read-only)", "blackman_offsets": {k: BN_OFF[k] for k in ("H01W", "H08S")},
                          "seabed_loglik_sha256": sha(HERE / "seabed_loglik.py")},
           "seconds": round(time.time() - t0, 1)}
    (outd / f"seed-{seed}.json").write_text(json.dumps(hdr, indent=1))
    print(stratum, seed, n, hdr["seconds"], "s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3])
