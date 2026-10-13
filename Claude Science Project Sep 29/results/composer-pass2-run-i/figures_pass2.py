"""Composer pass 2 (run I): five deliverable figures. Run inside the python kernel after report_pass2.py and seabed_report.py
(needs df, ev, sb, maps, smaps, lat_core, lat_oc and the figure-style helpers apply_figure_style / figure_style__panel_letter)."""
import textwrap
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

apply_figure_style(sizes=(8, 7, 6))
GRID = RP.GRID; LATC, LONC = RP.LATC, RP.LONC
DCOL = {"D0": "#4d4d4d", "D1": "#1f5fa8", "D2": "#6aa84f", "D3": "#c2571a", "D4": "#8e44ad", "D5": "#d4a017"}
DLAB = {"D0": "00:19 data not used", "D1": "00:19 timing only (R600 BTO)", "D2": "+ R600 frequency as recorded",
        "D3": "+ both frequencies as recorded", "D4": "+ both frequencies, Holland transient bias added",
        "D5": "+ R600 BFO + R1200 BFO, Holland transient bias added"}
LCOL = {"P1": "#9e9e9e", "Dr": "#1f5fa8", "DrS": "#0b2e59", "H": "#c2571a", "HS": "#7a2e05"}
LLAB = {"P1": "flight and end of flight only", "Dr": "+ debris drift", "DrS": "+ debris drift + seabed searches",
        "H": "+ Pléiades objects (if they are debris)", "HS": "+ Pléiades objects + seabed searches"}
TECH = ("Core run I: 4 core families x 8 seeds x 100,000 hand-off rows, equal family prior; NOT CONVERGED (split-half waypoints 0.916, floor "
        "0.924; free flight 0.830, descent-climb 0.794, Davey reproduction 0.891). End of flight run I (binary mh370-eof-ri1, 102.4 M impacts): piloted "
        "turns and interim pitch-down provisional; no structural limit (G13). 00:19: competing log-on causes q = 1/3, W = 00:10:58-01:15:56, C2 silent, "
        "survival factor applied; no treatment uses the R1200 BTO. Ocean: GLORYS12 and GlobCurrent (product-relative windage), equal prior, mixed per "
        "row (Bayesian model averaging). Drift h50; unscored rows carried at the mean ratio (<= 0.11 % of weight); Western Australia non-recovery not "
        "modelled (G26). Hydroacoustics predictive only, not in these products. Searches: ATSB Phase 2 + Bluefin-21, rho 0.05, point target; Ocean "
        "Infinity excluded. Pléiades: rho 0.25, rating 5, six clusters plus four COSMO-SkyMed contacts, conditional on the objects being debris. "
        "Strata mixed by core share x 00:19 evidence (ruling C), conditional on equal family prior. Composer pass 2, architecture stand-in.")


def foot(fig, ste, tech, y=0.0, w=170):
    t = "(i) " + ste + "\n(ii) Technical: " + tech
    fig.text(0.01, y, "\n".join(textwrap.fill(p, w) for p in t.split("\n")), fontsize=5.6, va="bottom", ha="left", color="#333333")


def dens(h):
    d = h / (h.sum() * RP.GSTEP); k = np.exp(-0.5 * (np.arange(-4, 5) * RP.GSTEP / 0.1) ** 2); k /= k.sum()
    return np.convolve(d, k, mode="same")


def hpd(s, lv):
    o = np.sort(s.ravel())[::-1]; c = np.cumsum(o); return [o[np.searchsorted(c, l * c[-1])] for l in lv]


def H(D, L, oc="M", fam="all", mix="mixC"):
    r = df[(df["product"] == f"{D}|T|{L}|{oc if L != 'P1' else '-'}|") & (df.mix == mix) & (df.family == fam)].iloc[0]
    return r


