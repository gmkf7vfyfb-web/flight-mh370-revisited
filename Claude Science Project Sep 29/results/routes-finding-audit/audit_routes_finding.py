"""Independent audit (architecture) of core's routes finding, 11 Oct 2026.

Read-only on core's code and outputs. Reproduces every number in
results/routes-finding-audit-architecture.md from:
  - engine/data/waypoints.csv (this branch)                      -> geometry
  - core run D run.json / routes.npy (mh370-exchange/core/next-run-d)
  - core route pilots run.json (core workspace out/route-pilot, out/route-pilot-tb)
  - core sampler smoke run.json (core workspace out/ts/runs), run E run.json
  - audit control smoke (pseudo-fix runs, 50k particles, this audit) in SMOKE dir
Usage: python audit_routes_finding.py <core_workspace_out> <exchange_run_d> <smoke_runs> <out_dir>
"""
import json, os, sys, datetime as dt
import numpy as np, pandas as pd, pyproj
from scipy.special import logsumexp

P, E, SM, OUT = sys.argv[1:5]
HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "engine")
g = pyproj.Geod(ellps="WGS84")
R_NM = 3440.065
load = lambda p: json.load(open(p))

# ---------------------------------------------------------------- 1. geometry
wp = pd.read_csv(os.path.join(ENGINE, "data", "waypoints.csv")).set_index("name")
pt = lambda n: wp.loc[n, ["lat_deg", "lon_deg"]].values.astype(float)


def fwd(A, B):
    a, b = pt(A), pt(B)
    az1, az2, d = g.inv(a[1], a[0], b[1], b[0])
    return az1 % 360, (az2 + 180) % 360, d / 1852


first = [["VAMPI", "MEKAR", "NILAM", "IGOGU"], ["VAMPI", "MEKAR", "NILAM", "ANOKO"], ["VAMPI", "MEKAR", "NILAM", "SAMAK"],
         ["VAMPI", "MEKAR", "NILAM", "NOPEK"], ["VAMPI", "MEKAR", "NILAM", "LAGOG"], ["VAMPI", "MEKAR", "SAMAK"]]
then = [[], ["BEDAX"], ["BULVA"], ["ISBIX"], ["POSOD"], ["MUTMI"], ["PIPOV"], ["BEBIM"]]
rows = []
for fi, f in enumerate(first):
    for ti, t in enumerate(then):
        rt = f + t
        legs = [fwd(rt[i], rt[i + 1]) for i in range(len(rt) - 1)]
        turns = [((legs[i][0] - legs[i - 1][1] + 180) % 360) - 180 for i in range(1, len(legs))]
        rows.append(dict(route=fi * 8 + ti, name="-".join(rt),
                         last_leg_initial_bearing=legs[-1][0], last_leg_nm=legs[-1][2],
                         turn_into_last_leg_deg=turns[-1] if t else np.nan,
                         old_rule_flown=(not t) or abs(turns[-1]) < 90))
geo = pd.DataFrame(rows)
ev_tb = pd.read_csv(os.path.join(P, "route-pilot-tb", "route-pilot-turnbacks-evidence.csv"))
ev_old = pd.read_csv(os.path.join(P, "route-pilot", "route-pilot-evidence.csv"))
geo = geo.merge(ev_tb[["route", "logZ_s1", "logZ_s2", "logZ_mean", "spread", "P_route", "formerly_skipped", "median_0019"]], on="route")
geo = geo.merge(ev_old[["route", "logZ_mean"]].rename(columns={"logZ_mean": "logZ_mean_old_rule"}), on="route")
geo["geometry_predicts_skip_matches_core"] = (~geo.old_rule_flown) == (geo.formerly_skipped == 1)
geo.to_csv(os.path.join(OUT, "route-geometry-and-evidence.csv"), index=False, float_format="%.4f")

legs = []
for A, B in [("VAMPI", "MEKAR"), ("MEKAR", "NILAM"), ("NILAM", "ANOKO"), ("ANOKO", "ISBIX"), ("ANOKO", "BULVA"),
             ("NILAM", "IGOGU"), ("IGOGU", "ISBIX"), ("IGOGU", "BULVA"), ("NILAM", "NOPEK"), ("NOPEK", "ISBIX"), ("ANOKO", "BEDAX")]:
    i, f_, d = fwd(A, B)
    legs.append(dict(leg=f"{A}->{B}", initial_bearing_deg=i, final_bearing_deg=f_, distance_nm=d))
