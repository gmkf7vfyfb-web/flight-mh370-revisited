#!/usr/bin/env python3
"""Charts for the stand-in rho sweep and Davey eq. (11.2) curve on core (b). Reads standin-sweep-b.json.

    python standin_charts_b.py <standin-sweep-b.json> <out-dir>
"""
import json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = json.loads(Path(sys.argv[1]).read_text()); OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
OPTS = [("none__other+unpowered", "00:19 Held Out", "#1d5aa6"),
        ("r600-bto__other+unpowered", "00:19 R600 BTO Only", "#d0731c"),
        ("r600_no-offset__other+unpowered", "00:19 R600 BTO + Raw BFO", "#2b8a5a")]
STRATA = [("b-free", "free speed and turn"), ("b-repro-radar", "Davey dynamics + radar"),
          ("b-descent-climb", "descent-climb"), ("b-routes", "routes")]
RHOS = [0.0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5]
REF = d["rho_reference"]
plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7,
                     "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.spines.top": False, "axes.spines.right": False})


def scen(block, rho):
    return block["scenarios"]["run.toml" if rho == REF else f"rho {rho:g}"]


def footnote(fig, ste, tech, top=0.235):
    fig.text(0.012, top, "Plain (ASD-STE100): " + ste, ha="left", va="top", fontsize=6.6, wrap=True, color="#222")
    fig.text(0.012, top - 0.105, "Technical: " + tech, ha="left", va="top", fontsize=6.2, wrap=True, color="#444")


LABELS = ("UNCONVERGED: core (b) split-half NOT converged; two-tank bookkeeping only; right-dry rows twin-engine "
          "continuation, left pool drained at doubled grid_inop (internal-v1); PROVISIONAL-OVERNIGHT; EoF sweep and this "
          "analysis run by architecture stand-ins, searched areas to review")
PF = d["pfamily"]
PFTXT = "/".join(f"{PF[s]:.3f}" for s, _ in STRATA)

# ---------- Figure 1: rho sweep ----------
fig, axs = plt.subplots(1, 2, figsize=(10.5, 5.4))
fig.subplots_adjust(left=0.07, right=0.985, top=0.90, bottom=0.36, wspace=0.25)
for key, name, col in OPTS:
    m = d["mixture_reweighted"][key]; mf = d["mixture"][key]
    z = [scen(m, r)["z"] for r in RHOS]; on = [scen(m, r)["on_p2"] for r in RHOS]
    axs[0].plot(RHOS, [scen(mf, r)["z"] for r in RHOS], color=col, lw=1.0, ls=(0, (3, 2)))
    axs[1].plot(RHOS, [100 * scen(mf, r)["on_p2"] for r in RHOS], color=col, lw=1.0, ls=(0, (3, 2)))
    for s, _ in STRATA:
        b = d["strata"][s][key]
        axs[0].plot(RHOS, [scen(b, r)["z"] for r in RHOS], color=col, lw=0.6, alpha=0.35)
        axs[1].plot(RHOS, [100 * scen(b, r)["on_p2"] for r in RHOS], color=col, lw=0.6, alpha=0.35)
    axs[0].plot(RHOS, z, color=col, lw=1.8, marker="o", ms=3.5, label=name)
    axs[1].plot(RHOS, [100 * v for v in on], color=col, lw=1.8, marker="o", ms=3.5, label=name)
    axs[1].scatter([0], [100 * m["scenarios"]["before"]["on_p2"]], color=col, marker="_", s=120, lw=1.6, zorder=4)
for ax in axs:
    ax.axvline(REF, color="#555", ls=(0, (2, 2)), lw=0.9)
    ax.set_xlabel("ρ, probability that the wreck is not found where the sonar searched")
    ax.grid(alpha=0.25, lw=0.5); ax.set_xlim(-0.01, 0.51)
axs[0].text(REF + 0.006, axs[0].get_ylim()[0] + 0.01, "reference ρ = 0.05", fontsize=7, color="#555")
axs[0].set_ylabel("Evidence Z = P(no find | searches)")
axs[0].set_title("The searches remove less probability when ρ is larger")
axs[0].legend(loc="lower right", frameon=False, title="Thick: groups mixed, weights updated by 00:19 data\nDashed: fixed group weights; thin: each group", title_fontsize=6.8)
axs[1].set_ylabel("Probability on Phase 2 searched ground after the searches (%)")
axs[1].set_title("ρ controls how much probability stays on searched ground")
axs[1].text(0.06, 0.98, "Short bars at ρ = 0: before the searches", transform=axs[1].transAxes, fontsize=7, va="top", color="#555")
fig.suptitle("Seabed search evidence against ρ, for three uses of the 00:19 data — NOT CONVERGED", fontsize=9, x=0.07, ha="left")
footnote(fig,
         "The chart shows how the result of the seabed searches changes with ρ, the probability that the wreck is in a searched area "
         "but the search did not find it. The impacts come from the core run (b) with the end-of-flight stage, four flight-path groups, "
         "mixed with weights updated by the 00:19 data (dashed lines: fixed weights). The aircraft was transmitting at 00:19:37 and had no electrical power at 01:15:56. The core run is not converged, so these values are provisional. "
         "No published value of ρ exists. The reference is 0.05. Davey et al. (2016, p. 102) use ρ close to 0.",
         "Z = Σ_f P_f Z_f; thick: P_f re-weighted by EoF Ẑ_00:19 (family-evidence-next-run-b.json, +alive keys); dashed: fixed P = "
         f"{PFTXT} (module convention 0.69/0.15/0.14/0.01 renormalised). EoF next-run on core (b) m0011 hand-offs, 4 strata × 4 seeds × "
         "3.2M = 51,200,096 impacts; weights from EoF option_posteriors, log-on cause other, +unpowered (airborne 00:19:37.443, not powered 01:15:56). Campaigns: Phase 2 "
         "(q 0.945, measured valid-data coverage) + Bluefin-21 (q 0.9); no Ocean Infinity. 'On searched ground' = Σ w·c_Phase2. "
         "Holland H1/H2 not yet estimable - targeted sampler in progress (mixture ESS 85/123), not shown. Coverage gap: EoF descent rates "
         "above 6,500 ft/min and unloading not reachable by the model. " + LABELS + ".")
