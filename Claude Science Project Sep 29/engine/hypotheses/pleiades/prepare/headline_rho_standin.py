"""STAND-IN (11 Oct 2026) for the Pléiades module: run C headline under the architecture rulings of 11 Oct 02:15 -0600
(ρ = 0.25 headline, ρ = 0 / 0.5 beside; GLORYS12 only headline, both models beside, labelled 'GlobCurrent windage double-counted
(drift audit F1)'). No method change: the module's published correlated-error surfaces (surfaces/joint-surface-rho*.f32,
prepare/rho_surface.py) replace L_P+C4 on the module's own run C mixture maps (branch_eof289 branch-maps.npz, strata re-weighted by
end of flight's family-evidence-run-c.json, closeup_styles.reweighted_pfam), as rho_sensitivity.py does on core (b). Statistics use the
module's own functions (closeup_figure.stats, rerun_reference.tension, branch_figure.hdr_level). For the module to review.

    python headline_rho_standin.py <branch root> <surface dir> <family-evidence json> <geom dir> <out dir>
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import closeup_figure as cf  # noqa: E402
import closeup_styles as cs  # noqa: E402
from branch_figure import hdr_level  # noqa: E402
from option_closeups import load_mixture  # noqa: E402
from rerun_reference import tension  # noqa: E402

OPTS = ["r600/no-offset+unpowered", "r600-bto+unpowered", "none+unpowered"]
# (key, rho, model): model 0 = GLORYS12 + ERA5, "mean" = equal-weight mean of both models (missing model = zero likelihood)
VARIANTS = [("rho0.25 GLORYS12", 0.25, 0), ("rho0 GLORYS12", 0.0, 0), ("rho0.5 GLORYS12", 0.5, 0), ("rho0.25 both models", 0.25, "mean")]


def rho_L(surf, rho, model):
    m = dict(l.split(" = ", 1) for l in (Path(surf) / f"joint-surface-rho{rho:g}.toml").read_text().splitlines())
    J = np.fromfile(Path(surf) / f"joint-surface-rho{rho:g}.f32", "<f4").reshape(2, int(m["nlat"]), int(m["nlon"])).astype(float)
    E = np.nan_to_num(np.exp(J))   # not computed -> zero likelihood (as build_branch)
    return E[model] if model != "mean" else 0.5 * (E[0] + E[1])


def with_L(maps, L):
    return {v: {**m, "L_P+C4": L} for v, m in maps.items()}


def row(MP, masks, v="oi2018-2025"):
    lat, lon, area = MP[v]["lat"], MP[v]["lon"], MP[v]["area"]
    LAT, LON = np.meshgrid(lat, lon, indexing="ij")
    m = cs.panel_mass(MP, v, "P+C4"); dn = m / area; s = cf.stats(m, area, LAT, LON, masks)
    Lf = np.nan_to_num(MP[v]["L_P+C4"]); t = cs.mix_tension(MP, v)
    return dict(hdr50_km2=float(area[dn >= hdr_level(dn, m, 0.5)].sum()), hdr90_km2=s["hdr90_km2"], mean_lat=s["mean_lat"],
                mean_lon=s["mean_lon"], share_outside_past_searches=1 - s["mass_in_past"], share_in_nw_band=s["mass_in_nw"],
                search_retains_under_H=float((MP[v]["post"] * Lf).sum() / (MP[v]["pre"] * Lf).sum()),
                search_retains_flight_only=float(MP[v]["post"].sum() / MP[v]["pre"].sum()),
                ln_S=t["ln_S"], tension_p=t["tension_p"], d_shared=t["d_shared"], mean_shift_nm=t["mean_shift_nm"],
                uncond_in_cond_hdr90=t["uncond_in_cond_hdr90"], cond_in_uncond_hdr90=t["cond_in_uncond_hdr90"], ln_R=t["ln_R"])


def main(root, surf, fam, geom, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    geo = json.loads((Path(geom) / "search_footprints.geojson").read_text())
    Ls = {k: rho_L(surf, r, mo) for k, r, mo in VARIANTS}
    rows, checks = [], []
    for o in OPTS:
        pf = cs.reweighted_pfam(fam, o)
        assert pf is not None, o
        maps = {v: load_mixture(root, o, v, pf) for v in ("base", "oi2018-2025")}
        lat, lon = maps["base"]["lat"], maps["base"]["lon"]
        LAT, LON = np.meshgrid(lat, lon, indexing="ij")
        masks = {"nw": cf.mask_of(cf.polygons(geo, "oi2024_proposed_inboard_northwest"), LON, LAT),
                 "past": cf.mask_of(cf.polygons(geo, "atsb_phase2_2014_2017"), LON, LAT)
                 | cf.mask_of(cf.polygons(geo, "oi2018_total_outline_approx"), LON, LAT)
                 | cf.mask_of(cf.polygons(geo, "oi2024_proposed_outboard_southeast"), LON, LAT)}
        g12, _ = cs.single_model(maps, surf, 0)
        # reproduction checks: the module's hook surfaces (rho = 0) on the same maps
        for nm, MP, Lj in (("hook both models (module headline)", maps, rho_L(surf, 0.0, "mean")),
                           ("hook GLORYS12 only", g12, Ls["rho0 GLORYS12"])):
            r0 = row(MP, masks)
            hook = np.nan_to_num(MP["oi2018-2025"]["L_P+C4"]); cm = MP["oi2018-2025"]["post"] * hook
            miss = float(cm[Lj == 0].sum() / cm.sum())
            ok = (hook > 0) & (Lj > 0)
            checks.append(dict(option=o, check=nm, hdr90_km2=r0["hdr90_km2"], mean_lat=r0["mean_lat"], mean_lon=r0["mean_lon"],
                               ln_S=r0["ln_S"], conditional_mass_where_rho0_surface_not_computed=miss,
                               lnratio_sd_rho0_vs_hook=float(np.std(np.log(Lj[ok]) - np.log(hook[ok])))))
        for k, _, _ in VARIANTS:
            MP = with_L(maps, Ls[k])
            rows.append(dict(option=o, option_name=cs.describe_option(o, short=True), variant=k, strata="reweighted-0019",
                             family_key=cs.eof_family_key(o, json.loads(Path(fam).read_text())["mixtures"]), **row(MP, masks)))
        print(o, flush=True)
    T = pd.DataFrame(rows); T.to_csv(out / "headline-rho025-stats.csv", index=False)
    C = pd.DataFrame(checks); C.to_csv(out / "headline-rho025-checks.csv", index=False)
    return T, C


if __name__ == "__main__":
    T, C = main(*sys.argv[1:6])
    pd.set_option("display.width", 250)
    print(C.to_string(index=False))
    print(T[["option_name", "variant", "hdr50_km2", "hdr90_km2", "mean_lat", "mean_lon", "share_outside_past_searches", "search_retains_under_H",
             "ln_S", "tension_p", "mean_shift_nm", "uncond_in_cond_hdr90"]].round(4).to_string(index=False))
