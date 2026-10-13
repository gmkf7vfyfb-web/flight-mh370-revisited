"""Composer pass 0: build the row-aligned factor columns the composer reads, for one (stratum, seed) of core (b).

PIPELINE TEST - core (b) unconverged; EoF physics provisional; hydro L_hyd stand-in; GlobCurrent F1; Holland H1/H2 not estimable.
Architecture stand-in glue, not module code. Every factor is the owning module's (or its stand-in's) own arithmetic,
imported read-only; nothing here re-derives a likelihood.

Columns written (row-major float64, one row per impacts.npy row, same order):
  weight, parent, mode, family            hand-off weight, parent, autopilot mode, EoF family_code (1 A1, 2 A2, 3 B, 4 A-then-lost)
  latitude_deg, longitude_deg
  loglik:none+alive                        terminal option 00:19 Held Out under EoF's `alive` constraint (0 or -inf)
  loglik:r600-bto+alive                    terminal option 00:19 R600 BTO Only (EoF derived_logliks) + alive
  debris-drift:loglik:<glorys12 label>     drift GLORYS12 surface, interpolate.rs lookup (score_impacts.lookup); NaN unscored
  hydroacoustics:loglik                    stand-in L_hyd (lhyd.Model.station_terms total, scenario A, KE, rng [20261010, si, k])
  pleiades:loglik:H/rho4-0/equal/<glorys12 label>        lnL_pleiades_glorys12 (Pleiades only); NaN not computed
  pleiades-cosmo:loglik:H/rho4-0/equal/<glorys12 label>  lnL_both_glorys12 (Pleiades + COSMO, one debris field); sensitivity
  seabed-search:loglik                     `mh370 evaluate` with hypotheses/seabed-search/run.toml (rho 0.05)
The "exclude not-computed rows" sensitivity copies (NaN -> -inf, the modules' own convention) are made by the
composer binary in memory, not stored.

Usage: python prep_inputs.py <stratum> <seed> <out_dir> <seabed_loglik.npy>
"""
import hashlib, importlib.util, json, pathlib, sys, time
import numpy as np

EXCH = pathlib.Path("/Users/pete/Downloads/mh370-exchange")
EOF_RUN = EXCH / "end-of-flight/next-run"
PLEI = EXCH / "pleiades/hydro-test/next-run-b"
WS = pathlib.Path("/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces")
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]                       # .../Claude Science Project Sep 29
EOF_3C6319F = WS / "d5fc8d7c-15e5-4858-b15e-9553989a6413/eof-3c6319f/Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke/displacement_hist.py"
EOF_HEAD_COMPACT = REPO / "engine/hypotheses/end-of-flight/smoke/compact_impacts.py"
SATCOM = REPO / "engine/data/satcom-observations.csv"
DRIFT_PILOT = WS / "f90cad13-a26e-40d1-9a16-691b3817aa7b/repo/Claude Science Project Sep 29/engine/hypotheses/debris-drift/prepare/pilot"
DRIFT_RUN = WS / "f90cad13-a26e-40d1-9a16-691b3817aa7b/repo/Claude Science Project Sep 29/engine/runs/debris-drift-production-glorys12/merged"
HYDRO_MOD = WS / "c617e88a-f70d-4d8a-847b-7a608fe526f4/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
HYDRO_SCRIPTS = REPO / "results/hydroacoustics-pleiades-test-standin/standin-scripts"
HYDRO_EVENTS = REPO / "results/hydroacoustics-pleiades-test-standin/imos_events_searched.json"
KADRI_CSV = HYDRO_MOD / "results-data/kadri2a/kadri_table1_geometry.csv"
STRATA = ["next-free", "next-repro-radar", "next-descent-climb", "next-routes"]   # hydro stand-in rng stream order
GLORYS = "glorys12v1+era5-wind10"
EXPECT_SHA = {EOF_3C6319F: "f964a9b9b4a42fe21eb4f34edaf1a014650f4c2ef9339cdb3aa75a6040983169",
              HYDRO_SCRIPTS / "lhyd.py": "5000c56ec514924cd4767eb065d3fd592273f7f7712a4aee2a6ee0ec8a01094f"}
CHUNK = 200_000
WANT = ["weight", "parent", "mode", "unix_s", "latitude_deg", "longitude_deg", "kinetic_energy_j",
        "bto_residual_us:m0019a", "bto_residual_us:m0019b", "latent:onset_mechanism", "latent:control_realised",
        "latent:realised_flameout_unix_s"]


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def read_cols(path, cols, names):
    X = np.load(path, mmap_mode="r"); ix = [cols[n] for n in names]
    out = np.empty((len(names), X.shape[0]))
    for s in range(0, X.shape[0], CHUNK):
        out[:, s:s + CHUNK] = np.asarray(X[s:s + CHUNK])[:, ix].T
    return {n: out[k] for k, n in enumerate(names)}


