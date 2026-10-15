"""Core request 20 Phase 1 smoke: dedupe, pilot g, scoring and prior recovery. Standard library only.
  dedupe_chunks <handoff dir> <root> <seed dir name> <chunk>   distinct rows in chunks -> root/c<i>/bto-bfo/<seed dir>/
  graw <pilot run> <pilot seed> <map.json> <out.json>          per-row ln G per arm (absolute log scale)
  gmerge <graw jsons, comma-sep> <N per mode csv> <out dir> <name seed>   per-particle g files + g-summary
  dedupe <handoff dir> <out dir>           distinct (mode, particle) rows -> out/handoff.toml + out/map.json
  g <pilot run dir> <pilot seed> <map.json> <N per mode csv> <out dir> [name seed]   per-particle g files + g-summary.json
  score <terminal run dir> <seed> <handoff dir> <label>            effective parents / impacts per arm (json)
  prior <handoff dir before> <handoff dir after>                   corrected-mean recovery (json)
Arms targeted (both bursts, BFO models no-offset and startup-offset; log-on cause 'other' = no time term)."""
import sys, os, json, ast, struct, math, re
from array import array
ARMS = ["both/no-offset", "both/startup-offset"]
EXTRA_ARMS = ["both/inflated", "r600/no-offset", "r1200/no-offset", "r1200/startup-offset"]
MODES = ["TrueHeading", "MagneticHeading", "TrueTrack", "MagneticTrack", "LateralNavigation"]
def read_npy(path):
    with open(path, "rb") as f:
        assert f.read(6) == b"\x93NUMPY"; major = f.read(2)[0]
        n = struct.unpack("<H" if major == 1 else "<I", f.read(2 if major == 1 else 4))[0]
        hdr = ast.literal_eval(f.read(n).decode("latin1"))
        a = array({"<f8": "d", "<f4": "f"}[hdr["descr"]]); count = 1
        for d in hdr["shape"]: count *= d
        a.fromfile(f, count)
    return a, hdr["shape"]
def write_npy(path, values):
    a = array("d", values); h = "{'descr': '<f8', 'fortran_order': False, 'shape': (%d, 1), }" % len(a)
    h += " " * (63 - (10 + len(h)) % 64) + "\n"
    with open(path, "wb") as f: f.write(b"\x93NUMPY\x01\x00" + struct.pack("<H", len(h)) + h.encode("latin1")); f.write(a.tobytes())
def ess(ws):
    s = sum(ws); s2 = sum(w * w for w in ws); return s * s / s2 if s2 > 0 else 0.0
def dedupe_chunks(src, root, seeddir, chunk):
    """Distinct (mode, particle) rows, written in chunks of `chunk` rows: root/c<i>/bto-bfo/<seeddir>/."""
    t = open(os.path.join(src, "handoff.toml")).read()
    head, *rows = t.split("\n[[row]]\n"); seen = set(); keep = []; mp = []
    for r in rows:
        m = int(re.search(r"^mode = (\d+)$", r, re.M).group(1)); p = int(re.search(r"^particle = (\d+)$", r, re.M).group(1))
        if (m, p) in seen: continue
        seen.add((m, p)); keep.append(r); mp.append([m, p])
    del t, rows
    n = 0
    for i in range(0, len(keep), chunk):
        part = keep[i:i + chunk]; w = 1.0 / len(part)
        part = [re.sub(r"^weight = .*$", "weight = %r" % w, r, count=1, flags=re.M) for r in part]
        d = os.path.join(root, "c%d" % n, "bto-bfo", seeddir); os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "handoff.toml"), "w") as f: f.write(head + "".join("\n[[row]]\n" + r for r in part))
        json.dump({"chunk": n, "rows": mp[i:i + chunk]}, open(os.path.join(d, "map.json"), "w")); n += 1
    print(json.dumps({"distinct": len(keep), "chunks": n}))
def graw(run, seed, mapf, out):
    """Per-row ln G for each targeted arm (G = sum over the row's descents of weight x likelihood), on an absolute log scale."""
    mp = json.load(open(mapf))["rows"]; pp, P, W, n = per_parent(run, seed, ARMS); D = len(mp); res = {"rows": mp, "descents": n, "lnG": {}}
    for arm, (P, W, L, c) in pp.items():
        g = [0.0] * D
        for i in range(n): g[int(P[i])] += W[i] * L[i]
        res["lnG"][arm] = [(math.log(x) + c) if x > 0 else None for x in g]
    json.dump(res, open(out, "w"))
