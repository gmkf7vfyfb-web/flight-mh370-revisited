"""Composer pass 1 (run C), seabed step (gap G12 fix): settling's aimed resample from the COMPOSED per-row weights.

1. finish: scale the per-stratum pooled row weights exported by summarise_stratum_c.py (G, H) by the products' stratum weights
   W_Q (00:19-re-weighted P(family), report_c.py), derive 'after searches' (Ga = G x L_search, Ha = H x L_search: exact, since the
   searched-areas factor is row-level and pooling multiplies through), and write settling's input contract
   (results/settling-aimed-resample/README.md): <dir>/<option>-<product>/{manifest.json, <stratum>/seed-<k>.f32, SHA256SUMS, READY}.
2. prep: settling's own wf_aimed.py prep (unchanged; run from this workspace, writes ./field/).
3. settle: settling's own wreckage_field test (copy of settling's worktree 9330d4c, unchanged), 2 threads.
4. areas: settled-mass seabed density on settling's grid (0.02 deg, Gaussian 0.1 deg, EoF hpd_levels, authalic cells), as in
   results/composer-pass0/seabed_finish.py (elements share their impact's weight in proportion to mass; afloat pieces excluded).
Usage: python seabed_c.py finish <work> <out exchange dir> | areas <work> <out json>
"""
import hashlib, json, math, os, pathlib, sys
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
REPO = (pathlib.Path(__file__).resolve().parent.parent / "repo/Claude Science Project Sep 29" if (pathlib.Path(__file__).resolve().parent.parent / "repo").exists() else pathlib.Path(__file__).resolve().parents[2])
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(REPO / "engine/hypotheses/end-of-flight/smoke"))
STRATA = ["next-c-free", "next-c-repro-radar", "next-c-descent-climb", "next-c-routes"]
ROOT = "/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run-c"
LABEL = {"r600-bto+unpowered": "00:19 R600 BTO Only", "heldout+unpowered": "00:19 Held Out"}
PNAME = {"G": "G (flight + EoF + drift + hydro)", "Ga": "G after searches", "H": "H (G + Pléiades, given H)", "Ha": "H after searches"}


def finish(work, outd, prods="G,Ga,H,Ha"):
    import seabed_loglik, compact_impacts
    work, outd = pathlib.Path(work), pathlib.Path(outd)
    R = json.loads((work.parent / "out" / "pass1-results.json").read_text())
    for opt in LABEL:
        O = R["options"][opt]
        for prod in prods.split(","):
            base = prod[0]
            W = O["products"][prod]["reweighted-0019"]["stratum_weights"]           # keyed by stratum dir name
            d = outd / f"{opt}-{prod}"; d.mkdir(parents=True, exist_ok=True); sums = []
            for st in STRATA:
                if st not in W:
                    continue
                (d / st).mkdir(exist_ok=True); ws = []
                for k in range(1, 9):
                    w = np.fromfile(work / "export" / f"{opt}-{base}" / st / f"seed-{k}.f32", "<f4").astype(float)
                    if prod.endswith("a"):
                        meta, g = compact_impacts.load(pathlib.Path(ROOT) / st / f"seed-{k}")
                        w = w * np.exp(seabed_loglik.loglik(g("latitude_deg"), g("longitude_deg")))
                    ws.append(w)
                tot = sum(x.sum() for x in ws)
                for k, w in enumerate(ws, 1):
                    f = d / st / f"seed-{k}.f32"; (w / tot * W[st]).astype("<f4").tofile(f)
                    sums.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {st}/seed-{k}.f32")
            man = {"product": f"{opt.split('+')[0]}-{prod}", "label": f"{LABEL[opt]}, {PNAME[prod]}", "option": opt.split("+")[0].replace("heldout", "none") + "__other",
                   "constraint": "unpowered", "run_root": ROOT, "strata": [s for s in STRATA if s in W], "seeds": list(range(1, 9)),
                   "stratum_weights": W, "note": "composer pass 1 (run C), architecture stand-in; run C NOT CONVERGED; values = W_Q(stratum) x pooled within-stratum weight"}
            (d / "manifest.json").write_text(json.dumps(man, indent=1))
            (d / "SHA256SUMS").write_text("\n".join(sums) + "\n"); (d / "READY").write_text("")
            print(d.name, "written", flush=True)