# ---------- Figure 1: latitude ----------
DLEG = {"D0": "00:19 not used", "D1": "timing only", "D2": "+ R600 BFO", "D3": "+ both BFOs", "D4": "+ both BFOs, Holland transient bias added", "D5": "+ R1200 BFO, Holland transient bias added"}
fig, axs = plt.subplots(2, 2, figsize=(7.2, 6.4)); fig.subplots_adjust(left=0.08, right=0.99, top=0.93, bottom=0.27, wspace=0.18, hspace=0.42)
for ax, L, title in ((axs[0, 0], "Dr", "With drift: 00:19 data shift the median < 0.5°"),
                     (axs[0, 1], "DrS", "After the searches, probability moves north")):
    for D in DCOL:
        h = maps[f"{D}|T|{L}|M|#mixC#lat"]; r = H(D, L)
        ax.plot(GRID, dens(h), color=DCOL[D], lw=1.5 if D in ("D0", "D1") else 1.0, ls="-" if r.ess >= 1000 else ":",
                label=DLEG[D] + ("" if r.ess >= 1000 else " (not estimable)"))
    ax.set_title(title, loc="left"); ax.set_xlim(-41, -25); ax.set_xlabel("Impact latitude (degrees)")
axs[0, 0].set_ylabel("Probability density (per degree)"); axs[0, 0].legend(frameon=False, fontsize=6, loc="center right", bbox_to_anchor=(1.0, 0.5), handlelength=1.4); axs[0, 0].set_xlim(-41, -20)
ax = axs[1, 0]
for L in LCOL:
    h = maps[f"D1|T|{L}|{'M' if L != 'P1' else '-'}|#mixC#lat"]
    ax.plot(GRID, dens(h), color=LCOL[L], lw=1.4, label=LLAB[L])
ax.set_title("00:19 timing only: evidence added in turn", loc="left"); ax.set_xlim(-41, -25)
ax.set_xlabel("Impact latitude (degrees)"); ax.set_ylabel("Probability density (per degree)"); ax.legend(frameon=False, fontsize=6, loc="upper right")
ax = axs[1, 1]
SC = {"next-i-waypoints": ("route waypoints", "#1f5fa8"), "next-i-free": ("free flight", "#c2571a"), "next-i-repro-radar": ("Davey reproduction", "#6aa84f"),
      "next-i-descent-climb": ("descent then climb", "#8e44ad"), "mixC": ("mixture, equal family prior", "#000000")}
for st, (lab, c) in SC.items():
    h, med, a90, ess = lat_core[st]
    ax.plot(GRID, dens(h), color=c, lw=1.6 if st in ("mixC", "next-i-free") else 0.9, ls="--" if st == "mixC" else "-", label=f"{lab} (median {med:.2f}°)")
ax.set_title("Free flight lies 0.3° north of the mixture", loc="left"); ax.set_xlim(-41, -25)
ax.set_xlabel("Impact latitude (degrees)"); ax.legend(frameon=False, fontsize=6, loc="upper right")
for a, l in zip(axs.ravel(), "abcd"):
    figure_style__panel_letter(a, l)
fig.suptitle("Where the aircraft hit the ocean, by latitude (core run I, not converged)", x=0.01, ha="left", fontsize=8, y=0.985)
foot(fig, "The curves show how probable each impact latitude is. The data at 00:19 change the curves only a little. The seabed searches found nothing, so "
     "they move probability away from the searched area, to the north. The waypoint family has almost all of the weight because the four families "
     "have equal prior weight; the free-flight curve is shown beside it. The result is not converged. Dotted curves have too few effective samples.",
     TECH + " Curves: 0.05° latitude bins, Gaussian 0.1°. (a, b) all six 00:19 treatments; (c) 00:19 R600 BTO Only; (d) R600 BTO Only + drift, per core "
     "family (waypoints 0.9982 of the equal-prior mixture).")
fig.savefig("note/fig1-impact-latitude.png", dpi=300); fig.savefig("note/fig1-impact-latitude.pdf"); plt.close(fig)

# ---------- Figure 2: maps ----------
fig, axs = plt.subplots(2, 3, figsize=(7.2, 6.6), sharex=True, sharey=True); fig.subplots_adjust(left=0.08, right=0.99, top=0.885, bottom=0.28, wspace=0.05, hspace=0.25)
panels = [("D1|T|P1|-|#mixC", "Flight and end of flight only", "P1"), ("D1|T|Dr|M|#mixC", "+ debris drift", "Dr"), ("D1|T|DrS|M|#mixC", "+ debris drift + seabed searches", "DrS"),
          ("D1|T|Dr|M|#next-i-free", "Free flight only, + debris drift", "Dr"), ("D1|T|H|M|#mixC", "+ Pléiades objects, if debris", "H"), ("D1|T|HS|M|#mixC", "+ Pléiades objects + seabed searches", "HS")]