def main(stratum, seed, outd, seabed_path):
    t0 = time.time()
    for p, h in EXPECT_SHA.items():
        assert sha(p) == h, f"{p}: sha256 changed"
    outd = pathlib.Path(outd); outd.mkdir(parents=True, exist_ok=True)
    sd = EOF_RUN / stratum / f"seed-{seed}"
    meta = json.loads((sd / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    d = read_cols(sd / "impacts.npy", cols, WANT); n = d["weight"].size
    g = lambda nm: d[nm]
    dh = load_module("eof_dh", EOF_3C6319F); dh.SATCOM_CSV = SATCOM
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]
    der = dh.derived_logliks(meta, g, present)
    alive = dh.constraint_log_factor(g, logon, "other", "alive")
    r600 = np.where(np.isfinite(der["r600-bto"]), der["r600-bto"], -np.inf) + alive
    fam = load_module("eof_compact", EOF_HEAD_COMPACT).family_labels(d["latent:onset_mechanism"], d["latent:control_realised"])["family_code"]
    fam_nan = int(np.isnan(fam).sum())
    fam = np.where(np.isnan(fam), 0.0, fam)          # 0 = no family label (counted and reported)

    # Pleiades stand-in columns, row-aligned (checked)
    P = np.load(PLEI / stratum / f"seed-{seed}" / "pleiades-lnL.npy", mmap_mode="r")
    assert len(P) == n and np.array_equal(np.asarray(P["row"]), np.arange(n)), "Pleiades rows not aligned"
    assert np.array_equal(np.asarray(P["parent"]).astype(float), d["parent"]), "Pleiades parent mismatch"
    nc = np.asarray(P["not_computed"]).astype(bool)
    lp = np.where(nc, np.nan, np.asarray(P["lnL_pleiades_glorys12"], float))
    lpc = np.where(nc, np.nan, np.asarray(P["lnL_both_glorys12"], float))

    # Drift GLORYS12 surface, interpolate.rs lookup
    sys.path.insert(0, str(DRIFT_PILOT)); from score_impacts import lookup, surface_arrays
    flag, ll = lookup(*surface_arrays(str(DRIFT_RUN), "ln_l"), d["latitude_deg"], d["longitude_deg"])
    ldrift = np.where(flag == 1, ll, np.nan)

    # Hydro stand-in L_hyd, exactly as rhyd_result.py draws it (rng [20261010, si, k], scenario A, total KE)
    sys.path.insert(0, str(HYDRO_SCRIPTS)); import lhyd
    m = lhyd.Model(str(HYDRO_MOD), str(HYDRO_EVENTS), str(KADRI_CSV))
    th = m.station_terms(d["unix_s"], d["latitude_deg"], d["longitude_deg"], d["kinetic_energy_j"],
                         np.random.default_rng([20261010, STRATA.index(stratum), seed]), "A")
    lhy = np.asarray(th["total"], float)

    lsea = np.load(seabed_path); assert lsea.shape == (n,)
    C = {"weight": d["weight"], "parent": d["parent"], "mode": d["mode"], "family": fam,
         "latitude_deg": d["latitude_deg"], "longitude_deg": d["longitude_deg"],
         "loglik:none+alive": alive, "loglik:r600-bto+alive": r600,
         f"debris-drift:loglik:{GLORYS}": ldrift, "hydroacoustics:loglik": lhy,
         f"pleiades:loglik:H/rho4-0/equal/{GLORYS}": lp, f"pleiades-cosmo:loglik:H/rho4-0/equal/{GLORYS}": lpc,
         "seabed-search:loglik": lsea}
    names = list(C)
    w = d["weight"]; mode = d["mode"].astype(int)
    mass = np.bincount(mode, weights=w, minlength=5)
    with open(outd / f"seed-{seed}.f64", "wb") as f:
        for s in range(0, n, CHUNK):
            np.stack([C[k][s:s + CHUNK] for k in names], axis=1).astype("<f8").tofile(f)
    hdr = {"stratum": stratum, "seed": seed, "rows": n, "columns": names,
           # Interface gap: the m0011 hand-off records no per-(replicate, mode) evidence. Pass 0 uses a common
           # replicate constant (0) so that ln Z_im = ln P_i(m | D<=00:11): equal seed weight within a stratum.
           "modes": [{"prior_weight": 1.0, "log_evidence": (float(np.log(mass[k])) if mass[k] > 0 else None),
                      "posterior_probability": float(mass[k] / mass.sum())} for k in range(5)],
           "weight_sum": float(w.sum()),
           "counts": {"family_unlabelled_rows": fam_nan, "family_code_rows": {str(int(v)): int((fam == v).sum()) for v in np.unique(fam)},
                      "pleiades_not_computed_rows": int(nc.sum()), "drift_flag_rows": {str(k): int((flag == k).sum()) for k in (0, 1, 2)},
                      "hydro_nonfinite_rows": int((~np.isfinite(lhy)).sum()), "seabed_nan_rows": int(np.isnan(lsea).sum()),
                      "alive_dead_rows": int(np.isinf(alive).sum())},
           "provenance": {"displacement_hist_sha256": sha(EOF_3C6319F), "compact_impacts_sha256": sha(EOF_HEAD_COMPACT),
                          "score_impacts_sha256": sha(DRIFT_PILOT / "score_impacts.py"), "drift_nodes_sha256": sha(DRIFT_RUN / "nodes.csv"),
                          "lhyd_sha256": sha(HYDRO_SCRIPTS / "lhyd.py"), "kadri_csv_sha256": sha(KADRI_CSV),
                          "pleiades_lnL_sha256_file": str(PLEI / stratum / f"seed-{seed}" / "SHA256SUMS")},
           "seconds": round(time.time() - t0, 1)}
    (outd / f"seed-{seed}.json").write_text(json.dumps(hdr, indent=1))
    print(stratum, seed, n, hdr["seconds"], "s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