legs = pd.DataFrame(legs)
legs.to_csv(os.path.join(OUT, "leg-geometry-wgs84.csv"), index=False, float_format="%.3f")

# ---------------------------------------------------------------- 2. same-data check
D = {s: load(os.path.join(E, f"next-d-{s}", "run.json")) for s in ["free", "routes", "repro-radar", "descent-climb"]}
T = {k: load(os.path.join(P, "route-pilot-tb", f"route-{k}", "run.json")) for k in [11, 10, 3, 2, 27, 8]}
O = {k: load(os.path.join(P, "route-pilot", f"route-{k}", "run.json")) for k in [27, 8]}
same = {}
for key in ["observations", "epochs", "hypotheses", "prior", "prior_unix_s", "reference_arcs", "stop"]:
    ref = json.dumps(D["free"][key], sort_keys=True)
    same[key] = all(json.dumps(x[key], sort_keys=True) == ref for x in list(D.values()) + list(T.values()) + list(O.values()))


def flat(d, pre=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flat(v, f"{pre}.{k}" if pre else k))
    elif isinstance(d, list) and all(not isinstance(i, (dict, list)) for i in d):
        out[pre] = tuple(d)
    elif isinstance(d, list):
        for i, v in enumerate(d):
            out.update(flat(v, f"{pre}[{i}]"))
    else:
        out[pre] = d
    return out


fa, fb = flat(D["routes"]["config"]), flat(T[11]["config"])
cfg_diff = sorted(k for k in set(fa) | set(fb) if fa.get(k) != fb.get(k))
lme = lambda v: float(logsumexp(v) - np.log(len(v)))
evid = []
for nm, x in [("run D free", D["free"]), ("run D routes (old rule)", D["routes"]), ("run D Davey dynamics + radar", D["repro-radar"]),
              ("run D descent-climb", D["descent-climb"])] + [(f"pilot turn-backs route {k}", v) for k, v in T.items()] + \
             [(f"pilot old rule route {k}", v) for k, v in O.items()]:
    le = [rp["log_evidence"] for rp in x["replicates"]]
    evid.append(dict(run=nm, build=x["code_revision"], particles=sum(x["replicates"][0]["particles_per_mode"]),
                     seeds=len(le), logZ_per_seed=";".join(f"{v:.3f}" for v in le), logZ_logmeanexp=lme(le),
                     seed_sd=float(np.std(le, ddof=1)), sampler_target_ess=x["config"]["sampler"].get("temper_target_ess"),
                     lookahead_resamples=sum(m["lookahead_resamples"] for rp in x["replicates"] for m in rp["modes"])))
TS = os.path.join(P, "ts", "runs")
for nm in ["e16-free", "ad50-free", "e16-routes", "ad50-routes"]:
    x = load(os.path.join(TS, f"ts-{nm}", "run.json"))
    le = [rp["log_evidence"] for rp in x["replicates"]]
    evid.append(dict(run=f"sampler smoke {nm} (quarter scale)", build=x["code_revision"], particles=sum(x["replicates"][0]["particles_per_mode"]),
                     seeds=len(le), logZ_per_seed=";".join(f"{v:.3f}" for v in le), logZ_logmeanexp=lme(le),
                     seed_sd=float(np.std(le, ddof=1)), sampler_target_ess=x["config"]["sampler"].get("temper_target_ess"), lookahead_resamples=0))
evid = pd.DataFrame(evid)
evid.to_csv(os.path.join(OUT, "evidence-by-run.csv"), index=False, float_format="%.3f")

# ---------------------------------------------------------------- 3. per-epoch decomposition


def epoch_decomp(x):
    eps = [e["epoch"] for e in x["replicates"][0]["modes"][0]["epochs"]]
    reps = []
    for rp in x["replicates"]:
        M = np.array([[e["log_evidence_increment"] for e in m["epochs"]] for m in rp["modes"]])
        pw = np.array([m["prior_weight"] for m in rp["modes"]]); pw = pw / pw.sum()
        mix = logsumexp(np.cumsum(M, axis=1) + np.log(pw)[:, None], axis=0)
        reps.append(np.diff(np.concatenate([[0], mix])))
    return eps, np.array(reps).mean(0)


