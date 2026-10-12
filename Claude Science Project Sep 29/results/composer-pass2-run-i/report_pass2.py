"""Composer pass 2 (run I): aggregate the per-quarter compositions into products, mixtures, evidence, ESS and split-half checks.

Stratum level: seeds pooled by evidence (Z_s = mean over seeds of the seed's summed row mass, as option_table_0019).
Mixtures over core families (strata), all labelled "conditional on equal family prior" (core run I: P_core = 0.9982 / 0.0011 /
0.0004 / 0.0002 for waypoints / free / Davey reproduction / descent-climb, the rounded shares end of flight and settling use):
  ruling C (PRIMARY, as pass 1): W_s = P_core(s) Z_s(00:19 cell, flight + EoF) - the module evidence acts within strata;
  all evidence (beside): W_s = P_core(s) Z_s(product).
Regions: 0.1 deg cells, Gaussian smoothing sigma 0.1 deg, highest-density 50 % / 90 % of the in-grid mass, spherical cell areas
(R = 6371.0072 km). Latitude quantiles from the pass-0 latitude grid (0.05 deg, unsmoothed CDF, linear within a bin).
Split-half: areas over three balanced seed partitions ({1-4|5-8}, {odd|even}, {1,3,6,8|2,4,5,7}); medians over all 35.
Usage: python report_pass2.py <work dir> <out dir>
"""
import itertools, json, math, pathlib, sys
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.special import logsumexp
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from compose_quarter import products, pid, G2, LAT2, LON2, NY2, NX2, GMIN, GSTEP, NPTS, DS, CS, LAYERS   # noqa: E402

STRATA = ["next-i-waypoints", "next-i-free", "next-i-repro-radar", "next-i-descent-climb"]
SNAME = {"next-i-waypoints": "waypoints", "next-i-free": "free flight", "next-i-repro-radar": "Davey reproduction", "next-i-descent-climb": "descent-climb"}
PCORE = {"next-i-waypoints": 0.9982, "next-i-free": 0.0011, "next-i-repro-radar": 0.0004, "next-i-descent-climb": 0.0002}
QS = ["1-3", "2-4", "5-7", "6-8"]; QSEEDS = {"1-3": (1, 3), "2-4": (2, 4), "5-7": (5, 7), "6-8": (6, 8)}
PARTS = [(("1-3", "2-4"), ("5-7", "6-8")), (("1-3", "5-7"), ("2-4", "6-8")), (("1-3", "6-8"), ("2-4", "5-7"))]
FAMS = ["all", "A1", "A2", "B"]
LATE = LAT2[0] + np.arange(NY2 + 1) * G2
CELLA = (6371.0072 ** 2 * np.radians(G2) * np.abs(np.sin(np.radians(LATE[1:])) - np.sin(np.radians(LATE[:-1]))))[:, None] * np.ones(NX2)[None, :]
LATC = 0.5 * (LATE[1:] + LATE[:-1]); LONC = LON2[0] + (np.arange(NX2) + 0.5) * G2
GRID = GMIN + np.arange(NPTS) * GSTEP
MIXES = ["mixC", "mixE"] + STRATA