for ax, (k, t, L) in zip(axs.ravel(), panels):
    s = maps[k].astype(float); lv = hpd(s, (0.9, 0.5))
    ax.contourf(LONC, LATC, s, levels=[lv[0], lv[1], s.max() * 1.01], colors=["#d0d7e2", LCOL[L]], alpha=0.95)
    mix = k.split("#")[1]; P = k.split("#")[0]; r = df[(df["product"] == P) & (df.mix == mix) & (df.family == "all")].iloc[0]
    ax.plot(r.mean_lon, r.mean_lat, marker="+", color="k", ms=6)
    ax.text(0.03, 0.03, f"50 %: {r.A50_km2 / 1e3:.0f}k km²\n90 %: {r.A90_km2 / 1e3:.0f}k km²\nmedian {r.lat_median:.2f}°", transform=ax.transAxes, fontsize=6, va="bottom",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1))
    ax.set_title(t, loc="left"); ax.set_xlim(84, 101); ax.set_ylim(-41, -27)
for a in axs[:, 0]:
    a.set_ylabel("Latitude (degrees)")
for a in axs[1]:
    a.set_xlabel("Longitude (degrees east)")
for a, l in zip(axs.ravel(), "abcdef"):
    figure_style__panel_letter(a, l)
fig.suptitle("Most probable impact regions with the 00:19 timing value (core run I, not converged)", x=0.01, ha="left", fontsize=8, y=0.985)
fig.text(0.01, 0.95, "Dark: 50 % region. Light: 90 % region. Cross: mean position.", fontsize=7)
foot(fig, "The maps show where the impact is most probable. The debris drift and the searches make the region larger, because the searches removed the "
     "middle of it. If the Pléiades objects are debris, the region is much smaller and to the north-east. Panel d uses only the free-flight family. "
     "The result is not converged: the two halves of the seeds give areas that differ by 13 to 41 %.",
     TECH + " 00:19 R600 BTO Only, competing causes q = 1/3. Regions: 0.1° cells, Gaussian 0.1°, highest density, spherical areas. Panels a-c, e-f: "
     "equal-prior core mixture (ruling C); d: free-flight family alone.")
fig.savefig("note/fig2-impact-regions.png", dpi=300); fig.savefig("note/fig2-impact-regions.pdf"); plt.close(fig)

# ---------- Figure 3: ocean models ----------
fig, axs = plt.subplots(1, 2, figsize=(7.2, 4.6), gridspec_kw={"width_ratios": [1.15, 1]}); fig.subplots_adjust(left=0.09, right=0.99, top=0.88, bottom=0.47, wspace=0.28)
ax = axs[0]; e = ev[ev.C == "T"].reset_index(drop=True)
for j, L in enumerate(["Dr", "DrS", "H", "HS"]):
    ax.plot(np.arange(6) + (j - 1.5) * 0.15, e[f"P_GLORYS12_{L}"], "o", color=LCOL[L], ms=4, label=LLAB[L])
ax.axhline(0.5, color="#999999", lw=0.7, ls="--"); ax.set_xticks(range(6)); ax.set_xticklabels(["not used", "timing", "+R600 BFO", "+both BFOs", "+both, bias", "+R1200, bias"], rotation=30, ha="right")
ax.set_ylim(0.3, 0.95); ax.set_ylabel("Posterior probability, GLORYS12"); ax.set_xlabel("00:19 data used")
ax.set_title("The debris data do not select an ocean model", loc="left"); ax.legend(frameon=False, fontsize=6, loc="upper left", ncol=1)
ax = axs[1]
for oc, lab, c, ls in (("G", "GLORYS12 alone", "#1f5fa8", "-"), ("C", "GlobCurrent alone", "#c2571a", "-"), ("M", "equal-prior mixture", "#000000", "--")):
    ax.plot(GRID, dens(lat_oc[oc]), color=c, ls=ls, lw=1.3, label=lab)
