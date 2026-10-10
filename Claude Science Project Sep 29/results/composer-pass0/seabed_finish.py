"""Composer pass 1: seabed PDFs of the composed products, by reweighting settling's own core-set seabed samples on core (b).

PIPELINE TEST - core (b) unconverged; EoF physics provisional; hydro L_hyd stand-in; GlobCurrent F1; Holland H1/H2 not estimable.

For each 00:19 option (Held Out: settling table A; R600 BTO Only: table B) and product Q (P1, G, Ga, H, Ha; Gx, Hx sensitivities),
each resampled impact of settling's ruled (00:19-re-weighted) mixture gets the importance weight
    v = W_Q(stratum) x w_Q(row) / ( P_settling(stratum) / 4 x p_src(row) ),
w_Q the composer's pooled within-stratum weight, W_Q the stratum weight of the note's primary mixture (EoF re-weighted
P(family), identical to settling's P_settling), p_src settling's seed-normalised `unpowered` option posterior. The seabed density is
settling's own `seabed_density` (wreckage_map_standard.py: settled elements share their impact's weight in proportion to mass)
with v as the one extra weight, on settling's grid (0.02 deg, Gaussian 0.1 deg, end of flight's hpd_levels, authalic areas):
the Pleiades-conditional stand-in's construction. Check: v = 1 reproduces settling's published areas.

Rows the composer weights but settling could not draw (+alive but powered at 01:15:56: `unpowered` = 0) are a coverage gap of
this reweighting; their share of each product's mass is reported.

Usage: python seabed_finish.py <work dir> <out json> <fig png>
"""
import json, pathlib, sys
import numpy as np
from scipy.ndimage import gaussian_filter

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import seabed_extract as X
import report as RP

EOF_SMOKE = "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/d5fc8d7c-15e5-4858-b15e-9553989a6413/eof-3c6319f/Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke"
sys.path.insert(0, EOF_SMOKE)
from displacement_greyscale import hpd_levels  # noqa: E402

GRID, R_AUTH, SMOOTH = 0.02, 6371.0072, 0.1
NAMES = {0: "00:19 Held Out", 1: "00:19 R600 BTO Only"}