class Store:
    def __init__(self, work):
        self.A, self.J = {}, {}
        for st in STRATA:
            for q in QS:
                f = pathlib.Path(work) / f"{st}-q{q}.npz"
                self.A[(st, q)] = np.load(f); self.J[(st, q)] = json.loads(f.with_suffix(".json").read_text())["scalars"]

    def seeds_scal(self, st, P, key, fam=None):
        """per-seed values {seed: v} for scalar `key` of product P."""
        out = {}
        for q in QS:
            E = self.J[(st, q)][P]; v = E[key] if fam is None else E[key][fam]
            for i, k in enumerate(QSEEDS[q]):
                out[k] = v[i]
        return out

    def lnZ(self, st, P, seeds, fam=None):
        d = self.seeds_scal(st, P, "lnM" if fam is None else "fam_lnM", fam)
        return float(logsumexp([d[k] for k in seeds]) - math.log(len(seeds)))

    def h2(self, st, P, qs, fam="all"):
        """unnormalised 2D mass histogram over quarters qs, on log scale: (ln scale, array)."""
        key = P + "|2d" + ("" if fam == "all" else f"|{fam}")
        parts = [(float(self.A[(st, q)][key + "|lnscale"][0]), self.A[(st, q)][key].astype(float)) for q in qs]
        mx = max(s for s, _ in parts)
        return mx, sum(h * math.exp(s - mx) for s, h in parts)

    def hlat(self, st, P, seeds, fam="all"):
        lm = self.seeds_scal(st, P, "lnM"); mx = max(lm[k] for k in seeds); acc = np.zeros(NPTS)
        for k in seeds:
            q = next(q for q in QS if k in QSEEDS[q])
            key = P + (f"|lat|s{k}" if fam == "all" else f"|lat|{fam}|s{k}")
            acc += self.A[(st, q)][key].astype(float) * math.exp(lm[k] - mx)
        return acc / sum(math.exp(lm[k] - mx) for k in seeds)


def area_stats(p):
    """p: in-grid density (any scale). Returns (A50, A90 km2, smoothed normalised map)."""
    s = gaussian_filter(p.reshape(NY2, NX2), 1.0, mode="constant"); s = s / s.sum()
    o = np.argsort(s.ravel())[::-1]; c = np.cumsum(s.ravel()[o]); a = CELLA.ravel()[o]
    return float(a[:np.searchsorted(c, 0.5) + 1].sum()), float(a[:np.searchsorted(c, 0.9) + 1].sum()), s


def lat_q(h, qs=(0.05, 0.5, 0.95)):
    c = np.cumsum(h); c = c / c[-1]; out = []
    for q in qs:
        k = int(np.searchsorted(c, q)); lo = c[k - 1] if k else 0.0
        out.append(float(GRID[k] - GSTEP / 2 + GSTEP * (q - lo) / max(c[k] - lo, 1e-300)))
    return out


