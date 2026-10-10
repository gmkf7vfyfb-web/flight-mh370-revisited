"""Figure for the conditional branch (branch_eof289.py output), with the run's key facts as a footnote.

    python branch_figure.py <branch dir> <module dir> <out stem>

Every chart from this module carries a footnote naming: the source posterior and its prior track, the
00:19 data option and log-on cause, the end-of-flight physics status, the search case, the ocean models
and spread, the object and contact choices, and what is excluded (Pete, 9 Oct 2026).
"""
import sys as _sys
from pathlib import Path as _P
_sys.path.insert(0, str(_P(__file__).resolve().parent))
import json
import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd


def footnote(fig, lines, width=180, size=5.5, y=-0.01):
    """Wrap and place `lines` (list of str) under the figure; returns the text artist."""
    text = "\n".join(textwrap.fill(l, width=width, subsequent_indent="   ") for l in lines)
    return fig.text(0.01, y, text, ha="left", va="top", fontsize=size, color="#333333", transform=fig.transFigure)


def hdr_level(dens, mass, level=0.9):
    o = np.argsort(dens.ravel())[::-1]
    c = np.cumsum(mass.ravel()[o])
    return dens.ravel()[o][min(np.searchsorted(c, level), len(o) - 1)]


BRANCH_NOTES = [
    "Source: end of flight's reference-289 impacts, run eof-289-full (hand-off runs/snap289-m0011 at 00:11), prior track 289.7 deg (sd 1.0) at "
    "18:01:49 UTC; base config (run.json) davey2016 + no-exhaustion-prior + reference-snapshots + early-families/overnight/reference-289 + "
    "end-of-flight full/reference-289. 4 seeds pooled with equal weight; 100,000 parents x 8 children x 4 descents per seed = 12,799,968 impacts; "
    "all four control families (ditching-attempt, maintained-then-lost, no-intervention, upset-then-recovery) pooled.",
    "BFO model to 00:11: constant per-trajectory bias, Kalman-marginalised, prior 150 +/- 25 Hz (Davey et al. 2016 sec. 5.3 / 8.1), 7 Hz BFO "
    "sigma baseline; altitude 25,000-43,000 ft, Mach 0.73-0.84, five navigation modes.",
    "{OPTION_LINE}",
    "End-of-flight physics PROVISIONAL: dive class (b) (being rebuilt against Boeing's simulator runs); Boeing-calibrated glide (Pete's reference).",
    "Search (row 2): the searched-areas module's own per-impact likelihood, base case Phase 2 2014-17 + Bluefin-21, point target, "
    "undetectable probability rho = 0.05; Ocean Infinity 2018 not applied.",
    "Under H (columns 2-4): ocean models GLORYS12 + ERA5 and GlobCurrent daily + ERA5, equal weight (P+C formed per model, then averaged); "
    "measured transport error (GDP-replay OU fit per component, no added diffusivity); windage 0-5 % uniform; released 00:20 UTC 8 Mar.",
    "Pleiades: rating-5 objects merged into 6 clusters at 3 km, equal cluster weights (rho4 = 0). COSMO-SkyMed: all four contacts, equal weights, dawn-20 Mar "
    "and dusk-21 Mar passes equally weighted; source, time and footprint unverified.",
    "Shading: density normalised to its maximum. Solid blue: 90 % HDR of the panel's PDF. Dashed grey: 90 % HDR of the flight posterior at the same stage. "
    "Circles: Pleiades rating-5 clusters; triangles: COSMO-SkyMed contacts. Grid 0.05 deg; 1.5-2.0 % of impact weight lies outside 85-103 E, 43-25 S and is not shown.",
    "Every PDF in columns 2-4 is conditional on H (the objects are debris from 9M-MRO); no Bayes factor or P(H | data) is computed or implied.",
]


OPTION_TEXT = {
    "none": "00:19 data option 'none' (project priority 1): neither 00:19 satellite message (R600 log-on request 00:19:29.416, "
            "R1200 00:19:37.443) scores the impacts (held out)",
    "r600/no-offset": "00:19 data option 'r600/no-offset' (project priority 2, R600 only, raw): the 00:19:29.416 R600 log-on request's BTO "
                      "and BFO score the impacts with no offset manipulation; R1200 held out",
    "r600/inflated": "00:19 data option 'r600/inflated' (project sensitivity): R600 BTO and BFO scored with an independent zero-mean "
                     "inflated BFO error; R1200 held out",
    "r1200/inflated": "00:19 data option 'r1200/inflated' (project sensitivity): R1200 BFO scored with an independent zero-mean inflated "
                      "BFO error; R600 held out",
}


def run_provenance(impacts_root):
    """Source line built from the impacts' own run.json (standing rule: the run, prior track and base config
    come from run.json, never from memory). Returns None when no run.json is found."""
    root = Path(impacts_root)
    runs = sorted(root.glob("seed-*/run.json"))
    if not runs:
        return None
    j = json.loads(runs[0].read_text())
    c = j.get("config", {})
    pr = c.get("prior", {})
    smp = c.get("sampler", {})
    chain = " + ".join(Path(x).stem if "sensitivity" in x or "davey" in x else x for x in j.get("config_paths", []))
    tem = smp.get("temper_epochs")
    tem_txt = (f"tempered sampler ({', '.join(tem)}, {smp.get('temper_stages')} stages)" if tem else "untempered sampler")
    srun = j.get("source_run") or ""
    srun = Path(srun).name if str(srun).startswith("/") else srun
    return (f"Source: impacts {root.name} ({len(runs)} seeds pooled with equal weight; source run {srun}, "
            f"code {j.get('code_revision')}); prior track {pr.get('track_deg')} deg (sd {pr.get('track_sd_deg')}); "
            f"config chain (run.json): {chain}; {tem_txt}; particles per mode {c.get('particles_per_mode')}; "
            f"BFO bias (run.json bfo_bias): {json.dumps(c.get('bfo_bias'), separators=(',', ':'))[:200]}.")


