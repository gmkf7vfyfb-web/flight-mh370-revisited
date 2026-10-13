"""Correlated Pléiades / COSMO-SkyMed transport errors on a core run (declared sensitivity; the hook assumes rho = 0).

Ocean transport measured the cross-lag (13 d / 15 d) error correlation between nearby undrogued drifters
(results/ocean-transport-error-pairs.md, 10 Oct 2026): central rho ~0.2-0.3 at the 40-80 km separations here, upper
sensitivity 0.5, rho = 0.8 not supported. This script re-scores P + all four COSMO contacts with a bivariate-normal error per
component (same OU variances as the hook, windages independent between object and contact), using audit_closeup's joint(),
which reproduces the hook's product at rho = 0. It then applies the result to the module's strata mixtures for each option.

    python rho_sensitivity.py <branch root> <out dir> <option> [<option> ...] [--fam <family-evidence json>]
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit_closeup as ac  # noqa: E402
import closeup_figure as cf  # noqa: E402
import closeup_styles as cs  # noqa: E402
from branch_figure import hdr_level  # noqa: E402
from option_closeups import load_mixture  # noqa: E402
from rerun_reference import tension  # noqa: E402

RHOS = (0.0, 0.25, 0.5)
PF = {"next-free": 0.6948, "next-repro-radar": 0.1527, "next-descent-climb": 0.1376, "next-routes": 0.0149}


def joint_surfaces(runs, module_dir, lat, lon):
    tabs = [ac.load_table(runs, n) for n in ac.TABLES]
    OUTS = tabs[0][0]["out_unix_s"]
    T5 = pd.read_csv(module_dir / "data/targets-3km.csv").query("arm == 'rating5'")
    Cc = pd.read_csv(module_dir / "data/cosmo-contacts.csv")
    LAT, LON = np.meshgrid(lat, lon, indexing="ij")
    EP = {(mi, ti): ac.endpoints_grid(tabs[mi][1], ti, LON, LAT) for mi in (0, 1) for ti in range(4)}

    def joint(mi, rho):   # audit_closeup.main section 6, on the given grid
        tot = 0.0
        for ps in (0, 1):
            vC = ac.ou_var_km2(mi, OUTS[ps] - ac.T_IMP)
            RC = [ac.resid(EP[(mi, ps)], (r.longitude, r.latitude)) for _, r in Cc.iterrows()]
            for _, r in T5.iterrows():
                ti = 2 if ac.SCENE[r.scene] == OUTS[2] else 3
                vP = ac.ou_var_km2(mi, ac.SCENE[r.scene] - ac.T_IMP)
                rP = ac.resid(EP[(mi, ti)], (r.lon, r.lat))
                lpP = -0.5 * np.sum(rP ** 2 / vP, -1) - np.log(2 * np.pi * np.sqrt(vP.prod()))
                b = rho * np.sqrt(vC / vP); vc = vC * (1 - rho ** 2)
                for rC in RC:
                    dif = rC[..., None, :, :] - b * rP[..., :, None, :]
                    lpC = -0.5 * np.sum(dif ** 2 / vc, -1) - np.log(2 * np.pi * np.sqrt(vc.prod()))
                    tot = tot + r.w_equal * 0.25 * 0.5 * np.mean(np.exp(lpP[..., :, None] + lpC), axis=(-2, -1))
        return tot

    out = {}
    for rho in RHOS:
        t0 = time.time()
        out[rho] = np.nan_to_num(0.5 * (joint(0, rho) + joint(1, rho)))
        print(f"rho {rho}: {time.time() - t0:.0f} s", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root"); ap.add_argument("out"); ap.add_argument("options", nargs="+"); ap.add_argument("--fam", default=None)
    a = ap.parse_args()
    root, out = Path(a.root), Path(a.out); out.mkdir(parents=True, exist_ok=True)
    runs, M = HERE.parents[2] / "runs" / "pleiades", HERE.parent
    geo = json.loads((HERE.parents[5] / "geom" / "search_footprints.geojson").read_text())
    first = load_mixture(root, a.options[0], "oi2018-2025", PF)
    lat, lon, area = first["lat"], first["lon"], first["area"]
    # box covering the conditional (as audit_closeup section 6): 86-98 E, 40-30 S
    bi = np.where((lat >= -40) & (lat <= -30))[0]; bj = np.where((lon >= 86) & (lon <= 98))[0]
    sl = (slice(bi[0], bi[-1] + 1), slice(bj[0], bj[-1] + 1))
    J = joint_surfaces(runs, M, lat[sl[0]], lon[sl[1]])
    np.savez_compressed(out / "rho-joint-surfaces.npz", lat=lat[sl[0]], lon=lon[sl[1]], **{f"rho_{r}": v for r, v in J.items()})
    A = area[sl]; LA, LO = np.meshgrid(lat[sl[0]], lon[sl[1]], indexing="ij")
    masks = {"past": cf.mask_of(cf.polygons(geo, "atsb_phase2_2014_2017"), LO, LA) | cf.mask_of(cf.polygons(geo, "oi2018_total_outline_approx"), LO, LA)
             | cf.mask_of(cf.polygons(geo, "oi2024_proposed_outboard_southeast"), LO, LA)}
    rows = []
    for opt in a.options:
        pf = cs.reweighted_pfam(a.fam, opt) or PF
        for v in ("base", "oi2018-2025"):
            mp = load_mixture(root, opt, v, pf)
            ref = np.nan_to_num(mp["L_P+C4"])[sl]
            ok = (ref > 0) & (J[0.0] > 0)
            sd0 = float(np.std(np.log(J[0.0][ok]) - np.log(ref[ok])))
            post, pre = mp["post"][sl], mp["pre"][sl]
            # share of the full-grid conditional (rho = 0) inside the box: the box must hold nearly all of it
            full = mp["post"] * np.nan_to_num(mp["L_P+C4"]); inbox = float(full[sl].sum() / full.sum())
            for rho in RHOS:
                m = post * J[rho]; s = cf.stats(m, A, LA, LO, masks); dn = (m / m.sum()) / A
                z = np.zeros_like(A, dtype=bool)
                t = tension(post, J[rho], A, lat[sl[0]], lon[sl[1]], z, z, z)
                rows.append(dict(option=opt, option_name=cs.describe_option(opt, short=True), search=cs.SEARCH_SHORT[v], rho=rho,
                                 strata=("reweighted-0019" if pf is not PF else "fixed"),
                                 hdr50_km2=round(float(A[dn >= hdr_level(dn, m / m.sum(), 0.5)].sum())), hdr90_km2=round(s["hdr90_km2"]),
                                 mean_lat=round(s["mean_lat"], 3), mean_lon=round(s["mean_lon"], 3),
                                 outside_past_searches=round(1 - s["mass_in_past"], 4),
                                 search_retains_under_H=round(float((post * J[rho]).sum() / (pre * J[rho]).sum()), 3),
                                 ln_S=round(t["ln_S"], 3), tension_p=round(t["tension_p"], 3), mean_shift_nm=round(t["mean_shift_nm"], 1),
                                 rho0_vs_hook_lnratio_sd=round(sd0, 5), conditional_share_in_box=round(inbox, 4)))
    T = pd.DataFrame(rows); T.to_csv(out / "rho-sensitivity.csv", index=False)
    print(T[T.search.str.contains("OI")][["option", "rho", "hdr50_km2", "hdr90_km2", "mean_lat", "mean_lon", "search_retains_under_H",
                                          "ln_S", "mean_shift_nm", "rho0_vs_hook_lnratio_sd", "conditional_share_in_box"]].to_string(index=False))


if __name__ == "__main__":
    main()