class Mixer:
    def __init__(self, S):
        self.S = S

    def weights(self, P, mix, seeds_by_st):
        d, c = P.split("|")[:2]; base = f"{d}|{c}|P1|-|"
        if mix in STRATA:
            return {mix: 1.0}
        W = {}
        for st in STRATA:
            W[st] = math.log(PCORE[st]) + self.S.lnZ(st, base if mix == "mixC" else P, seeds_by_st)
        mx = max(W.values()); W = {k: math.exp(v - mx) for k, v in W.items()}; t = sum(W.values())
        return {k: v / t for k, v in W.items()}

    def product(self, P, mix, fam="all", qs=tuple(QS), full=True):
        seeds = sorted(k for q in qs for k in QSEEDS[q]); W = self.weights(P, mix, seeds)
        dens = np.zeros(NY2 * NX2); hl = np.zeros(NPTS); share = 0.0; ess_num = 0.0; ess_den = 0.0
        mlat = mlon = 0.0; fast = out2d = nc = 0.0
        for st, w in W.items():
            if w == 0:
                continue
            lnM = self.S.seeds_scal(st, P, "lnM"); lnM2 = self.S.seeds_scal(st, P, "lnM2")
            mx = max(lnM[k] for k in seeds); Ms = sum(math.exp(lnM[k] - mx) for k in seeds)       # stratum mass / e^mx
            sc, h = self.S.h2(st, P, qs, fam); dens += w * h * math.exp(sc - mx) / Ms
            if fam == "all":
                M2 = sum(math.exp(lnM2[k] - 2 * mx) for k in seeds); f_s = 1.0
            else:
                fl = self.S.seeds_scal(st, P, "fam_lnM", fam); fl2 = self.S.seeds_scal(st, P, "fam_lnM2", fam)
                M2 = sum(math.exp(fl2[k] - 2 * mx) for k in seeds); f_s = sum(math.exp(fl[k] - mx) for k in seeds) / Ms
            share += w * f_s; ess_num += w * f_s; ess_den += w * w * M2 / Ms ** 2
            if full:
                hl += w * self.S.hlat(st, P, seeds, fam)
                sw = {k: math.exp(lnM[k] - mx) / Ms for k in seeds}
                for key, acc in (("mean_lat", "mlat"), ("mean_lon", "mlon"), ("fast_share", "fast"), ("out2d_share", "out2d"), ("drift_nc_share_G", "nc")):
                    v = self.S.seeds_scal(st, P, key); val = w * sum(sw[k] * v[k] for k in seeds)
                    if acc == "mlat": mlat += val
                    elif acc == "mlon": mlon += val
                    elif acc == "fast": fast += val
                    elif acc == "out2d": out2d += val
                    else: nc += val
        r = {"weights": W, "share": share, "ess": (ess_num ** 2 / ess_den) if ess_den > 0 else 0.0}
        a50, a90, sm = area_stats(dens) if dens.sum() > 0 else (float("nan"), float("nan"), None)
        r.update(A50=a50, A90=a90, smooth=sm, dens=dens)
        if full:
            q05, q50, q95 = lat_q(hl)
            r.update(q05=q05, median=q50, q95=q95, hlat=hl)
            if fam == "all":
                r.update(mean_lat=mlat, mean_lon=mlon, fast=fast, out2d=out2d, drift_nc=nc)
            else:
                g = dens.reshape(NY2, NX2); t = g.sum()
                r.update(mean_lat=float((g.sum(1) * LATC).sum() / t), mean_lon=float((g.sum(0) * LONC).sum() / t))
        return r

    def split(self, P, mix):
        """area relative differences and 2D overlap over 3 partitions; median differences over 35 partitions."""
        ad, md, ov = [], [], []
        for h0, h1 in PARTS:
            a = self.product(P, mix, qs=h0, full=False); b = self.product(P, mix, qs=h1, full=False)
            ad.append((abs(a["A50"] - b["A50"]) / (0.5 * (a["A50"] + b["A50"])), abs(a["A90"] - b["A90"]) / (0.5 * (a["A90"] + b["A90"]))))
            ov.append(float(np.minimum(a["smooth"], b["smooth"]).sum()))
        for comb in itertools.combinations(range(2, 9), 3):
            s0 = (1,) + comb; s1 = tuple(k for k in range(1, 9) if k not in s0); ms = []
            for ss in (s0, s1):
                W = self.weights(P, mix, list(ss)); hl = np.zeros(NPTS)
                for st, w in W.items():
                    hl += w * self.S.hlat(st, P, list(ss))
                ms.append(lat_q(hl, (0.5,))[0])
            md.append(abs(ms[0] - ms[1]))
        return {"area50_reldiff_max": max(x[0] for x in ad), "area90_reldiff_max": max(x[1] for x in ad), "overlap2d_mean": float(np.mean(ov)),
                "median_diff_max_deg": float(max(md)), "median_diff_mean_deg": float(np.mean(md))}