fig.savefig(OUT / "rho-sweep-b.png", dpi=200); fig.savefig(OUT / "rho-sweep-b.pdf")
plt.close(fig)

# ---------- Figure 2: Davey eq. (11.2) ----------
fig, axs = plt.subplots(1, 3, figsize=(12, 5.4), sharey=True)
fig.subplots_adjust(left=0.06, right=0.985, top=0.88, bottom=0.36, wspace=0.08)
for ax, (key, name, col) in zip(axs, OPTS):
    m = d["mixture_reweighted"][key]["planning"]
    cf = d["mixture"][key]["planning"]["curve"]["residual"]
    ax.plot(np.array(cf["km2"]) / 1e3, cf["p_find"], color=col, lw=1.0, ls=(0, (3, 2)), label="fixed group weights")
    for s, _ in STRATA:
        c = d["strata"][s][key]["planning"]["curve"]["residual"]
        ax.plot(np.array(c["km2"]) / 1e3, c["p_find"], color=col, lw=0.6, alpha=0.35)
    cd = m["curve"]["disabled"]; cr = m["curve"]["residual"]
    ax.plot(np.array(cd["km2"]) / 1e3, cd["p_find"], color="#555", lw=1.1, ls=(0, (1, 1.5)), label="if no search had been made")
    ax.plot(np.array(cr["km2"]) / 1e3, cr["p_find"], color=col, lw=1.9, label="after Phase 2 and Bluefin-21")
    for t in ("0.25", "0.5", "0.75"):
        th = m["thresholds"]["residual"][t]
        if th:
            ax.plot([th["km2"] / 1e3], [float(t)], "o", color=col, ms=3.5)
            ax.annotate(f"{th['km2'] / 1e3:,.0f}k km²", (th["km2"] / 1e3, float(t)), xytext=(5, -9),
                        textcoords="offset points", fontsize=6.8, color=col)
    ax.set(xlim=(0, 700), ylim=(0, 0.9), xlabel="Ground searched, best 0.5° blocks first (thousand km²)", title=name)
    ax.grid(alpha=0.25, lw=0.5)
axs[0].set_ylabel("P(find) from a new search, Davey eq. (11.2)")
axs[0].legend(loc="upper left", frameon=False, title="Thick: groups mixed, weights updated by 00:19 data;\nthin: each group", title_fontsize=6.8)
fig.suptitle("Probability of finding the wreck against the area of a new search — NOT CONVERGED", fontsize=9, x=0.06, ha="left")
footnote(fig,
         "The chart shows the probability that a new search finds the wreck, if the search starts with the most probable areas "
         "and continues to less probable areas. The dotted line ignores the earlier searches. The impacts come from the core run (b), "
         "four flight-path groups mixed with weights updated by the 00:19 data; the aircraft was transmitting at 00:19:37 and had no electrical power at 01:15:56. The core run is not converged. "
         "The order of single blocks is not reliable. Use the curve only.",
         "Davey et al. (2016) eq. (11.2), p. 101: P(find | A) = P_D ∫_A p(x | Z) dx, planning P_D = 0.9 (Stone et al. 2014 cap, not the "
         f"module's q), on 0.5° blocks of a 0.1° weighted impact histogram, authalic sphere. Residual = after Phase 2 (q 0.945) + Bluefin-21 "
         f"(q 0.9) at ρ = {REF:g}; no Ocean Infinity. Mixture of maps Σ_f P_f·map_f, P_f re-weighted by EoF Ẑ_00:19 (dashed: fixed {PFTXT}). EoF next-run, 51,200,096 impacts, "
         "option_posteriors, cause other, +unpowered. Holland H1/H2 not yet estimable - targeted sampler in progress. Rapid descents "
         "above 6,500 ft/min and unloading not reachable by the model. " + LABELS + ".")
fig.savefig(OUT / "eq11-2-curve-b.png", dpi=200); fig.savefig(OUT / "eq11-2-curve-b.pdf")
plt.close(fig)
print("charts written")