def gmerge(parts, ncsv, out, name_seed):
    N = [int(x) for x in ncsv.split(",")]; mp = []; lnG = {}; descents = 0
    for f in parts.split(","):
        r = json.load(open(f)); mp += r["rows"]; descents += r["descents"]
        for a, v in r["lnG"].items(): lnG.setdefault(a, []).extend(v)
    D = len(mp); summary = {"distinct": D, "descents": descents, "arms": {}}; G = {}
    for a, v in lnG.items():
        top = max(x for x in v if x is not None) if any(x is not None for x in v) else 0.0
        g = [math.exp(x - top) if x is not None else 0.0 for x in v]; mean = sum(g) / D
        G[a] = [x / mean for x in g] if mean > 0 else g
        summary["arms"][a] = {"parents_with_any_hit": sum(1 for x in g if x > 0), "ess_over_distinct": ess(g), "max_share": max(g) / sum(g) if sum(g) > 0 else None}
    gm = [sum(G[a][u] for a in G) / len(G) for u in range(D)]
    summary["mixture"] = {"ess_over_distinct": ess(gm), "positive": sum(1 for x in gm if x > 0)}
    os.makedirs(out, exist_ok=True)
    for m in range(len(N)):
        vv = [0.0] * N[m]
        for u, (mm, p) in enumerate(mp):
            if mm == m: vv[p] = gm[u]
        write_npy(os.path.join(out, "g-%d-%s.npy" % (name_seed, MODES[m])), vv)
        summary.setdefault("per_mode_distinct", {})[MODES[m]] = sum(1 for mm, _ in mp if mm == m)
    json.dump(summary, open(os.path.join(out, "g-summary-%d.json" % name_seed), "w"), indent=1); print(json.dumps(summary))
def dedupe(src, out):
    t = open(os.path.join(src, "handoff.toml")).read()
    head, *rows = t.split("\n[[row]]\n"); seen = {}; keep = []
    for r in rows:
        m = int(re.search(r"^mode = (\d+)$", r, re.M).group(1)); p = int(re.search(r"^particle = (\d+)$", r, re.M).group(1))
        if (m, p) in seen: continue
        seen[(m, p)] = len(keep); keep.append(r)
    w = 1.0 / len(keep)
    keep = [re.sub(r"^weight = .*$", "weight = %r" % w, r, count=1, flags=re.M) for r in keep]
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "handoff.toml"), "w") as f: f.write(head + "".join("\n[[row]]\n" + r for r in keep))
    json.dump({"source_rows": len(rows), "distinct": len(keep), "rows": [[m, p] for (m, p), _ in sorted(seen.items(), key=lambda kv: kv[1])]}, open(os.path.join(out, "map.json"), "w"))
    print(json.dumps({"source_rows": len(rows), "distinct": len(keep)}))
def load_impacts(run, seed):
    cols = json.load(open(os.path.join(run, "run.json")))["impact_columns"]
    a, shape = read_npy(os.path.join(run, "bto-bfo", "seed-%d" % seed, "impacts.npy")); w = shape[1]; assert w == len(cols), (w, len(cols))
    return a, shape[0], w, cols
def per_parent(run, seed, arms):
    a, n, w, cols = load_impacts(run, seed); P = a[cols.index("parent")::w]; W = a[cols.index("weight")::w]
    out = {}
    for arm in arms:
        name = "loglik:" + arm
        if name not in cols: continue
        L = a[cols.index(name)::w]; fin = [x for x in L if x > -1e300 and not math.isnan(x)]
        c = max(fin) if fin else 0.0
        out[arm] = (P, W, [math.exp(x - c) if (x > -1e300 and not math.isnan(x)) else 0.0 for x in L], c)
    return out, P, W, n