def make(branch_dir, module_dir, out, plt, panel_letter=None, labels=None):
    B, M = Path(branch_dir), Path(module_dir)
    Z = np.load(B / "branch-maps.npz")
    lat, lon, area, pre, post = Z["lat"], Z["lon"], Z["area"], Z["pre"], Z["post"]
    T = pd.read_csv(M / "data/targets-3km.csv")
    T5 = T[T.arm == "rating5"]
    Cc = pd.read_csv(M / "data/cosmo-contacts.csv")
    fields = [("Flight posterior alone\n(no Pléiades or COSMO)", None), ("Pléiades objects only\n(12 rating-5, 23 Mar)", "L_P"),
              ("all four COSMO-SkyMed\nradar contacts only", "L_C4"), ("Pléiades + all four COSMO\ncontacts, one debris field", "L_P+C4")]
    fig, axs = plt.subplots(2, 4, figsize=(7.1, 4.0), sharex=True, sharey=True, gridspec_kw=dict(wspace=0.06, hspace=0.12))
    ext = [lon[0] - 0.025, lon[-1] + 0.025, lat[0] - 0.025, lat[-1] + 0.025]
    for r, (stage, pc) in enumerate([("before search", pre), ("after search", post)]):
        u = pc / pc.sum()
        du = u / area
        for c, (ttl, key) in enumerate(fields):
            L = np.ones_like(pc) if key is None else np.nan_to_num(Z[key])
            m = pc * L
            m = m / m.sum()
            dn = m / area
            ax = axs[r, c]
            ax.imshow(dn / dn.max(), origin="lower", extent=ext, cmap="Greys", vmin=0, vmax=1, aspect=1 / np.cos(np.radians(35)), interpolation="nearest")
            ax.contour(lon, lat, dn, levels=[hdr_level(dn, m)], colors=["#1f5fa8"], linewidths=0.8)
            if c > 0:
                ax.contour(lon, lat, du, levels=[hdr_level(du, u)], colors=["#888888"], linewidths=0.6, linestyles="--")
            if key in ("L_P", "L_P+C3"):
                ax.plot(T5.lon, T5.lat, "o", ms=2, mfc="none", mec="#b03030", mew=0.6)
            if key in ("L_C3", "L_P+C3"):
                ax.plot(Cc.longitude, Cc.latitude, "^", ms=2.5, mfc="none", mec="#7a3fb0", mew=0.6)
            ax.set_xlim(86, 100)
            ax.set_ylim(-41, -28)
            ax.set_yticks(range(-40, -27, 2))
            if r == 0:
                ax.set_title(ttl, loc="left")
            if c == 0:
                ax.set_ylabel(f"Latitude (°), {stage}")
            if r == 1:
                ax.set_xlabel("Longitude (°E)")
    if panel_letter:
        for a, l in zip(axs.ravel(), "abcdefgh"):
            panel_letter(a, l)
    info = json.loads((B / "branch.json").read_text())
    opt = info["option"]
    base, _, con = opt.partition("+")
    from describe import describe_option
    line = "What was run: " + describe_option(base) + f"; log-on cause 'other' (no fuel-exhaustion log-on density). Weight = impact weight x exp(loglik:{base})"
    if con:
        line += (f" x end of flight's existence constraint '{con}' (its own constraint_log_factor; 'alive' = airborne at 00:19:37.443, "
                 "PROVISIONAL-OVERNIGHT, 10 Oct ~04:05 UTC)")
    line += "."
    notes = [n.replace("{OPTION_LINE}", line) for n in BRANCH_NOTES]
    src = run_provenance(info["impacts_root"]) if "impacts_root" in info else None
    if src:
        notes[0] = src
        notes = [n for n in notes if not n.startswith("BFO model to 00:11")]
    if labels:
        notes.insert(1, "Labels: " + labels + ".")
    og = info.get("uncond_mass_outside_grid")
    if og:
        notes = [n.replace("1.5-2.0 % of impact weight", f"{100 * min(og):.1f}-{100 * max(og):.1f} % of impact weight") for n in notes]
    from describe import describe_option
    fig.suptitle(f"If the imaged objects are from 9M-MRO: where the debris entered the sea, before (top) and after (bottom) the "
                 f"Phase 2 + Bluefin-21 search — {describe_option(opt, short=True)}", x=0.01, ha="left", y=1.02, fontsize=7)
    footnote(fig, notes + [f"Label: {info['label']}; generated by prepare/branch_eof289.py + branch_figure.py (hypothesis/pleiades)."])
    fig.savefig(str(out) + ".png", dpi=300, bbox_inches="tight")
    fig.savefig(str(out) + ".pdf", bbox_inches="tight")
    return fig, axs


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    matplotlib.rcParams.update({"font.size": 6, "axes.titlesize": 6.5, "axes.labelsize": 6, "xtick.labelsize": 5.5, "ytick.labelsize": 5.5})
    make(*sys.argv[1:4], plt=plt, labels=(sys.argv[4] if len(sys.argv) > 4 else None))