ax.set_xlim(-41, -27); ax.set_xlabel("Impact latitude (degrees)"); ax.set_ylabel("Probability density (per degree)")
ax.set_title("00:19 timing only, + debris drift", loc="left"); ax.legend(frameon=False, fontsize=6, loc="upper right")
for a, l in zip(axs, "ab"):
    figure_style__panel_letter(a, l)
fig.suptitle("Two ocean models for the debris drift, weighted by the evidence (core run I, not converged)", x=0.01, ha="left", fontsize=8, y=0.985)
foot(fig, "Two ocean models give the drift of the debris. Each model starts with a probability of one half. The debris finds change this "
     "probability only a little, so the result uses both models together. With the 00:19 timing value and the drift, the two medians are 0.2° apart.",
     TECH + " P(GLORYS12) = Z_G / (Z_G + Z_C) on the core mixture; the GlobCurrent run is partly in-sample for drifter skill, so no up-weighting. "
     "Treatments with both BFOs have low effective sample size after drift (see the coverage table).", w=165)
fig.savefig("note/fig3-ocean-models.png", dpi=300); fig.savefig("note/fig3-ocean-models.pdf"); plt.close(fig)

# ---------- Figure 4: coverage (ESS) ----------
fig, axs = plt.subplots(1, 2, figsize=(7.2, 5.6), sharey=True); fig.subplots_adjust(left=0.33, right=0.97, top=0.90, bottom=0.30, wspace=0.06)
rowsD = [(D, C) for D in ["D0", "D1", "D2", "D3", "D4", "D5"] for C in ["T", "C1", "C2s", "T1"]]
CL = {"T": "both causes, q = 1/3", "C1": "fuel exhaustion", "C2s": "other cause, silent", "T1": "both causes, q = 1"}
DSHORT = {"D0": "00:19 not used", "D1": "00:19 timing only", "D2": "+ R600 BFO as recorded", "D3": "+ both BFOs as recorded", "D4": "+ both BFOs, Holland transient bias added", "D5": "+ R1200 BFO, Holland transient bias added"}
cmap = mpl.colormaps["viridis"]; norm = mpl.colors.LogNorm(10, 1e6)
for ax, fam, t in ((axs[0], "all", "All end-of-flight families"), (axs[1], "A1", "Uncontrolled descent after fuel exhaustion")):
    M = np.array([[df[(df["product"] == f"{D}|{C}|{L}|{'-' if L == 'P1' else 'M'}|") & (df.mix == "mixC") & (df.family == fam)].ess.iloc[0] for L in LCOL] for D, C in rowsD])
    ax.imshow(np.clip(M, 10, 1e6), cmap=cmap, norm=norm, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]; txt = f"{v / 1e3:.0f}k" if v >= 1e4 else (f"{v / 1e3:.1f}k" if v >= 1e3 else f"{v:.0f}")
            ax.text(j, i, txt, ha="center", va="center", fontsize=5.5, color="white" if v < 3e4 else "black", fontweight="bold" if v < 1000 else "normal")
            if v < 1000:
                ax.add_patch(mpl.patches.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, ec="#d62728", lw=0.9))
    ax.set_xticks(range(5)); ax.set_xticklabels(["flight + end\nof flight", "+ drift", "+ drift\n+ searches", "+ Pléiades", "+ Pléiades\n+ searches"], fontsize=6)
    ax.set_title(t, loc="left")
axs[0].set_yticks(range(len(rowsD))); axs[0].set_yticklabels([f"{DSHORT[D]} | {CL[C]}" for D, C in rowsD], fontsize=5.5)
cb = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=axs, fraction=0.03, pad=0.01); cb.set_label("Effective impacts (Kish), log scale; red box: below 1,000")
for a, l in zip(axs, "ab"):
    figure_style__panel_letter(a, l)