def g_cmd(run, seed, mapf, ncsv, out, name_seed=None):
    name_seed = seed if name_seed is None else name_seed
    mp = json.load(open(mapf))["rows"]; N = [int(x) for x in ncsv.split(",")]
    pp, P, W, n = per_parent(run, seed, ARMS); D = len(mp); summary = {"distinct": D, "descents": n, "arms": {}}
    G = {}
    for arm, (P, W, L, c) in pp.items():
        g = [0.0] * D
        for i in range(n): g[int(P[i])] += W[i] * L[i]
        mean = sum(g) / D; G[arm] = [x / mean for x in g] if mean > 0 else g
        pos = sum(1 for x in g if x > 0)
        summary["arms"][arm] = {"parents_with_any_hit": pos, "ess_over_distinct": ess(g), "max_share": max(g) / sum(g) if sum(g) > 0 else None, "log_scale": c}
    gm = [sum(G[a][u] for a in G) / len(G) for u in range(D)]
    summary["mixture"] = {"ess_over_distinct": ess(gm), "positive": sum(1 for x in gm if x > 0)}
    os.makedirs(out, exist_ok=True)
    for m in range(len(N)):
        v = [0.0] * N[m]
        for u, (mm, p) in enumerate(mp):
            if mm == m: v[p] = gm[u]
        write_npy(os.path.join(out, "g-%d-%s.npy" % (name_seed, MODES[m])), v)
        summary.setdefault("per_mode_distinct", {})[MODES[m]] = sum(1 for mm, _ in mp if mm == m)
    json.dump(summary, open(os.path.join(out, "g-summary-%d.json" % name_seed), "w"), indent=1); print(json.dumps(summary))
def score_cmd(run, seed, hdir, label):
    pp, P, W, n = per_parent(run, seed, ARMS + EXTRA_ARMS + ["none"])
    res = {"label": label, "descents": n, "weight_sum": sum(W), "arms": {}}
    parents = {}
    for i in range(n): parents[int(P[i])] = parents.get(int(P[i]), 0.0) + W[i]
    res["arms"]["none"] = {"effective_parents": ess(list(parents.values())), "effective_impacts": ess(list(W))}
    for arm, (P, W, L, c) in pp.items():
        wl = [W[i] * L[i] for i in range(n)]; par = {}
        for i in range(n): par[int(P[i])] = par.get(int(P[i]), 0.0) + wl[i]
        v = sorted(par.values(), reverse=True); tot = sum(v)
        res["arms"][arm] = {"effective_parents": ess(v), "effective_impacts": ess(wl), "top100_parent_share": sum(v[:100]) / tot if tot > 0 else None,
                            "ln_increment": (math.log(tot) + c) if tot > 0 else None}
    print(json.dumps(res))
def hmeans(hdir):
    a, shape = read_npy(os.path.join(hdir, "handoff.npy")); w = shape[1]; W = list(a[0::w])
    if w == 14: W = [x * math.exp(lc) for x, lc in zip(W, a[13::w])]
    cols = {"latitude_deg": 1, "longitude_deg": 2, "altitude_ft": 3, "mach": 4, "tau_h": 5, "bfo_bias_hz": 8}
    s = sum(W); out = {"weight_sum": s, "ess": ess(W)}
    for k, j in cols.items():
        x = a[j::w]; m = sum(wi * xi for wi, xi in zip(W, x)) / s; v = sum(wi * (xi - m) ** 2 for wi, xi in zip(W, x)) / s
        out[k] = (m, v)
    return out
def prior_cmd(before, after):
    b, a = hmeans(before), hmeans(after); res = {"before_ess": b["ess"], "after_ess": a["ess"], "after_weight_sum": a["weight_sum"], "vars": {}}
    for k in b:
        if k in ("weight_sum", "ess"): continue
        (mb, vb), (ma, va) = b[k], a[k]; sd = math.sqrt(vb)
        se = math.sqrt(vb / b["ess"] + va / a["ess"])
        res["vars"][k] = {"before": mb, "after": ma, "standardised_deviation": (ma - mb) / sd if sd > 0 else 0.0, "z": (ma - mb) / se if se > 0 else 0.0}
    print(json.dumps(res))
cmd = sys.argv[1]
if cmd == "dedupe_chunks": dedupe_chunks(sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]))
elif cmd == "graw": graw(sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5])
elif cmd == "gmerge": gmerge(sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]))
elif cmd == "dedupe": dedupe(sys.argv[2], sys.argv[3])
elif cmd == "g": g_cmd(sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6], int(sys.argv[7]) if len(sys.argv) > 7 else None)
elif cmd == "score": score_cmd(sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5])
elif cmd == "prior": prior_cmd(sys.argv[2], sys.argv[3])