def areas(work, outp, tags="cp1g,cp1h"):
    from scipy.ndimage import gaussian_filter
    from displacement_greyscale import hpd_levels
    res = {"products": []}; maps = {}
    for tag in tags.split(","):
        if not pathlib.Path(f"field/{tag}_info.json").exists():
            print("missing", tag); continue
        info = json.loads(pathlib.Path(f"field/{tag}_info.json").read_text()); z = np.load(f"field/{tag}_draws.npz")
        ext = info["extent_lon_lon_lat_lat"]; G = 0.02
        le = np.arange(ext[2], ext[3] + G / 2, G); oe = np.arange(ext[0], ext[1] + G / 2, G)
        cell = (6371.0072 ** 2) * np.radians(G) * np.abs(np.sin(np.radians(le[1:])) - np.sin(np.radians(le[:-1])))[:, None] * np.ones(len(oe) - 1)[None, :]
        sm = lambda H: (lambda d: d / d.sum())(gaussian_filter(H, 0.1 / G, mode="constant"))
        ar = lambda H: [float(cell[sm(H) >= l].sum()) for l in hpd_levels(sm(H), (0.99, 0.9, 0.5))]
        for j, p in enumerate(info["products"]):
            if not pathlib.Path(f"field/{tag}P{j}_elements.f64").exists():
                print("no elements", tag, j); continue
            T = np.fromfile(f"field/{tag}P{j}_impacts.f64", "<f8").reshape(-1, 14)
            EL = np.fromfile(f"field/{tag}P{j}_elements.f64", "<f8").reshape(-1, 8)
            rows, draws = z[f"rows_{j}"], z[f"draws_{j}"]
            st_ = EL[:, 4] == 0
            key = EL[st_, 0].astype(np.int64) * 1048576 + EL[st_, 1].astype(np.int64)
            o = np.argsort(key, kind="stable"); key, lat, lon, mass = key[o], EL[st_, 5][o], EL[st_, 6][o], EL[st_, 7][o]
            uk, start = np.unique(key, return_index=True); stop = np.r_[start[1:], len(key)]
            share = mass / np.repeat(np.add.reduceat(mass, start), stop - start)
            want = rows.astype(np.int64) * 1048576 + draws.astype(np.int64)
            pos = np.minimum(np.searchsorted(uk, want), len(uk) - 1); ok = uk[pos] == want
            n_el = (stop - start)[pos[ok]]; idx = np.concatenate([np.arange(a_, b_) for a_, b_ in zip(start[pos[ok]], stop[pos[ok]])])
            w = share[idx] / ok.sum()
            Hw = np.histogram2d(lat[idx], lon[idx], bins=[le, oe], weights=w)[0]
            imp = T[rows, 1:3]; Hs = np.histogram2d(imp[:, 0], imp[:, 1], bins=[le, oe])[0]
            il, io = np.repeat(imp[ok, 0], n_el), np.repeat(imp[ok, 1], n_el)
            off = np.hypot((lat[idx] - il) * 111.2, (lon[idx] - io) * 111.2 * np.cos(np.radians(il))); oo = np.argsort(off); c = np.cumsum(w[oo]) / w.sum()
            fate = EL[:, 4]; em = EL[:, 7]
            e = {"tag": tag, "j": j, "label": p["manifest"]["label"], "product": p["manifest"]["product"], "N": p["N"], "row_ess_kish": p["row_ess_kish"],
                 "distinct_impacts": p["distinct_impacts"], "nan_weight_rows": p["nan_weight_rows"], "impact_area90_all_rows_km2": p["impact_area90_km2_all_rows"],
                 "outcomes_outside_settling_domain": int((~ok).sum()), "impact_area_km2_99_90_50": ar(Hs), "seabed_area_km2_99_90_50": ar(Hw),
                 "offset_km_p50_p90_p99": [float(off[oo][np.searchsorted(c, q)]) for q in (0.5, 0.9, 0.99)],
                 "afloat_mass_share_unweighted": float(em[fate == 1].sum() / em[fate >= 0].sum()),
                 "seabed_mean_lat_lon": [float(np.average(lat[idx], weights=w)), float(np.average(lon[idx], weights=w))],
                 "estimable": bool(p["row_ess_kish"] >= 1000 and p["distinct_impacts"] >= 1000)}
            res["products"].append(e); maps[e["product"]] = (sm(Hs).astype(np.float32), sm(Hw).astype(np.float32), le, oe)
            print(e["label"], round(e["row_ess_kish"]), e["distinct_impacts"], [round(x / 1e3, 1) for x in e["seabed_area_km2_99_90_50"]], flush=True)
    pathlib.Path(outp).write_text(json.dumps(res, indent=1))
    figure(maps, res, pathlib.Path(outp).with_name("fig5-seabed.png"))


