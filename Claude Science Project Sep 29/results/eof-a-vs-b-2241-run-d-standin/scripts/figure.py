import json, pathlib, textwrap
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
W = pathlib.Path(__file__).resolve().parents[1]; A = json.load(open(W / "abd" / "aggregate.json"))
STR = [("next-d-free", "Free"), ("next-d-repro-radar", "Davey dynamics + radar"), ("next-d-routes", "Routes"), ("next-d-descent-climb", "Descent-climb")]
OPT = [("m0011", "00:19 Held Out"), ("m0011+r600-bto", "00:19 R600 BTO Only"), ("m0011+r600/no-offset", "00:19 R600 BTO + Raw BFO")]
FOCAL, CMP, GREY = "#1f4e79", "#c07a1a", "#8a8a8a"
plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7, "font.family": "DejaVu Sans"})
fig = plt.figure(figsize=(7.2, 5.6)); gs = fig.add_gridspec(1, 3, left=0.25, right=0.985, top=0.78, bottom=0.36, wspace=0.07)
rows = [(s, l) for s, l in STR] + [("mix", "Mixture of strata"), ("runc", "Run C, descent-climb only")]
ny = len(rows); axes = []
for j, (key, lab) in enumerate(OPT):
    ax = fig.add_subplot(gs[0, j], sharey=axes[0] if axes else None); axes.append(ax)
    ax.axvline(0, color="#444", lw=0.7, zorder=0)
    for i, (s, l) in enumerate(rows):
        y = ny - 1 - i
        for ver, dy, col in (("", 0.13, FOCAL), ("~v212", -0.13, CMP)):
            if s == "mix": d = A["mixed"]["stop_evidence"]["options"].get(key + ver)
            elif s == "runc":
                if ver: continue
                v = [A["run_c_descent_climb_eof"][k].get(key) for k in sorted(A["run_c_descent_climb_eof"])]
                v = [x for x in v if x is not None]
                d = {"per_seed": v, "ln_BF_mean": float(np.mean(v)), "seed_se": float(np.std(v, ddof=1) / np.sqrt(len(v))), "estimable": None} if len(v) > 1 else None
            else: d = A["per_stratum"].get(s, {}).get(key + ver)
            if not d: ax.text(0.02, y + dy, "not run" if s != "runc" else "not scored", fontsize=6, color=GREY, va="center", transform=ax.get_yaxis_transform()); continue
            c = GREY if s == "runc" else col
            ax.scatter(d["per_seed"], [y + dy] * len(d["per_seed"]), s=7, color=c, alpha=0.45, lw=0, zorder=2)
            m, se = d["ln_BF_mean"], d["seed_se"]
            filled = d.get("estimable") is not False
            ax.errorbar(m, y + dy, xerr=2 * se if np.isfinite(se) else None, fmt="o", ms=4.2, color=c, mfc=c if filled else "white", mew=1, elinewidth=1, capsize=1.5, zorder=3)
    ax.set_title(lab, loc="left"); ax.set_xlabel("ln Bayes factor, A against B")
    ax.set_xlim(-1.5, 3.5); ax.margins(y=0.06)
    if j: plt.setp(ax.get_yticklabels(), visible=False)
axes[0].set_yticks(range(ny)); axes[0].set_yticklabels([l for _, l in rows][::-1])
for a in axes: a.tick_params(axis="y", length=0)
fig.text(0.015, 0.955, "Cruise to fuel exhaustion (A) against a deliberate descent before exhaustion (B), flown from 22:41", fontsize=8.5, weight="bold")
fig.text(0.015, 0.92, "UNCONVERGED. Positive values favour A. Core run D, four strata, four seeds each.", fontsize=7.5)
from matplotlib.lines import Line2D
h = [Line2D([], [], marker="o", ls="", color=FOCAL, ms=4, label="all impacts"), Line2D([], [], marker="o", ls="", color=CMP, ms=4, label="impacts above 212 m/s removed"),
     Line2D([], [], marker="o", ls="", color=GREY, ms=4, label="run C (module's own runs)"), Line2D([], [], marker="o", ls="", mfc="white", color=FOCAL, ms=4, label="open circle: not estimable")]
fig.legend(handles=h, loc="upper left", bbox_to_anchor=(0.01, 0.905), ncol=4, frameon=False, handletextpad=0.3, columnspacing=1.0)
ste = ("Simplified English: Each dot is one seed. The large dot is the mean of the seeds. The bar is two standard errors of the seed mean. "
       "A is a cruise until the fuel is gone, then a descent. B is a deliberate descent before the fuel is gone, with an approach to ditching. "
       "The two flight types use the same data, so the difference is a Bayes factor. The core result is not converged. "
       "The end-of-flight physics is provisional: there is no structural speed limit, no push-over and no Boeing system sequence. "
       "Descent rates above 6,500 ft/min and unloading cannot occur in the model. The run was done by a stand-in for the module.")
tec = ("Technical: ln BF = ln Z(A) - ln Z(B), Z self-normalised over the corrected look-ahead hand-off weights (w exp(log_correction)); seed s.e. over N = 4 seeds "
       "(100,000 rows x 4 children x 4 descents). Gate: >= 30 effective parents per seed in both arms and seed s.e. <= 0.25. Mixture: equal stratum priors "
       "x [stop] log-evidence to 22:41 (core request 18). Held Out = 23:15 BFO + 00:11 BTO/BFO; R600 BTO Only adds the 00:19:29 BTO (sd from satcom-observations.csv); "
       "Raw BFO = no-offset model. 212 m/s = 1.25 VMO, normalised by the unfiltered total. Log-on cause 'other'. Binary 097a5d77; recipe full/sweep_2241_ab.sh.")
y = 0.235
for t in (ste, tec):
    s = "\n".join(textwrap.wrap(t, 168)); fig.text(0.015, y, s, fontsize=5.5, va="top", color="#222"); y -= 0.0195 * (s.count("\n") + 1) + 0.012
fig.savefig(W / "eof-a-vs-b-2241-run-d-standin.png", dpi=300); print("saved")
