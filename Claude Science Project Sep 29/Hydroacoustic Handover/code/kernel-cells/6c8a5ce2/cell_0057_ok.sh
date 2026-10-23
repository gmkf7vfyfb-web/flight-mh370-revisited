cd .tmp/standin; cat > chart_tau.py <<'EOF'
import json, sys, textwrap, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.ticker
sys.path.insert(0, "../hy/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare")
import imos_stageB_map as B, f35a_eta_calibration as F
H = json.load(open("tau90_hist.json")); S = json.load(open(sys.argv[1])); tag = sys.argv[2]
plt.rcParams.update({"font.size": 9, "axes.titlesize": 9.5, "legend.fontsize": 7.5})
fig = plt.figure(figsize=(13, 7.0)); ax = [fig.add_axes([0.06 + i * 0.335, 0.37, 0.27, 0.52]) for i in range(3)]
e = np.array(H["edges"]); c = np.sqrt(e[1:] * e[:-1]); w = np.diff(np.log10(e))
names = {"next-c-free": "free", "next-c-repro-radar": "Davey dynamics + radar", "next-c-descent-climb": "descent-climb", "next-c-routes": "routes"}
cols = {"next-c-free": "#1b9e77", "next-c-repro-radar": "#d95f02", "next-c-descent-climb": "#7570b3", "next-c-routes": "#e7298a"}
for st, d in H["strata"].items():
    h = np.array(d["hist"]); ax[0].step(c, h / h.sum() / w, where="mid", color=cols[st], lw=1, label=f"Water-entry model, {names[st]}")
x = np.logspace(np.log10(0.05), 1, 50); ax[0].plot(x, np.full_like(x, 1 / np.log10(200)), "k--", lw=1.2, label="Module scenario prior (log-uniform 0.05–10 s)")
ax[0].axvspan(10, 100, color="0.9", lw=0); ax[0].text(12, 0.05, "set to 10 s\nby the lookup", fontsize=7)
ax[0].set_xscale("log"); ax[0].set_xlim(0.03, 60); ax[0].set_xlabel("Energy-transfer duration τ (s)"); ax[0].set_ylabel("Probability density per decade (rows, unweighted)")
ax[0].set_title("A. Duration: water-entry model vs scenario prior"); ax[0].legend(frameon=False, loc="upper left")
tau = np.logspace(np.log10(0.05), 1, 200); fr = sum(B.band_fraction(fc, 1 / tau, 2) for fc in F.BANDS)
ax[1].plot(tau, 10 * np.log10(fr), "k-"); ax[1].set_xscale("log"); ax[1].set_xlabel("Assumed source duration τ (s)")
ax[1].set_ylabel("Share of source energy in 5–40 Hz (dB)"); ax[1].set_title("B. Why τ matters: energy in the detection band")
keys = [k for k in S if "/seed-" in k]; strata = [s for s in names if any(k.startswith(s + "/") for k in keys)]
for j, st in enumerate(strata):
    ks = [k for k in keys if k.startswith(st + "/")]
    for i, (lab, key) in enumerate((("scenario prior", "scenario_tau"), ("water-entry model", "eof_tau90"))):
        v = [S[k][key]["share_le_m1"] for k in ks]
        ax[2].plot(np.full(len(v), j + (i - 0.5) * 0.3), v, "o" if i else "s", color=cols[st], mfc="none" if i == 0 else cols[st], ms=4,
                   label=(f"τ from {lab}" if j == 0 else None))
ax[2].set_xticks(range(len(strata))); ax[2].set_xticklabels([names[s] for s in strata], rotation=15, fontsize=8)
ax[2].set_ylabel("Share of rows with soft log-likelihood ≤ −1"); ax[2].set_title(f"C. Rows the non-detections penalise\n(open: scenario prior; filled: water-entry model; {tag})")
ax[2].legend(frameon=False, loc="lower right")
fig.text(0.5, 0.965, "Run C sensitivity: impact duration from the end-of-flight water-entry model. UNCONVERGED (core (b) split-half not converged). Sensitivity only, not a likelihood.", ha="center", fontsize=10, weight="bold")
diffs = [S[k]["paired_diff"] for k in keys]
ste = ("STE100: Panel A compares two sets of values for how long the impact puts energy into the water: the new end-of-flight model and the range the module used before. "
       "The model gives longer durations for most rows (ditching), and short ones for steep dives. Panel B: a longer duration puts less energy into the band the hydrophones use. "
       "Panel C: the share of rows that the 'no signal seen' evidence counts against is almost the same with both duration sets. The change does not move the result.")
tech = (f"Technical: module writer per_impact_lnl.py (amendment 2 daa7abc3, fix 3b5b4446; --calerr structured --noise blackman), nuisance stream unchanged, only τ replaced by tau90_v1.npz "
        f"(impact_tau_method = 1, ruling 8dbefed2; results/eof-impact-tau-method-oct11.md); mechanical τ90 used as acoustic source duration (stand-in assumption, module to rule). "
        f"lnL_soft is the exploratory near-limit term (borrowed IMS P_D, TL NOT CALIBRATED). {len(keys)} seed(s); paired Δ lnL_soft per row: median of seed means "
        f"{np.median([d['mean'] for d in diffs]):+.4f}, worst seed q01/q99 {min(d['q01'] for d in diffs):+.2f}/{max(d['q99'] for d in diffs):+.2f}. Rows unweighted (as the module's own summary); "
        f"~6% of rows have τ > 10 s, clamped by the module's lookup; band fraction ESD flat to 1/τ then f^-2.")
fig.text(0.015, 0.225, textwrap.fill(ste, 228), fontsize=7.3, va="top"); fig.text(0.015, 0.125, textwrap.fill(tech, 240), fontsize=7.0, va="top", color="0.2")
fig.savefig("hydroacoustics-run-c-tau-sensitivity-standin.png", dpi=160); fig.savefig("hydroacoustics-run-c-tau-sensitivity-standin.pdf")
EOF
python chart_tau.py smoke_tau/summary.json "smoke: free seed 1" && echo ok