def figure(maps, res, figp):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from displacement_greyscale import hpd_levels
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 7.2, "axes.labelsize": 8, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
                         "axes.spines.top": False, "axes.spines.right": False, "font.family": "DejaVu Sans"})
    fig, axes = plt.subplots(2, 4, figsize=(8.0, 7.6), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.86, bottom=0.31, wspace=0.06, hspace=0.32)
    col = {"G": "#1f5fa8", "Ga": "#1f5fa8", "H": "#c2571a", "Ha": "#c2571a"}
    E = {e["product"]: e for e in res["products"]}
    for r, opt in enumerate(("r600-bto", "heldout")):
        for c, pid in enumerate(("G", "Ga", "H", "Ha")):
            ax = axes[r, c]; key = f"{opt}-{pid}"
            ax.set_title({"G": "Drift and sound", "Ga": "... after the seabed searches", "H": "Pléiades objects added", "Ha": "... after the seabed searches"}[pid], loc="left")
            if key not in maps:
                ax.text(0.5, 0.5, "not available", transform=ax.transAxes, ha="center", fontsize=7); continue
            di, dw, le, oe = maps[key]; lc, oc = 0.5 * (le[1:] + le[:-1]), 0.5 * (oe[1:] + oe[:-1])
            lv = hpd_levels(dw, (0.9, 0.5)); ax.contourf(oc, lc, dw, levels=[lv[0], lv[1], dw.max() * 1.01], colors=["#d9d9d9", col[pid]], alpha=0.9)
            ax.contour(oc, lc, di, levels=hpd_levels(di, (0.9,)), colors="k", linewidths=0.5, linestyles="--")
            e = E[key]; ax.text(0.02, 0.02, f"90 %: {e['seabed_area_km2_99_90_50'][1] / 1e3:,.0f}k km²\n50 %: {e['seabed_area_km2_99_90_50'][2] / 1e3:,.0f}k km²", transform=ax.transAxes, fontsize=6.0, va="bottom", bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1))
            ax.set_xlim(84, 106); ax.set_ylim(-43, -22)
        axes[r, 0].set_ylabel("Latitude (degrees)")
        fig.text(0.01, axes[r, 0].get_position().y1 + 0.04, "00:19 R600 BTO Only (primary)" if r == 0 else "00:19 Held Out", fontsize=8, fontweight="bold")
    for ax in axes[1]:
        ax.set_xlabel("Longitude (degrees east)")
    fig.suptitle("Where the wreckage is on the seabed, for each set of evidence", x=0.01, ha="left", fontsize=9, y=0.985)
    fig.text(0.01, 0.950, "Grey: 90 % region of the wreckage. Colour: 50 % region. Dashed line: 90 % region of the impact point.", fontsize=7)
    fig.add_artist(matplotlib.lines.Line2D([0.01, 0.99], [0.235, 0.235], color="#999999", lw=0.5))
    fig.text(0.01, 0.228, "NOT CONVERGED (core run C). The areas show where the wreckage is possibly on the seabed. The right half is correct only if the "
             "Pléiades objects are aircraft debris. The wreckage moves very little as it sinks, so the seabed areas are almost the same as the impact "
             "areas. Do not use these maps for a search.", fontsize=6.1, va="top", wrap=True)
    fig.text(0.01, 0.160, "Technical: G panels: settling's published aimed samples (settling/next-run-c-composed-aimed); Pléiades panels: the stand-in's run of the same tools. Settling's aimed resample (results/settling-aimed-resample/wf_aimed.py) of 40,000 impacts drawn from the composed per-row "
             "weights (composer pass 1, run C, +unpowered; strata by 00:19-re-weighted P(family)); one settling draw each with settling's wreckage_field "
             "test (copy of settling 9330d4c; real ocean GLORYS12V1 column, breakup table PROVISIONAL). After searches = composed weight x searched-areas "
             "likelihood per row (point target, rho 0.05). Factors: EoF run C (no structural limit, G13; descents <= 6,500 ft/min), drift GLORYS12 only, "
             "current nodes (GlobCurrent excluded, F1; not-computed rows carried), stand-in hydro + F8 (predictive, not calibrated), Pléiades v2 rating 5, "
             "equal, GLORYS12, given H. 0.02 deg grid, Gaussian 0.1 deg, HPD on settled mass; afloat pieces excluded. Row ESS (Kish) >= 1,000 required. "
             "Holland H1/H2 not estimable.", fontsize=5.4, va="top", wrap=True, color="#333333")
    fig.savefig(figp, dpi=200); fig.savefig(str(figp).replace(".png", ".pdf")); plt.close(fig)


if __name__ == "__main__":
    {"finish": finish, "areas": areas}[sys.argv[1]](*sys.argv[2:])
