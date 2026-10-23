mkdir -p figs; cat > energy_chart.py <<'EOF'
# expects in namespace: Eq, Wt, E, res50, top5p, top5s, foc, foc_E, ANCH, ANOTE, RXN, DETN, apply_figure_style, panel_letter
import matplotlib as mpl, matplotlib.pyplot as plt, numpy as np
apply_figure_style(sizes=(8,7,6))
EF35, EF35_SD = 9e8, 2e8; RF35 = EF35*ANCH
OPTN = {"D0":"00:19 data held out","D2":"00:19 time only","D3":"both 00:19 frequencies as recorded","D4":"both 00:19 frequencies, shared start-up offset"}
E5, E95 = Eq["D0"][0.05], Eq["D0"][0.95]
Ex = np.logspace(np.log10(E5), np.log10(E95), 50)
CP, CS, CF = "#2b6cb0", "#d17a22", "#6b2c91"   # pairs, singles, focal pair
fig = plt.figure(figsize=(7.2, 7.9))
gs = fig.add_gridspec(3, 2, height_ratios=[0.9, 4.2, 0.01], width_ratios=[1, 1], hspace=0.12, wspace=0.28, left=0.09, right=0.985, top=0.95, bottom=0.30)
axE = [fig.add_subplot(gs[0, j]) for j in range(2)]
axa = fig.add_subplot(gs[1, 0], sharex=axE[0]); axb = fig.add_subplot(gs[1, 1], sharex=axE[1])
xl = (1e8, 3e10)
for ax in axE:
    for k, o in enumerate(["D0", "D2", "D3", "D4"]):
        y = 3 - k; q = Eq[o]
        ax.plot([q[0.05], q[0.95]], [y, y], color="0.35", lw=1.2, solid_capstyle="butt")
        ax.plot([q[0.25], q[0.75]], [y, y], color="0.35", lw=3.5, solid_capstyle="butt")
        ax.plot(q[0.5], y, "o", ms=4.5, mfc="white", mec="0.2", mew=1)
    ax.set_yticks([3, 2, 1, 0]); ax.set_yticklabels([OPTN[o] for o in ["D0", "D2", "D3", "D4"]] if ax is axE[0] else [])
    ax.set_ylim(-0.7, 3.7); ax.set_xscale("log"); ax.set_xlim(*xl); ax.tick_params(labelbottom=False)
    ax.errorbar([EF35], [-0.45], xerr=[[EF35_SD], [EF35_SD]], fmt="D", ms=4, color="k", capsize=2, lw=0.8)
axE[0].set_title("Simulated impact energy (median, 25-75 % and 5-95 %) for each way of using the 00:19 data", loc="left", x=0, fontsize=8)
axE[0].text(EF35*1.35, -0.45, "aircraft crash used as reference", va="center", fontsize=6)
# ---- panel a: coupling vs energy
ax = axa; ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(1e-7, 30)
ax.axhspan(1e-6, 1e-2, color="0.92", zorder=0); ax.text(1.15e8, 1.4e-6, "assumed range of coupling (prior)", fontsize=6, color="0.3")
ax.axhspan(1, 30, color="#f3dede", zorder=0); ax.text(1.15e8, 2.0, "impossible: more sound than impact energy", fontsize=6, color="#7a2f2f")
for R_ in 10.0**np.arange(2, 12):
    ax.plot(xl, [R_/xl[0], R_/xl[1]], color="0.75", lw=0.5, ls=":", zorder=1)
    xe = 2.4e10; ye = R_/xe
    if 1.5e-7 < ye < 20: ax.text(xe, ye*1.12, f"$10^{{{int(np.log10(R_))}}}$ J", fontsize=5.5, color="0.5", ha="right", va="bottom", rotation=-33)
