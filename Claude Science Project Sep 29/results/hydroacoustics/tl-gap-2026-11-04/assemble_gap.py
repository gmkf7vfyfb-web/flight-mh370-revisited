"""Assemble the loss-gap diagnostic runs (gapdiag.py) into band tables and range curves.
fg_db_per_km and sph_db are verbatim copies of tlchain.chain (tl-chain-2026-10-27), so this file needs only numpy/pandas.
Outputs (to <outdir>): band_tl_runs.csv (band TL at the hydrophone per path, kind, seabed, source depth),
range_curves.csv (per path, seabed, band: forward water-column energy and reverse TL against source position, 5-km bins)."""
import json, sys
from collections import defaultdict
import numpy as np, pandas as pd

R_EARTH = 6371.0
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]


def fg_db_per_km(f_hz, T=4.0, S=34.7, pH=8.0, z=1000.0):            # copy of tlchain.chain.fg_db_per_km
    f = np.asarray(f_hz, float) / 1000.0
    c = 1412.0 + 3.21 * T + 1.19 * S + 0.0167 * z
    A1 = 8.86 / c * 10 ** (0.78 * pH - 5); f1 = 2.8 * np.sqrt(S / 35.0) * 10 ** (4 - 1245.0 / (T + 273.0))
    A2 = 21.44 * S / c * (1 + 0.025 * T); P2 = 1 - 1.37e-4 * z + 6.2e-9 * z ** 2
    f2 = 8.17 * 10 ** (8 - 1990.0 / (T + 273.0)) / (1 + 0.0018 * (S - 35.0))
    A3 = 4.937e-4 - 2.59e-5 * T + 9.11e-7 * T ** 2 - 1.50e-8 * T ** 3; P3 = 1 - 3.83e-5 * z + 4.9e-10 * z ** 2
    return A1 * f1 * f ** 2 / (f1 ** 2 + f ** 2) + A2 * P2 * f2 * f ** 2 / (f2 ** 2 + f ** 2) + A3 * P3 * f ** 2


def sph_db(R_km):                                                    # copy of tlchain.chain.sph_db
    x = np.asarray(R_km, float) / R_EARTH
    return 10 * np.log10(np.where(x > 0, x / np.sin(np.where(x > 0, x, 1)), 1.0))


def band_tl(I_by_f, freqs, R_km):                                    # copy of tlchain.chain.band_tl
    a = np.array([np.asarray(I) * 10 ** (-fg_db_per_km(f) * R_km / 10) for I, f in zip(I_by_f, freqs)])
    with np.errstate(divide="ignore"):
        return -10 * np.log10(a.mean(axis=0)) + sph_db(R_km)


def load(out_jsonl):
    g = defaultdict(list)
    for ln in open(out_jsonl):
        r = json.loads(ln)
        if r.get("status") != "ok":
            continue
        kind, sb, path, fc, f = r["id"].split("|")
        g[(kind, sb, path, float(fc))].append((float(f), r))
    return g


def assemble(out_jsonl, outdir, rev_depths=(10.0, 2.0, 5.0, 30.0, 100.0), krk_depths=(2.0, 10.0, 30.0), bin_km=5.0):
    g = load(out_jsonl)
    rows, curves = [], []
    for (kind, sb, path, fc), v in sorted(g.items()):
        v.sort(key=lambda x: x[0]); fs = np.array([x[0] for x in v]); L = v[0][1]["L_km"]
        if kind == "krk":
            ok = [x for x in v if x[1].get("ok") and x[1].get("I") is not None]
            if not ok:
                continue
            I = np.array([x[1]["I"] for x in ok], float); fk = np.array([x[0] for x in ok])
            tl = band_tl(I, fk, L)
            for j, z in enumerate(krk_depths):
                rows.append(dict(path=path, kind=kind, seabed=sb, fc_hz=fc, src_depth_m=z, tl_db=float(tl[j]), nf=len(fk), range_km=L))
            continue
        I = np.array([x[1]["I"] for x in v], float)
        tl = band_tl(I, fs, L)
        deps = rev_depths if kind == "rev" else (10.0,)
        for j, z in enumerate(deps):
            rows.append(dict(path=path, kind=kind, seabed=sb, fc_hz=fc, src_depth_m=z, tl_db=float(tl[j]), nf=len(fs), range_km=L))
        # range curves on a common bin grid
        edges = np.arange(0.0, L + bin_km, bin_km); mid = 0.5 * (edges[1:] + edges[:-1])
        if kind == "rev" and "rec_r" not in v[0][1]:
            continue                                     # runs without a range record (addendum runs)
        if kind == "rev":
            acc = np.zeros(len(mid)); n = np.zeros(len(mid))
            for f, r in v:
                rr = np.asarray(r["rec_r"]) / 1e3; Ir = 10 ** (-np.asarray(r["rec_tl"]) / 10) * 10 ** (-fg_db_per_km(f) * rr / 10)
                k = np.clip(np.digitize(rr, edges) - 1, 0, len(mid) - 1)
                np.add.at(acc, k, Ir); np.add.at(n, k, 1)
            with np.errstate(divide="ignore", invalid="ignore"):
                tlr = -10 * np.log10(acc / n) + sph_db(mid)
            # rec distance is measured from the hydrophone; convert to distance from the impact end too
            for m_, t_ in zip(mid, tlr):
                curves.append(dict(path=path, kind="rev", seabed=sb, fc_hz=fc, r_from_rcv_km=m_, r_from_src_km=L - m_, value_db=t_,
                                   quantity="TL from a 10 m source at this point to the hydrophone (dB)"))
        else:
            acc = np.zeros(len(mid)); accu = np.zeros(len(mid)); n = np.zeros(len(mid)); zb = np.zeros(len(mid))
            for f, r in v:
                rr = np.asarray(r["rec_r"]) / 1e3; a = 10 ** (-fg_db_per_km(f) * rr / 10)
                k = np.clip(np.digitize(rr, edges) - 1, 0, len(mid) - 1)
                np.add.at(acc, k, np.asarray(r["rec_F"]) * a); np.add.at(accu, k, np.asarray(r["rec_Fup"]) * a)
                np.add.at(n, k, 1); np.add.at(zb, k, np.asarray(r["rec_zb"]))
            with np.errstate(divide="ignore", invalid="ignore"):
                Fm = acc / n; Fu = accu / n; zbm = zb / n
            Iend = float(np.mean([x[1]["I"][0] * 10 ** (-fg_db_per_km(x[0]) * L / 10) for x in v]))
            for m_, F_, U_, z_ in zip(mid, Fm, Fu, zbm):
                curves.append(dict(path=path, kind="fwd", seabed=sb, fc_hz=fc, r_from_src_km=m_, r_from_rcv_km=L - m_,
                                   value_db=10 * np.log10(F_), upper_db=10 * np.log10(U_), seafloor_m=z_, I_end=Iend, L_km=L,
                                   quantity="water-column energy, 10 log10 of r times depth-integrated |p|^2 (dB re 1 m)"))
    B = pd.DataFrame(rows); Cv = pd.DataFrame(curves)
    B.to_csv(f"{outdir}/band_tl_runs.csv", index=False); Cv.to_csv(f"{outdir}/range_curves.csv.gz", index=False)
    return B, Cv


if __name__ == "__main__":
    B, Cv = assemble(sys.argv[1], sys.argv[2])
    print(B.shape, Cv.shape)
