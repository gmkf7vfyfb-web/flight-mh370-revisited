"""Run J northern supplement, step 1 (measure first). Per seed of the end-of-flight production pass on run J:
per treatment (D0', D2, D3, D4) and 5-deg band of IMPACT latitude, the band mass, Kish ESS over rows and over
distinct 00:11 parents (band_ess.py definition), at nested subsets of (a) descents per parent and (b) parents,
and per autopilot mode. Masses use end of flight's cell_logmass (competing causes, q = 1/3 as option_table_0019).
    python measure_eof.py EOF_ROOT CORE_ROOT OUT_DIR PART NPARTS
"""
import json, sys, pathlib
import numpy as np
SM = pathlib.Path(sys.argv[6]) if len(sys.argv) > 6 else None
sys.path.insert(0, str(SM))
from compact_impacts import load
from run_i_maps import cell_logmass
STRATA = {"run-j-waypoints": 0.9982, "run-j-free": 0.0013, "run-j-repro-radar": 0.0003, "run-j-descent-climb": 0.0002}
BANDS = np.array([-45., -40., -35., -30., -25., -20., -15.]); NB = len(BANDS) - 1
CELLS = ("D0", "D2", "D3", "D4")
KROWS = (8, 16, 32, 64)        # rows kept per parent (4 descents per child: 2, 4, 8, 16 children)
JPAR = (1, 2, 4, 8)            # parents kept: index % 8 < j

def seeds(root):
    out = []
    for st, P in STRATA.items():
        s = sorted((p for p in (pathlib.Path(root) / st).glob("seed-*") if p.is_dir()), key=lambda p: int(p.name[5:]))
        out += [(st, P, len(s), sd) for sd in s]
    return out

def acc(m, b, par, nb=NB):
    ok = b >= 0
    M = np.bincount(b[ok], m[ok], nb); M2 = np.bincount(b[ok], m[ok] ** 2, nb)
    key = b[ok].astype(np.int64) * 10_000_000 + par[ok]; u, inv = np.unique(key, return_inverse=True); s = np.bincount(inv, m[ok])
    P2 = np.bincount(u // 10_000_000, s ** 2, nb); NP = np.bincount(u // 10_000_000, (s > 0).astype(float), nb)
    return M, M2, P2, NP

def main(eof, core, out, k, n):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    for st, P, K, sd in seeds(eof)[k::n]:
        f = out / f"{st}.{sd.name}.json"
        if f.exists(): continue
        meta, g = load(sd)
        hpath = pathlib.Path(core) / st / "bto-bfo" / sd.name / "handoff-m0011" / "handoff.npy"
        lm = cell_logmass(g, meta, hpath)
        H = np.load(hpath)
        lat = g("latitude_deg"); par = g("parent").astype(np.int64)
        b = np.digitize(lat, BANDS) - 1; b[(b < 0) | (b >= NB)] = -1
        rank = np.arange(len(par)) - np.searchsorted(par, par)     # rows are grouped by parent (checked)
        mode = H[par, 6].astype(int); hlat = H[par, 1]
        hb = np.digitize(hlat, BANDS) - 1; hb[(hb < 0) | (hb >= NB)] = -1
        c = np.log(P / K); R = {"stratum": st, "seed": sd.name, "P": P, "K": K, "rows": int(len(lat)), "parents": int(len(H))}
        for d in CELLS:
            a = lm[d]; m = np.zeros(len(a)); fin = np.isfinite(a); m[fin] = np.exp(c + a[fin])
            R[d] = {"full": [x.tolist() for x in acc(m, b, par)]}
            R[d]["krows"] = {kr: [x.tolist() for x in acc(np.where(rank < kr, m * 64 / kr, 0), b, par)] for kr in KROWS[:-1]}
            R[d]["jpar"] = {j: [x.tolist() for x in acc(np.where(par % 8 < j, m * 8 / j, 0), b, par)] for j in JPAR[:-1]}
            R[d]["by_mode"] = {int(md): [x.tolist() for x in acc(np.where(mode == md, m, 0), b, par)] for md in range(5)}
            # by 00:11 hand-off latitude band (where a core proposal acts)
            R[d]["by_handoff_band"] = [x.tolist() for x in acc(m, hb, par)]
            R[d]["total"] = float(m.sum())
        json.dump(R, open(f, "w"))
        print(st, sd.name, flush=True)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
