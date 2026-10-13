"""Altitude against time, 22:41 hand-off to impact, for a representative sample of descents (Pete, 10 Oct 2026).

Traces come from the module's trace recorder (`smoke/trace-sample.toml` / `trace-dense.toml`), which records a
deterministic hash-selected subset with no effect on the sampled stream. Each trace is joined to its impact row
(impact time and position), so it carries the row's hand-off weight, onset mechanism and option likelihoods.
Two samples per arm, drawn with replacement from the traced set:
  prior      - proportional to the hand-off weight (what the arm proposes before any data after 22:41);
  posterior  - proportional to the weight under the chosen option (default m0011__other: 23:15 BFO + 00:11 BTO/BFO).
The cruise from 22:41 to onset is flown by the core's cruise dynamics and is NOT recorded by the module; it is
drawn as a flat segment at the takeover altitude (core level changes in that interval are not shown).

Usage (from engine/): python vertical_profiles.py OUT_STEM RUN_V1B RUN_V2 [--trace traces-dense.csv] [--option m0011__other] [--n 40]
"""
import argparse, json, pathlib, textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from displacement_hist import option_posteriors

MECH = {0: ("anticipatory", "#1a1a1a", "-"), 1: ("fuel cue", "#6b6b6b", "--"), 2: ("flame-out-associated", "#a8a8a8", "-")}