def main(work, outp, figp):
    work = pathlib.Path(work)
    info = json.loads((X.FIELD / "nrb_info.json").read_text()); z = np.load(X.FIELD / "nrb_draws.npz")
    ext = info["extent_lon_lon_lat_lat"]
    le = np.arange(ext[2], ext[3] + GRID / 2, GRID); oe = np.arange(ext[0], ext[1] + GRID / 2, GRID)
    cell = (R_AUTH ** 2) * np.radians(GRID) * np.abs(np.sin(np.radians(le[1:])) - np.sin(np.radians(le[:-1])))[:, None] * np.ones(len(oe) - 1)[None, :]
    D = RP.load(work)
    sm = lambda H: (lambda d: d / d.sum())(gaussian_filter(H, SMOOTH / GRID, mode="constant"))
    areas = lambda H: [float(cell[sm(H) >= l].sum()) for l in hpd_levels(sm(H), (0.99, 0.9, 0.5))]
    res = {"label": RP.LABEL, "settling": "results/settling-core-set-next-run-b (hypothesis/settling 5b595bf), field/nrb*, read in place",
           "constraint_settling": info["constraint"], "options": {}}
    maps = {}
    for j, (t, tag, opt) in X.OPTS.items():
        T = np.fromfile(X.FIELD / f"nrb{t}_impacts.f64", "<f8").reshape(-1, 14)
        EL = np.memmap(X.FIELD / f"nrb{t}_elements.f64", dtype="<f8", mode="r").reshape(-1, 8)
        st_ = EL[:, 4] == 0
        key = EL[st_, 0].astype(np.int64) * 1048576 + EL[st_, 1].astype(np.int64)
        o = np.argsort(key, kind="stable"); key, lat, lon, mass = key[o], np.asarray(EL[st_, 5])[o], np.asarray(EL[st_, 6])[o], np.asarray(EL[st_, 7])[o]
        uk, start = np.unique(key, return_index=True); stop = np.r_[start[1:], len(key)]
        share = mass / np.repeat(np.add.reduceat(mass, start), stop - start)
        ka = np.asarray(EL[:, 0]).astype(np.int64) * 1048576 + np.nan_to_num(np.asarray(EL[:, 1]), nan=-1).astype(np.int64)
        fate, emass = np.asarray(EL[:, 4]), np.asarray(EL[:, 7])
        rows_all, draws_all, strat_all = z[f"rows_{j}"], z[f"draws_{j}"], z[f"stratum_{j}"]
        mix = z[f"reweighted_{j}"]
        # per-outcome extracted records
        R = {}
        for si, st in enumerate(info["strata"]):
            e = np.load(work / "seabed" / f"{st}.npz")
            for kk in e.files:
                jj, name = kk.split("|", 1)
                if int(jj) == j:
                    R.setdefault(name, []).append(e[kk])
        R = {k: np.concatenate(v) for k, v in R.items()}
        outcome = R["outcome"]; sel = mix[outcome]
        P_set = info["options"][NAMES[j]]["reweighted"]["p_family"]
        matched = int((R["row"][sel] >= 0).sum())
        O = res["options"][NAMES[j]] = {"outcomes_in_ruled_mixture": int(sel.sum()), "matched": matched, "products": {}}

        def density(v, rows, draws):
            want = rows.astype(np.int64) * 1048576 + draws.astype(np.int64)
            pos = np.minimum(np.searchsorted(uk, want), len(uk) - 1); ok = uk[pos] == want
            n_el = (stop - start)[pos[ok]]
            idx = np.concatenate([np.arange(a, b) for a, b in zip(start[pos[ok]], stop[pos[ok]])])
            w = share[idx] * np.repeat(v[ok], n_el) / v.sum()
            Hw = np.histogram2d(lat[idx], lon[idx], bins=[le, oe], weights=w)[0]
            imp = T[rows, 1:3]; Hs = np.histogram2d(imp[:, 0], imp[:, 1], bins=[le, oe], weights=v)[0]
            il, io = np.repeat(imp[ok, 0], n_el), np.repeat(imp[ok, 1], n_el)
            off = np.hypot((lat[idx] - il) * 111.2, (lon[idx] - io) * 111.2 * np.cos(np.radians(il))); oo = np.argsort(off); c = np.cumsum(w[oo]) / w.sum()
            inp = np.isin(ka, want); af = float(emass[inp & (fate == 1)].sum() / emass[inp & (fate >= 0)].sum())
            return Hw, Hs, {"offset_km_p50_p90_p99": [float(off[oo][np.searchsorted(c, q)]) for q in (0.5, 0.9, 0.99)],
                            "outcomes_outside_settling_domain": int((~ok).sum()), "afloat_mass_share_unweighted": af}

        rows_o, draws_o = rows_all[outcome][sel], draws_all[outcome][sel]
        # settling's own weights (validation)
        Hw, Hs, st0 = density(np.ones(sel.sum()), rows_o, draws_o)
        O["settling_as_published"] = {"impact_area_km2_99_90_50": areas(Hs), "seabed_area_km2_99_90_50": areas(Hw), **st0}
        for pid in X.PRODUCTS:
            W = RP.weights(D, tag, pid, "reweighted-0019")
            strat = np.array(info["strata"])[strat_all[outcome][sel]]
            Wq = np.array([W[s] for s in strat]); Ps = np.array([P_set[s] for s in strat])
            wq = R[f"w_{pid}"][sel].astype(float) * R[f"f_{pid}"][sel]
            ps = R["p_src"][sel]
            v = np.where((R["row"][sel] >= 0) & (ps > 0), Wq * wq / (Ps / 4.0 * ps), 0.0)
            Hw, Hs, st1 = density(v, rows_o, draws_o)
            # composer mass on rows settling could not draw (p_src = 0): from the composer's own histograms is not row-resolved;
            # report the outcome-level count with v = 0 and the products' +alive vs +unpowered gap from the summaries.
            O["products"][pid] = {"label": dict(P1="flight + EoF", G="general: + drift + hydro", Ga="general, after searches",
                                                H="Pleiades hypothesis (given H)", Ha="Pleiades hypothesis, after searches",
                                                Gx="general, not-computed excluded (sensitivity)", Hx="Pleiades, not-computed excluded (sensitivity)")[pid],
                                  "ess_of_resample": float(v.sum() ** 2 / (v ** 2).sum()), "outcomes": int(v.size),
                                  "outcomes_with_zero_weight": int((v == 0).sum()), "max_share_one_outcome": float(v.max() / v.sum()),
                                  "impact_area_km2_99_90_50": areas(Hs), "seabed_area_km2_99_90_50": areas(Hw), **st1}
            maps[(j, pid)] = (sm(Hs), sm(Hw))
            print(NAMES[j], pid, round(O["products"][pid]["ess_of_resample"]), [round(a / 1e3, 1) for a in O["products"][pid]["seabed_area_km2_99_90_50"]], flush=True)
    pathlib.Path(outp).write_text(json.dumps(res, indent=1))
    figure(maps, res, le, oe, figp)


