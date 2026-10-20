"""Fuel feasibility of a fuel-TRACKED, unconstrained posterior (core order 2026-10-15b step 3).
Standard library only (deskstar's python3 has no numpy).
usage: python3 fuel_feasibility.py <run dir> [case] > out.json
Pools rows as weight x mode_probability[stratum] / (sum of weight in that stratum) / n_replicates
(equal seed pooling, as summary.json does). Times are seconds after 2014-03-08 00:00:00 UTC, read from
final.npy's fuel_exhausted_s_after_0000 (F12: never the float32 unix column). NaN = still
holding fuel at the final step (00:19:37). If tanks.npy (f8) or tanks32.npy (f4) is present the
first-engine flame-out is reported too."""
import sys, os, json, ast, struct, math
from array import array
T0 = 1394236800.0
M0011, M0019A, M0019B = 659.0, 1169.0, 1177.0   # 00:10:59, 00:19:29, 00:19:37 (epoch times)
COLS = ["weight", "latitude_deg", "longitude_deg", "altitude_ft", "mach", "tau_h", "turns", "accelerations",
        "climbs", "mode", "bfo_bias_hz", "origin", "stratum", "fuel_kg", "fuel_exhausted_unix_s",
        "fuel_below_tables_s", "fuel_extrapolated_s", "fuel_above_ceiling_s", "fuel_no_flow_s",
        "fuel_no_flow_cause", "fuel_exhausted_s_after_0000"]
def read_npy(path):
    with open(path, "rb") as f:
        assert f.read(6) == b"\x93NUMPY"; major = f.read(2)[0]
        n = struct.unpack("<H" if major == 1 else "<I", f.read(2 if major == 1 else 4))[0]
        hdr = ast.literal_eval(f.read(n).decode("latin1"))
        a = array({"<f8": "d", "<f4": "f"}[hdr["descr"]]); a.frombytes(f.read())
    assert not hdr["fortran_order"]
    return a, hdr["shape"]
def hhmmss(s):
    if s is None or not math.isfinite(s): return "after 00:19:37 (fuel left)"
    t = int(round(s)) % 86400; return "%02d:%02d:%02d" % (t // 3600, t // 60 % 60, t % 60)
def wquant(pairs, qs):
    pairs = sorted(pairs); tot = sum(w for _, w in pairs); out = []; acc = 0.0; i = 0
    for q in qs:
        while i < len(pairs) and acc + pairs[i][1] < q * tot: acc += pairs[i][1]; i += 1
        out.append(pairs[min(i, len(pairs) - 1)][0])
    return out
def shares(pairs, extra):
    tot = sum(w for _, w in pairs)
    def sh(f): return sum(w for t, w in pairs if f(t)) / tot
    r = {"mass": tot,
         "dry_before_0010_59": sh(lambda t: t < M0011),
         "dry_0010_59_to_0019_29_arcs6_7": sh(lambda t: M0011 <= t <= M0019A),
         "dry_0019_29_to_0019_37": sh(lambda t: M0019A < t <= M0019B),
         "fuel_left_at_0019_37": sh(lambda t: not (t <= M0019B))}
    r["feasible_power_at_0010_59"] = 1.0 - r["dry_before_0010_59"]
    q = wquant([(t if math.isfinite(t) else 1e9, w) for t, w in pairs], [0.05, 0.5, 0.95])
    r["fe_quantiles_all_mass"] = {k: (v if v < 1e8 else None) for k, v in zip(["q05", "q50", "q95"], q)}
    r["fe_quantiles_all_mass_utc"] = {k: hhmmss(v if v < 1e8 else None) for k, v in zip(["q05", "q50", "q95"], q)}
    dry = [(t, w) for t, w in pairs if math.isfinite(t)]
    if dry:
        qd = wquant(dry, [0.05, 0.5, 0.95])
        r["fe_quantiles_dry_by_0019_37_utc"] = {k: hhmmss(v) for k, v in zip(["q05", "q50", "q95"], qd)}
    r.update({k: v / tot for k, v in extra.items()})
    return r
run = sys.argv[1]; case = sys.argv[2] if len(sys.argv) > 2 else "bto-bfo"
summ = json.load(open(os.path.join(run, "summary.json")))
c = [x for x in summ["cases"] if x["case"] == case][0]
reps = c["replicates"]; n = len(reps); pooled = []; pex = {}; per_seed = []; first_pooled = []
for rep in reps:
    d = os.path.join(run, case, "seed-%d" % rep["seed"])
    a, shape = read_npy(os.path.join(d, "final.npy")); nc = shape[1]; assert nc == len(COLS), shape
    mp = rep["mode_probability"]; rows = shape[0]
    W = a[0::nc]; S = a[12::nc]; FE = a[20::nc]; CEIL = a[17::nc]; EXT = a[16::nc]; NOF = a[18::nc]
    wsum = [0.0] * len(mp); pairs = []; ex = {"above_ceiling_any": 0.0, "extrapolated_any": 0.0, "no_flow_any": 0.0}
    for i in range(rows):
        wsum[int(S[i])] += W[i]
    # final.npy's weight already sums to mode_probability within each mode (checked 15 Oct on
    # davey2016-inmarsat and run I repro); rescaling by mp / wsum is correct under either convention.
    scale = [(mp[m] / wsum[m]) if wsum[m] > 0 else 0.0 for m in range(len(mp))]
    for i in range(rows):
        s = int(S[i]); pw = W[i] * scale[s]
        pairs.append((FE[i], pw))
        if CEIL[i] > 0: ex["above_ceiling_any"] += pw
        if EXT[i] > 0: ex["extrapolated_any"] += pw
        if NOF[i] > 0: ex["no_flow_any"] += pw
    first = None
    for tn, code, toff in (("tanks.npy", "d", T0), ("tanks32.npy", "f", 0.0)):
        p = os.path.join(d, tn)
        if os.path.exists(p):
            t, ts = read_npy(p); assert ts[0] == rows
            first = [(t[5 + 8 * i] - toff, pairs[i][1]) for i in range(rows)]; break
    rs = shares(pairs, ex); rs["seed"] = rep["seed"]; rs["rows"] = rows
    rs["within_mode_weight_sums"] = wsum; rs["mode_probability"] = mp; rs["log_evidence"] = rep["log_evidence"]
    if first:
        rs["first_engine"] = shares(first, {}); first_pooled += [(t, w / n) for t, w in first]
    per_seed.append(rs); pooled += [(t, w / n) for t, w in pairs]
    for k, v in ex.items(): pex[k] = pex.get(k, 0.0) + v / n
out = {"run": run, "case": case, "replicates": n, "log_evidence": c["log_evidence"], "pooled": shares(pooled, pex), "per_seed": per_seed}
if first_pooled: out["pooled_first_engine"] = shares(first_pooled, {})
k = "dry_before_0010_59"; v = [r[k] for r in per_seed]; m = sum(v) / n
out["pooled"]["dry_before_0010_59_seed_sd"] = (sum((x - m) ** 2 for x in v) / (n - 1)) ** 0.5 if n > 1 else None
print(json.dumps(out, indent=1))
