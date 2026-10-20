import sys, json, textwrap; sys.path.insert(0, "leg"); import numpy as np, pandas as pd, matplotlib as mpl; mpl.use("Agg"); import matplotlib.pyplot as plt
L = pd.read_json("leg/out/levels.json"); P = pd.read_json("leg/out/conditional_on_h01w_level.json")
NAME = {"H01W": "Cape Leeuwin (IMS)", "PerthCanyon_3376": "Perth Canyon 3376", "PerthCanyon_3315": "Perth Canyon 3315", "H08S": "Diego Garcia South",
        "OHAS_SSEIR": "S-SEIR", "OHAS_SWAMS3": "SW-AMS 3", "OHAS_MAD": "MAD", "OHAS_WKER": "W-KER", "OHAS_NCRO": "N-CRO"}
ORDER = ["H01W", "PerthCanyon_3376", "PerthCanyon_3315", "H08S", "OHAS_SSEIR", "OHAS_SWAMS3", "OHAS_MAD", "OHAS_WKER", "OHAS_NCRO"]
FOC, GRY, ORA = "#1f3b73", "#8c8c8c", "#c26a00"
fig, axs = plt.subplots(1, 3, figsize=(7.2, 3.0), gridspec_kw=dict(width_ratios=[1.25, 1.0, 0.9], wspace=0.62))
ax = axs[0]; ETAS = [1e-4, 1e-3, 1e-2, 1e-1]; y = np.arange(len(ORDER))[::-1]
for k, (eta, mk, col) in enumerate(zip(ETAS, ["o", "s", "D", "^"], ["#c6d0e2", "#8fa3c8", "#4f6aa3", FOC])):
    for i, stn in enumerate(ORDER):
        r = L[(L.D == "D2") & (L.subset == "strip") & (L.station == stn) & np.isclose(L.eta, eta)].iloc[0]; q = r.snr_db_q; yy = y[i] + (k - 1.5) * 0.17
        ax.plot([q[0], q[2]], [yy, yy], color=col, lw=0.8); ax.plot(q[1], yy, mk, ms=3, color=col, label=f"coupling {eta:g}" if i == 0 else None)
ax.axvline(10, color=GRY, lw=0.6, ls="--"); ax.set_yticks(y); ax.set_yticklabels([NAME[s] for s in ORDER]); ax.set_xlabel("Predicted SNR, dB (median, 5-95 %)")
ax.set_title("a  Impacts on the bearing strip", loc="left"); ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=2, fontsize=5.5, handlelength=1)
ax = axs[1]
for i, stn in enumerate([s for s in ORDER if s != "H01W"]):
    for j, (br, col) in enumerate((("T", FOC), ("C", ORA))):
        r = P[(P.D == "D2") & (P.subset == "strip") & (P.anchor == "energy") & (P.station == stn) & (P.branch == br)].iloc[0]; q = r.cond_snr_db_q; yy = len(ORDER) - 2 - i + (0.12 if j == 0 else -0.12)
        ax.plot([q[1] - 1.96 * 7.9, q[1] + 1.96 * 7.9], [yy, yy], color=col, lw=0.8, alpha=0.6); ax.plot(q[1], yy, "o", ms=3, color=col, label=("text time" if br == "T" else "caption time") if i == 0 else None)
yy3376 = len(ORDER) - 2 - 0
ax.plot(4.8, yy3376 + 0.12, "x", color="black", ms=5, mew=1.0, label="largest value in the window (measured)"); ax.plot(8.7, yy3376 - 0.12, "x", color="black", ms=5, mew=1.0)
ax.set_yticks(np.arange(len(ORDER) - 1)[::-1]); ax.set_yticklabels([NAME[s] for s in ORDER if s != "H01W"]); ax.set_xlabel("Predicted SNR, dB (+/- 2 sd of TL)")
ax.set_title("b  Implied by the Cape Leeuwin level", loc="left"); ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.4, -0.2), ncol=2, fontsize=5.5, handlelength=1)
ax = axs[2]; rows = [("strip", "T", "strip, text"), ("timing-consistent T", "T", "timed, text"), ("strip", "C", "strip, caption"), ("timing-consistent C", "C", "timed, caption")]
for i, (sub, br, lab) in enumerate(rows):
    r = P[(P.D == "D2") & (P.subset == sub) & (P.anchor == "energy") & (P.station == "PerthCanyon_3376") & (P.branch == br)].iloc[0]; q = r.eta_req_q; yy = len(rows) - 1 - i
    ax.plot([q[0], q[2]], [yy, yy], color=FOC if br == "T" else ORA, lw=1.0); ax.plot(q[1], yy, "o", ms=3.5, color=FOC if br == "T" else ORA)
ax.axvspan(1e-4, 1e-1, color="#eeeeee", zorder=0); ax.axvline(2.7e-3, color=GRY, lw=0.8, ls="--"); ax.text(2.7e-3, len(rows) - 0.45, "airframe\nanchor", fontsize=5.5, ha="center", va="bottom", color="#555555")
ax.set_xscale("log"); ax.set_xlim(3e-5, 5); ax.set_ylim(-0.6, len(rows) + 0.4); ax.set_yticks(range(len(rows))[::-1]); ax.set_yticklabels([r[2] for r in rows])
ax.set_xlabel("Coupling needed to match the\nCape Leeuwin level (5/50/95 %)"); ax.set_title("c  Coupling needed", loc="left")
f1 = ("(i) Panel a shows how loud the impact sound would be at each station for four values of the coupling. Panel b uses the measured level at Cape Leeuwin and shows the "
      "level that the other stations would then get. Crosses show the largest level that Perth Canyon measured. Panel c shows the coupling that the Cape Leeuwin level needs. The grey band is the coupling range that we use.")
f2 = ("(ii) Source posterior: run J, 74 seeds, headline 'D2 total q=0.333 (C2 silent)' (00:19 option D2, log-on cause mixture p=0.75, C2 silent); strip = bearing 306.18 +/-1 deg, arc -60 to +250 km "
      "(ESS 172; timed subsets weighted by the pre-registered H01W arrival term, ESS 11 text / 5 caption, provisional). Physics: SE = eta E rho c/2pi sum S_b(tau90) 10^(-TL/10); TL BORROWED from the nearest "
      "committed path (31.6 S 96.8 E), range-adjusted, sd 7.9 dB; propagation slope misfit +10 dB/oct (H01W) and coupling uncertainty apply; OHASISBIO noise and TL are H08S proxies, ridge loss not included. "
      "Measured level: digitised Kadri Fig. 9c, max 1 s mean-square excess 0.128 / 0.069 Pa^2. Search case and ocean model: n/a. Excluded: NE-AMS, H08N, Portland, Scott Reef.")
fig.text(0.01, -0.2, "\n".join(textwrap.wrap(f1, 200)), fontsize=5.5, ha="left", va="top"); fig.text(0.01, -0.29, "\n".join(textwrap.wrap(f2, 200)), fontsize=5.5, ha="left", va="top", color="#444444")
fig.savefig("leg/fig/received-level-detectability.png", dpi=300, bbox_inches="tight"); fig.savefig("leg/fig/received-level-detectability.pdf", bbox_inches="tight")