e50_new, e50_old = res50[("D0", 0.01)][0], 6e-4
ax.plot([E5, E95], [e50_new]*2, color="k", lw=1.2, ls="--"); ax.text(E95*1.08, e50_new, "half detected\n(this table)", fontsize=5.5, va="center")
ax.plot([E5, E95], [e50_old]*2, color="0.5", lw=0.9, ls="--"); ax.text(E95*1.08, e50_old, "half detected\n(earlier table)", fontsize=5.5, va="center", color="0.4")
ax.errorbar([EF35], [ANCH], xerr=[[EF35_SD], [EF35_SD]], fmt="D", ms=4.5, color="k", capsize=2, lw=0.8, zorder=5)
ax.annotate("", xy=(EF35, ANCH/4), xytext=(EF35, ANCH), arrowprops=dict(arrowstyle="-|>", color="k", lw=0.8))
ax.text(EF35*0.85, ANCH*1.6, "aircraft crash\n(upper bound;\nprovisional)", fontsize=5.5, ha="right")
def band(ax, R_, col, lw, lab, yfac):
    ax.plot(Ex, yfac(R_, Ex), color=col, lw=lw, solid_capstyle="round", zorder=4)
    ax.text(Ex[-1]*1.06, yfac(R_, Ex[-1]), lab, color=col, fontsize=6, va="center", zorder=6)
fa = lambda R_, x: R_/x
for i, r in enumerate(top5p.itertuples()): band(ax, r.eta_pd50_all_a005*r.E_ref, CP, 1.3, f"P{i+1}", fa)
for i, r in enumerate(top5s.itertuples()): band(ax, r.eta_needed*1.13e9, CS, 1.3, f"S{i+1}", fa)
band(ax, foc.eta_pd50_all_a005*foc_E, CF, 2.2, "★", fa)
ax.set_xlabel("Impact kinetic energy (J)"); ax.set_ylabel("Coupling efficiency (share of impact energy that becomes sound)")
ax.set_title("Coupling each candidate would need", loc="left")
# ---- panel b: multiple of the reference crash's radiated sound energy
ax = axb; ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(1e-4, 3e5)
fb = lambda R_, x: np.full_like(np.atleast_1d(x), R_/RF35, dtype=float) if np.ndim(x) else R_/RF35
xx = np.logspace(8, np.log10(3e10), 60)
ax.fill_between(xx, 1e-6*xx/RF35, 1e-2*xx/RF35, color="0.92", zorder=0)
ax.fill_between(xx, xx/RF35, 3e5, color="#f3dede", zorder=0)
ax.plot(xx, e50_new*xx/RF35, color="k", ls="--", lw=1.2); ax.plot(xx, e50_old*xx/RF35, color="0.5", ls="--", lw=0.9)
ax.errorbar([EF35], [1.0], xerr=[[EF35_SD], [EF35_SD]], fmt="D", ms=4.5, color="k", capsize=2, lw=0.8, zorder=5)
ax.axhline(1, color="k", lw=0.5, zorder=1)
for i, r in enumerate(top5p.itertuples()): band(ax, r.eta_pd50_all_a005*r.E_ref, CP, 1.3, f"P{i+1}", fb)
for i, r in enumerate(top5s.itertuples()): band(ax, r.eta_needed*1.13e9, CS, 1.3, f"S{i+1}", fb)
Rfoc = foc.eta_pd50_all_a005*foc_E
band(ax, Rfoc, CF, 2.2, "★", fb)
ax.annotate(f"about {Rfoc/RF35:.0f}× the reference crash's sound\n(coupling {foc.eta_pd50_all_a005/ANCH:.0f}× its coupling)", xy=(1.2e9, Rfoc/RF35), xytext=(1.3e8, 2.5e4),
            fontsize=6, color=CF, arrowprops=dict(arrowstyle="-", color=CF, lw=0.6))