def main(work, outd):
    outd = pathlib.Path(outd); outd.mkdir(parents=True, exist_ok=True)
    S = Store(work); M = Mixer(S); PR = [pid(p) for p in products()]
    rows = []; maps = {}
    SPLIT_FOR = lambda P: P.split("|")[1] == "T" and P.split("|")[4] in ("",) and P.split("|")[3] in ("M", "-")
    for P in PR:
        for mix in MIXES:
            for fam in FAMS:
                r = M.product(P, mix, fam)
                row = {"product": P, "mix": mix, "family": fam, "share": r["share"], "ess": r["ess"], "A50_km2": r["A50"], "A90_km2": r["A90"],
                       "lat_q05": r["q05"], "lat_median": r["median"], "lat_q95": r["q95"], "mean_lat": r["mean_lat"], "mean_lon": r["mean_lon"]}
                if fam == "all":
                    row.update(fast_share=r["fast"], out_of_grid=r["out2d"], drift_nc_share=r["drift_nc"],
                               lnZ=float(logsumexp([math.log(PCORE[st]) + S.lnZ(st, P, list(range(1, 9))) for st in STRATA]) if mix in ("mixC", "mixE") else S.lnZ(mix, P, list(range(1, 9)))),
                               stratum_weights=json.dumps({SNAME[k]: round(v, 6) for k, v in r["weights"].items()}))
                    if SPLIT_FOR(P) and mix in ("mixC", "next-i-free", "next-i-waypoints"):
                        row.update(M.split(P, mix))
                    if mix in ("mixC", "next-i-free") and P.split("|")[1] == "T":
                        maps[f"{P}#{mix}"] = r["smooth"].astype(np.float32); maps[f"{P}#{mix}#lat"] = r["hlat"].astype(np.float32)
                elif mix == "mixC" and P.split("|")[1] == "T" and P.split("|")[3] in ("M", "-") and P.split("|")[4] == "":
                    maps[f"{P}#{mix}#{fam}"] = r["smooth"].astype(np.float32)
                rows.append(row)
        print("product", P, flush=True)
    json.dump(rows, open(outd / "products-all.json", "w"))
    np.savez_compressed(outd / "maps.npz", **maps)
    # evidence, model weights
    ev = []
    for d in DS:
        for c in CS:
            Z = lambda L, oc="M", var="": float(logsumexp([math.log(PCORE[st]) + S.lnZ(st, f"{d}|{c}|{L}|{oc}|{var}", list(range(1, 9))) for st in STRATA]))
            e = {"D": d, "C": c, "lnZ_P1": Z("P1", "-")}
            for L in LAYERS:
                e[f"lnZ_{L}"] = Z(L)
            e["d_drift"] = e["lnZ_Dr"] - e["lnZ_P1"]; e["d_search_after_drift"] = e["lnZ_DrS"] - e["lnZ_Dr"]
            e["d_pleiades_hook_scale"] = e["lnZ_H"] - e["lnZ_Dr"] + 12.43; e["d_search_after_H"] = e["lnZ_HS"] - e["lnZ_H"]
            if c == "T":
                for L in LAYERS:
                    zg, zc = Z(L, "G"), Z(L, "C"); e[f"P_GLORYS12_{L}"] = 1.0 / (1.0 + math.exp(zc - zg)); e[f"lnZ_{L}_G"] = zg; e[f"lnZ_{L}_C"] = zc
                    e[f"lnR_hyd_{L}"] = Z(L, "M", "+hyd") - e[f"lnZ_{L}"]
                e["drift_x_lnZ_Dr"] = Z("Dr", "M", "x")
                for st in STRATA:          # per-stratum model weights (drift only) for the free-only comparison
                    zg = S.lnZ(st, f"{d}|T|Dr|G|", list(range(1, 9))); zc = S.lnZ(st, f"{d}|T|Dr|C|", list(range(1, 9)))
                    e[f"P_GLORYS12_Dr_{SNAME[st]}"] = 1.0 / (1.0 + math.exp(zc - zg))
            ev.append(e)
    json.dump(ev, open(outd / "evidence.json", "w"), indent=1)
    # per-seed lnZ spread (stratum) for headline products
    sd = {}
    for P in PR:
        if P.split("|")[1] == "T" and P.split("|")[4] == "":
            sd[P] = {SNAME[st]: float(np.std(list(S.seeds_scal(st, P, "lnM").values()), ddof=1)) for st in STRATA}
    json.dump(sd, open(outd / "seed-sd-lnZ.json", "w"))
    meta = {st: {q: S.J[(st, q)]["_meta"] for q in QS} for st in STRATA}
    json.dump(meta, open(outd / "inputs-meta.json", "w"))
    print("report done", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