cols = {}
for nm, x in [("route 11 NILAM-ANOKO-ISBIX", T[11]), ("route 10 NILAM-ANOKO-BULVA", T[10]), ("route 3 NILAM-IGOGU-ISBIX", T[3]),
              ("route 27 NILAM-NOPEK-ISBIX", T[27]), ("run D free", D["free"]), ("run D routes (old rule)", D["routes"]),
              ("run D Davey dynamics + radar", D["repro-radar"]), ("run D descent-climb", D["descent-climb"])]:
    eps, inc = epoch_decomp(x); cols[nm] = inc
ep = pd.DataFrame(cols, index=eps)
ep["route 11 minus free"] = ep["route 11 NILAM-ANOKO-ISBIX"] - ep["run D free"]
ep["route 11 minus route 27"] = ep["route 11 NILAM-ANOKO-ISBIX"] - ep["route 27 NILAM-NOPEK-ISBIX"]
ep.loc["TOTAL"] = ep.sum()
ep.to_csv(os.path.join(OUT, "per-epoch-log-evidence.csv"), float_format="%.3f")

# ---------------------------------------------------------------- 4. family prior sensitivity
lzR = float(logsumexp(ev_tb.logZ_mean.values) - np.log(48))
others = np.array([evid.set_index("run").loc[k, "logZ_logmeanexp"] for k in ["run D free", "run D Davey dynamics + radar", "run D descent-climb"]])
sens = []
for pi in [0.25, 0.1, 0.05, 1 / 48, 0.01, 0.005]:
    w = np.concatenate([[np.log(pi) + lzR], np.log((1 - pi) / 3) + others]); p = np.exp(w - logsumexp(w))
    sens.append(dict(routes_family_prior=pi, P_routes=p[0], P_free=p[1], P_davey_radar=p[2], P_descent_climb=p[3]))
pd.DataFrame(sens).to_csv(os.path.join(OUT, "family-prior-sensitivity.csv"), index=False, float_format="%.4f")

# ---------------------------------------------------------------- 5. posterior paths: free reaches the same turn south
t0 = D["free"]["prior_unix_s"]; times = t0 + 600 * np.arange(38)


def to_xyz(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)


def xtrack(lat, lon, poly):
    Pp = to_xyz(lat, lon); best = np.full(lat.shape, np.inf)
    for (la1, lo1), (la2, lo2) in zip(poly[:-1], poly[1:]):
        A = to_xyz(la1, lo1); B = to_xyz(la2, lo2); n = np.cross(A, B); n /= np.linalg.norm(n)
        s = Pp @ n; xt = np.abs(np.arcsin(np.clip(s, -1, 1))) * R_NM
        pr = Pp - s[..., None] * n; pr /= np.linalg.norm(pr, axis=-1, keepdims=True)
        ab = np.arccos(np.clip(A @ B, -1, 1)); inside = np.abs(np.arccos(np.clip(pr @ A, -1, 1)) + np.arccos(np.clip(pr @ B, -1, 1)) - ab) < 1e-6
        dA = np.arccos(np.clip(Pp @ A, -1, 1)) * R_NM; dB = np.arccos(np.clip(Pp @ B, -1, 1)) * R_NM
        best = np.minimum(best, np.where(inside, xt, np.minimum(dA, dB)))
    return best


def seg_tracks(Pa):
    az, _, d = g.inv(Pa[:, :-1, 1].ravel(), Pa[:, :-1, 0].ravel(), Pa[:, 1:, 1].ravel(), Pa[:, 1:, 0].ravel())
    return (az % 360).reshape(Pa.shape[0], -1)


paths = {}
for s in ["free", "routes", "repro-radar"]:
    paths[s] = np.concatenate([np.load(os.path.join(E, f"next-d-{s}", "bto-bfo", f"seed-{k}", "routes.npy")) for k in range(1, 5)])