ax.set_xlabel("Impact kinetic energy (J)"); ax.set_ylabel("Sound energy needed ÷ sound energy of the reference crash")
ax.set_title("The same, as a multiple of the reference crash", loc="left")
for a_, L in zip([axE[0], axa], "ab"): panel_letter(a_, L)
from matplotlib.lines import Line2D
h = [Line2D([], [], color=CP, lw=1.3, label="P1-P5: highest-ranked two-recorder candidates"), Line2D([], [], color=CS, lw=1.3, label="S1-S5: highest-ranked one-recorder candidates"),
     Line2D([], [], color=CF, lw=2.2, label="★ strongest pair by p-value (Cape Leeuwin 00:52:04 × Diego Garcia South 01:12:49)"),
     Line2D([], [], color="k", ls="--", lw=1.2, label="coupling at which half of simulated impacts are detected"),
     Line2D([], [], color="0.75", ls=":", lw=0.8, label="equal sound energy (coupling × impact energy)")]
fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.09, 0.205), ncol=2, frameon=False, fontsize=6)
F1 = ("(i) Each line is one candidate signal. It shows the share of the impact energy that must become sound to make that signal, "
      "for impact energies from the 5 % to the 95 % value of the simulation. Above 1 is not possible. "
      "The reference crash (a fighter aircraft that hit the sea in 2022) changed only a small share of its energy into sound; that value is provisional. "
      "The ★ pair needs about 330 times the coupling of the reference crash, at the simulated impact energy of about 1.1 GJ; "
      "because that energy is about 1.2 times the crash energy (0.9 GJ), the sound energy needed is about 390 times the crash's sound energy. "
      "Its sound direction does not agree with the directions Kadri published. These are estimates, not detections.")
F2 = (f"(ii) Source posterior: run J geometry sample (8.85 M rows), 00:19 Held Out (D0'), p = 0.5; energy = contact KE (energy_transferred_j = 1/2 m v^2). Bands: eta(E) = R/E with R = "
      f"eta_needed x E_ref (pairs: eta for P_D(both) = 0.5, alpha 0.05, at the lag's arc locus with run J median E within +/-1 deg; singles: level match at the reference impact 37.1 S, 1.13 GJ, tau90 3.3 s). "
      f"F-35A: E = 900 +/- 200 MJ, eta = 2.1e-4 ({ANOTE}); an upper bound (shallow sound channel). "
      f"Half-detected line: P_D(any of 6 receivers) = 0.5 at alpha 0.01 with the +/-10 dB calibration draw, recomputed with the block 11 machinery on the corrected IMOS RAM-grid table: eta50 = {e50_new:.1e} "
      f"(alpha 0.05: {res50[('D0',0.05)][0]:.1e}); earlier table 6e-4 (injection-recovery note). Star pair: H01W 00:52:04 M1b p 0.043 (digitised Kadri Fig. 9c; text time 00:52:03, caption time 00:54:30) x "
      f"H08S 01:12:49 M1b p 0.039 (raw panel e; p_B 0.30, airgun-dominated), lag 1,245 s in [809, 1536]; locus 33.6 S 94.5 E, impact 00:31:41; locus bearing 268.9 deg from H01W, "
      f"144.8 deg from H08S; Kadri gives 57 or 306.18 deg (text p. 9 vs Table 1 caption), neither within 37 deg; nearest Table 1 bearing 00:52:50 at 274.84 deg (46 s later). "
      f"tau dependence of the required level ignored along each band. EXPLORATORY; PREDICTIVE, NOT CALIBRATED; caveats C1 (+10.4/+7.4 dB per octave slope misfit at H01W/H08S), C2.")
import textwrap
fig.text(0.02, 0.135, textwrap.fill(F1, 175), fontsize=6, va="top")
fig.text(0.02, 0.07, textwrap.fill(F2, 205), fontsize=5, va="top", color="0.25")
fig.suptitle("The candidate signals need far more of the impact energy to become sound than the reference crash did", x=0.02, ha="left", y=0.985, fontsize=8)
for f in ("png", "pdf"): fig.savefig(f"figs/impact_energy_and_coupling.{f}", dpi=300)
EOF
echo ok