fig.suptitle("Effective sample size of each combination of 00:19 data, log-on cause and evidence", x=0.01, ha="left", fontsize=8, y=0.985)
foot(fig, "Each number is the effective number of impacts that carry the result. Below 1,000 (red box), the result is not reliable. When we add the "
     "R1200 frequency, the drift and the Pléiades objects, few impacts remain. The fuel-exhaustion family without control (right) is the weakest.",
     TECH + " Rows: 00:19 data treatment D0-D5 x log-on cause (q = 1/3 primary; C1, C2 silent, q = 1 sensitivities). Holland's Hypothesis 1 = D4 x C1, "
     "Hypothesis 2 = D3 x C2 silent. ESS on the equal-prior core mixture (ruling C), pooled over 8 seeds, ocean models mixed.", w=165)
fig.savefig("note/fig4-coverage-ess.png", dpi=300); fig.savefig("note/fig4-coverage-ess.pdf"); plt.close(fig)

# ---------- Figure 5: seabed ----------
fig, axs = plt.subplots(2, 3, figsize=(7.2, 6.6), sharex=True, sharey=True); fig.subplots_adjust(left=0.08, right=0.99, top=0.88, bottom=0.27, wspace=0.05, hspace=0.18)
for r_, D in enumerate(["D0", "D1"]):
    for c_, L in enumerate(["P1", "DrS", "HS"]):
        ax = axs[r_, c_]; s = smaps[f"{D}|{L}"].astype(float); lv = hpd(s, (0.9, 0.5))
        ax.contourf(LONC, LATC, s, levels=[lv[0], lv[1], s.max() * 1.01], colors=["#d0d7e2", LCOL[L]], alpha=0.95)
        im = maps[f"{D}|T|{L}|{'-' if L == 'P1' else 'M'}|#mixC"].astype(float); ax.contour(LONC, LATC, im, levels=hpd(im, (0.9,)), colors="k", linewidths=0.5, linestyles="--")
        x = sb[(sb.D == D) & (sb.layer == L) & (sb.subset == "all") & (sb.cell == "total")].iloc[0]
        ess_row = H(D, L).ess
        ax.text(0.03, 0.03, f"50 %: {x['seabed|all|A50'] / 1e3:.0f}k km²\n90 %: {x['seabed|all|A90'] / 1e3:.0f}k km²", transform=ax.transAxes, fontsize=6, va="bottom",
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1))
        if r_ == 0:
            ax.set_title({"P1": "Flight and end of flight", "DrS": "+ drift + searches", "HS": "+ Pléiades + searches"}[L], loc="left")
        ax.set_xlim(84, 101); ax.set_ylim(-41, -27)
for a in axs[:, 0]:
    a.set_ylabel("Latitude (degrees)")
for a in axs[1]:
    a.set_xlabel("Longitude (degrees east)")
for a, l in zip(axs.ravel(), "abcdef"):
    figure_style__panel_letter(a, l)
for r_, t in enumerate(["Row 1: 00:19 data not used", "Row 2: 00:19 timing only (R600 BTO)"]):
    axs[r_, 0].text(0.03, 0.96, t.split(": ", 1)[1], transform=axs[r_, 0].transAxes, fontsize=7, fontweight="bold", va="top")
fig.suptitle("Where the wreckage is on the seabed (core run I, not converged)", x=0.01, ha="left", fontsize=8, y=0.985)
fig.text(0.01, 0.955, "Dark: 50 % region of the wreckage. Light: 90 % region. Dashed line: 90 % region of the impact point.", fontsize=7)
foot(fig, "The wreckage moves very little as it sinks, so the seabed regions are almost the same as the impact regions. The right column is correct "
     "only if the Pléiades objects are debris. Breakup in the air is not modelled for the debris field. Do not use these maps for a search.",
     TECH + " Seabed: settling run I samples (settling 9330d4c; 40,000 outcomes per stratum and treatment, from the flight + end-of-flight weights), "
     "re-weighted per outcome by the composed module factors (importance weights; outcome ESS 1,300-1,900 in the right column); settled mass "
     "only, afloat 18 %; breakup rows settled from the intact impact point (G-bf). Strata by settling's core share x Z(cell).", w=165)
fig.savefig("note/fig5-seabed.png", dpi=300); fig.savefig("note/fig5-seabed.pdf"); plt.close(fig)
print("figures written")