def figure(maps, res, le, oe, figp):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 7.5, "axes.labelsize": 8, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(2, 4, figsize=(7.2, 7.4), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.86, bottom=0.30, wspace=0.05, hspace=0.30)
    lc, oc = 0.5 * (le[1:] + le[:-1]), 0.5 * (oe[1:] + oe[:-1])
    col = {"G": "#1f5fa8", "Ga": "#1f5fa8", "H": "#c2571a", "Ha": "#c2571a"}
    for r, j in enumerate((1, 0)):
        for c, pid in enumerate(("G", "Ga", "H", "Ha")):
            ax = axes[r, c]; di, dw = maps[(j, pid)]
            lv = hpd_levels(dw, (0.9, 0.5))
            ax.contourf(oc, lc, dw, levels=[lv[0], lv[1], dw.max() * 1.01], colors=["#d9d9d9", col[pid]], alpha=0.9)
            li = hpd_levels(di, (0.9,))
            ax.contour(oc, lc, di, levels=li, colors="k", linewidths=0.5, linestyles="--")
            p = res["options"][NAMES[j]]["products"][pid]
            ax.set_title({"G": "Drift and sound", "Ga": "... after searches", "H": "Pléiades objects added", "Ha": "... after searches"}[pid]
                         + f"\n90 %: {p['seabed_area_km2_99_90_50'][1] / 1e3:,.0f}k km²; ESS {p['ess_of_resample']:,.0f}", loc="left")
            ax.set_xlim(86, 106); ax.set_ylim(-43, -24)
            if p["ess_of_resample"] < 1000:
                ax.text(0.97, 0.03, "NOT ESTIMABLE\n(ESS below 1,000)", transform=ax.transAxes, ha="right", va="bottom", fontsize=6.5, color="#b00020")
        axes[r, 0].set_ylabel("Latitude (degrees)")
        fig.text(0.01, axes[r, 0].get_position().y1 + 0.045, "Primary case: 00:19 transmission range used" if j == 1 else "Comparison case: 00:19 transmissions not used", fontsize=8, fontweight="bold")
    for ax in axes[1]:
        ax.set_xlabel("Longitude (°E)")
    fig.suptitle("Where the wreckage is on the seabed, for each set of evidence", x=0.01, ha="left", fontsize=9, y=0.985)
    fig.text(0.01, 0.950, "Grey: 90 % region of the wreckage. Colour: 50 % region. Dashed line: 90 % region of the impact point.", fontsize=7)
    fig.add_artist(matplotlib.lines.Line2D([0.01, 0.99], [0.245, 0.245], color="#999999", lw=0.5))
    fig.text(0.01, 0.237, "PIPELINE TEST - NOT CONVERGED (core (b) split-half). The areas show where the wreckage is possibly on the seabed. "
             "The right half is correct only if the Pléiades objects are aircraft debris. The wreckage moves very little in the water, "
             "so the seabed areas are almost the same as the impact areas. In the top row there are not sufficient samples for a result. Do not use these maps for a search.", fontsize=6.2, va="top", wrap=True)
    fig.text(0.01, 0.165, "Technical: settling core-set run on core (b) (settling 5b595bf, wider GLORYS12V1 column 75-115 E, 45-10 S; breakup table "
             "PROVISIONAL; constraint 'unpowered'), one draw per resampled impact (R600 BTO Only 40,000; Held Out 200,000), reweighted by "
             "composed / sampling weight (composer pass 1; constraint +alive; strata by 00:19-re-weighted P(family)). Composed factors: EoF 3c6319f "
             "(descent <= 6,500 ft/min, PROVISIONAL), drift GLORYS12 50 km (GlobCurrent excluded, audit F1), stand-in L_hyd, Pléiades rating 5 GLORYS12, "
             "searches Phase 2 + Bluefin-21 rho 0.05; not-computed rows carried at the mean. 0.02 deg grid, Gaussian 0.1 deg, HPD; afloat pieces "
             "excluded. ESS = Kish ESS of the reweighted resample; below 1,000 not estimable (settling convention). Holland H1/H2 not estimable and not shown.", fontsize=5.6, va="top", wrap=True, color="#333333")
    fig.savefig(figp, dpi=200); fig.savefig(str(figp).replace(".png", ".pdf")); plt.close(fig)


if __name__ == "__main__":
    main(*sys.argv[1:4])