a11 = os.path.join(SM, "a-ANOKO", "bto-bfo", "seed-1", "routes.npy")
if os.path.exists(a11):
    paths["route 11 (audit smoke)"] = np.load(a11)
poly = {n: [tuple(pt(x)) for x in n.split("-")] for n in ["VAMPI-MEKAR-NILAM-ANOKO-ISBIX", "VAMPI-MEKAR-NILAM-NOPEK-ISBIX"]}
pp = []
for s, Pa in paths.items():
    trk = seg_tracks(Pa)
    for k in range(1, 11):
        r = dict(stratum=s, utc=dt.datetime.utcfromtimestamp(times[k]).strftime("%H:%M"),
                 lat_median=np.median(Pa[:, k, 0]), lon_median=np.median(Pa[:, k, 1]),
                 next10min_track_p10=np.percentile(trk[:, k], 10), next10min_track_p50=np.percentile(trk[:, k], 50),
                 next10min_track_p90=np.percentile(trk[:, k], 90))
        for n, pl in poly.items():
            xt = xtrack(Pa[:, k, 0], Pa[:, k, 1], pl)
            r[f"xtrack_to_{n.split('-')[3]}_ISBIX_nm_p10"] = np.percentile(xt, 10)
            r[f"xtrack_to_{n.split('-')[3]}_ISBIX_nm_p50"] = np.median(xt)
            r[f"frac_within_3nm_of_{n.split('-')[3]}_ISBIX"] = float(np.mean(xt < 3.0))
        pp.append(r)
pp = pd.DataFrame(pp)
pp.to_csv(os.path.join(OUT, "posterior-paths-vs-route-lines.csv"), index=False, float_format="%.3f")

# ---------------------------------------------------------------- 6. Occam estimate for free (prior of the turn south)
rng = np.random.default_rng(0)
tau_min = np.exp(rng.uniform(np.log(0.1), np.log(10.0), 400000)) * 60.0  # Davey tau prior: log-uniform 0.1-10 h
occ = []
for W in [3, 5, 10]:
    tc = 35.0  # minutes after 18:01:49 (turn near 18:37)
    p_time = float(np.mean(np.exp(-(tc - W / 2) / tau_min) - np.exp(-(tc + W / 2) / tau_min)))
    for dh in [2, 4, 8]:
        occ.append(dict(window_min=W, heading_width_deg=dh, P_first_random_turn_in_window=p_time,
                        P_turn_and_heading=p_time * dh / 360, ln_P=np.log(p_time * dh / 360)))
pd.DataFrame(occ).to_csv(os.path.join(OUT, "free-turn-prior-occam-estimate.csv"), index=False, float_format="%.4g")

# ---------------------------------------------------------------- 7. audit control smoke (pseudo-fixes)
ctl = []
if os.path.isdir(SM):
    aw = pd.read_csv(os.path.join(SM, "..", "audit-waypoints.csv")).set_index("name")
    for run in sorted(os.listdir(SM)):
        rj = os.path.join(SM, run, "run.json")
        if not os.path.exists(rj):
            continue
        x = load(rj)
        fx = x["config"]["dynamics"]["early"]["routes"]["first"][0][-1]
        offs = 0.0 if fx == "ANOKO" else (int(fx[2:]) * (1 if fx[1] == "E" else -1))
        eps, inc = epoch_decomp(x)
        for rp in x["replicates"]:
            ctl.append(dict(run=run, fix=fx, offset_east_of_ANOKO_nm=offs, lat=aw.loc[fx, "lat_deg"], lon=aw.loc[fx, "lon_deg"],
                            seed=rp["seed"], logZ=rp["log_evidence"], build=x["code_revision"],
                            particles=sum(rp["particles_per_mode"])))
ctl = pd.DataFrame(ctl)
if len(ctl):
    ctl.sort_values(["offset_east_of_ANOKO_nm", "seed"]).to_csv(os.path.join(OUT, "pseudo-fix-control-smoke.csv"), index=False, float_format="%.4f")

json.dump(dict(same_fields=same, config_keys_differing_routesD_vs_pilot11=cfg_diff, routes_family_logZ_turnbacks=lzR),
          open(os.path.join(OUT, "same-data-check.json"), "w"), indent=1)
print("ok", len(geo), len(evid), len(pp), len(ctl))