def load_arm(run, trace_name, option):
    run = pathlib.Path(run); sd = sorted((run / "bto-bfo").glob("seed-*"))[0]
    m = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(m["impact_columns"])}
    X = np.load(sd / "impacts.npy", mmap_mode="r"); g = lambda k: np.array(X[:, cols[k]], float)
    post = {k: p for k, p, c in option_posteriors(run, sd) if k in ("none__other", option)}
    # Join key: impact time to 1 ms and latitude to 1e-6 deg, rounded identically on both sides from the CSV's
    # 6- and 9-decimal text (the finer keys lost ~12% of traces to last-digit rounding differences).
    rows = pd.DataFrame({"imp_t": np.round(np.round(g("unix_s"), 6), 3), "imp_lat": np.round(np.round(g("latitude_deg"), 9), 6), "w_prior": post["none__other"],
                         "w_post": post[option], "mech": g("latent:onset_mechanism"), "onset": g("latent:onset_unix_s"), "to_alt": g("takeover_altitude_ft")})
    tr = pd.read_csv(run / trace_name, header=None, names=["imp_t", "imp_lat", "imp_lon", "t", "alt", "vz"])
    tr["imp_t"] = tr["imp_t"].round(3); tr["imp_lat"] = tr["imp_lat"].round(6)
    rows = rows.drop_duplicates(subset=["imp_t", "imp_lat"], keep=False)  # an ambiguous key is dropped, never mis-joined
    keys = tr[["imp_t", "imp_lat"]].drop_duplicates()
    j = keys.merge(rows, on=["imp_t", "imp_lat"], how="left")
    return m, tr, j


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("stem"); ap.add_argument("v1b"); ap.add_argument("v2")
    ap.add_argument("--trace", default="traces-dense.csv"); ap.add_argument("--option", default="m0011__other"); ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--labels", default="V1b,V2", help="panel labels for the two runs"); ap.add_argument("--note", default="", help="extra footnote text (envelope overlays etc.)")
    a = ap.parse_args(); rng = np.random.default_rng(20261010)
    fig, axs = plt.subplots(2, 2, figsize=(10.5, 6.6), sharex=True, sharey=True, gridspec_kw=dict(hspace=0.22, wspace=0.06))
    info = {}
    labels = a.labels.split(","); assert len(labels) == 2, a.labels
    for col, (arm, run) in enumerate(((labels[0], a.v1b), (labels[1], a.v2))):
        m, tr, j = load_arm(run, a.trace, a.option)
        ep = {e["id"]: e["logged_unix_s"] for e in m["terminal"]["epochs"]}; t0 = m["stop"]["unix_s"]
        groups = dict(tuple(tr.groupby(["imp_t", "imp_lat"])))
        info[arm] = {"traced_descents": int(len(j)), "joined": int(j["w_prior"].notna().sum()), "join_rate": float(j["w_prior"].notna().mean())}
        for row, wcol in enumerate(("w_prior", "w_post")):
            ax = axs[row, col]; w = j[wcol].fillna(0).to_numpy(); ok = w > 0
            ess = float(w[ok].sum() ** 2 / np.sum(w[ok] ** 2)) if ok.any() else 0.0
            info[arm][wcol + "_traced_ess"] = ess
            pick = rng.choice(np.flatnonzero(ok), size=a.n, replace=True, p=w[ok] / w[ok].sum()) if ok.any() else []
            for i in pick:
                r = j.iloc[i]; t = groups[(r.imp_t, r.imp_lat)]
                lab, colr, ls = MECH.get(int(r.mech), ("?", "#000000", ":"))
                hrs = lambda x: (np.asarray(x) - t0) / 3600.0
                ax.plot(hrs([t0, r.onset]), [r.to_alt, r.to_alt], color=colr, lw=0.6, ls=":", alpha=0.7)
                ax.plot(hrs(t["t"]), t["alt"], color=colr, lw=0.8, ls=ls, alpha=0.85)
            for e, nm, ha in (("m2315", "23:15", "left"), ("m0011", "00:11", "right"), ("m0019a", "00:19", "left")):
                ax.axvline((ep[e] - t0) / 3600.0, color="#4a6fa5", lw=0.7, ls="--"); ax.text((ep[e] - t0) / 3600.0, 44500, (" " + nm) if ha == "left" else (nm + " "), fontsize=6.5, color="#4a6fa5", va="top", ha=ha)
            ax.set_ylim(0, 45000); ax.grid(True, color="#e6e6e6", lw=0.5); ax.tick_params(labelsize=7)
            what = "prior (hand-off weight, no data after 22:41)" if row == 0 else f"posterior under {a.option} (23:15 BFO + 00:11 BTO/BFO)"
            ax.set_title(f"{arm}: {what}\n{a.n} draws (with replacement); traced-subset ESS {ess:,.0f}", fontsize=7.5, loc="left")
            if col == 0: ax.set_ylabel("pressure altitude (ft)", fontsize=7.5)
            if row == 1: ax.set_xlabel("hours after the 22:41 hand-off", fontsize=7.5)
    hs = [Line2D([], [], color=c, ls=s, lw=1.0, label=f"onset: {l}") for l, c, s in MECH.values()] + [Line2D([], [], color="#777777", ls=":", lw=0.8, label="cruise to onset (core-flown; drawn flat at takeover altitude)")]
    fig.legend(handles=hs, loc="lower center", ncol=4, frameon=False, fontsize=6.8, bbox_to_anchor=(0.5, -0.02))
    m = json.loads((pathlib.Path(a.v2) / "run.json").read_text())
    foot = (f"Runs: {pathlib.Path(a.v1b).name}, {pathlib.Path(a.v2).name}, seed 1 (terminal stage on core 'reference-289', hand-off m2241, prior track "
            f"{m['config']['prior']['track_deg']} deg). 100,000 parents x {m['terminal']['children']} children x 4 descents per arm; traces from a hash-selected subset "
            f"({a.trace}), joined to their impact rows. Labels: SMOKE; UNCORRECTED FUEL (22:41 fuel state, audit F1-F4); PROVISIONAL SAMPLER (22:41 population "
            f"before core request 17). Descent burn with the ICAO EEDB Trent 892 idle floor. Point-mass descent; PROVISIONAL dive class; Boeing-calibrated glide band. "
            f"Code {m['code_revision']}." + ((" " + a.note) if a.note else ""))
    fig.text(0.02, -0.07, "\n".join(textwrap.wrap(foot, 210)), fontsize=5.6, color="#333333", ha="left", va="top")
    fig.suptitle(f"Altitude from the 22:41 hand-off to impact: representative descents, {labels[0]} and {labels[1]}", fontsize=8.5, x=0.02, ha="left", y=0.995)
    fig.savefig(a.stem + ".png", dpi=200, bbox_inches="tight"); fig.savefig(a.stem + ".pdf", bbox_inches="tight")
    pathlib.Path(a.stem + ".json").write_text(json.dumps(info, indent=1)); print(json.dumps(info))


if __name__ == "__main__":
    main()
