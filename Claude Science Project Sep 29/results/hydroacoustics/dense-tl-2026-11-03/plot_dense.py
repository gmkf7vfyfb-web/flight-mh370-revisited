import numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
apply_figure_style(sizes=(8, 7, 6))
TITLE_B = globals().get("TITLE_B", "Sound loss along the arc for four stations")
df = pd.read_csv("dense/tl_dense_bands.csv"); m = pd.read_csv("dense/runs/paths.csv")
NAMES = [("H01W", "Cape Leeuwin, IMS array"), ("IMOS3315", "Perth Canyon logger (3315)"), ("IMOS3376", "Perth Canyon logger (3376)"),
         ("IMOS3274", "Portland logger (3274)"), ("IMOS3275", "Portland logger (3275)"), ("IMOS3250", "Scott Reef logger (3250)"),
         ("H08S", "Diego Garcia South, IMS array"), ("SWAMS1", "OHASISBIO south-west (SWAMS1)"), ("SWAMS2", "OHASISBIO south-west (SWAMS2)"),
         ("SWAMS3", "OHASISBIO south-west (SWAMS3)"), ("SSEIR", "OHASISBIO south-east ridge (SSEIR)"), ("MAD", "OHASISBIO Madagascar (MAD)"),
         ("NCRO", "OHASISBIO Crozet north (NCRO)"), ("WKER", "OHASISBIO Kerguelen west (WKER)")]
lats = np.sort(m.src_lat.unique())                       # -41 ... -20
d10 = df[df.src_depth_m == 10.0]
nb = d10.groupby("path").fc_hz.nunique(); full = nb[nb == nb.max()].index
med = d10[d10.path.isin(full)].groupby("path").tl_db.median()
Z = np.full((len(NAMES), len(lats)), np.nan); LAND = np.zeros_like(Z, bool)
for i, (k, _) in enumerate(NAMES):
    for j, la in enumerate(lats):
        nm = f"arc{abs(la):04.1f}S-{k}"; row = m[m.name == nm].iloc[0]
        if row.land: LAND[i, j] = True
        elif nm in med.index: Z[i, j] = med[nm]
fig, (a, b) = plt.subplots(2, 1, figsize=(7.2, 7.6), gridspec_kw=dict(height_ratios=[1.35, 1], hspace=0.42))
cm = mpl.colormaps["viridis_r"].copy(); cm.set_over("#3b0f3b")
ext = [-lats[0] + 0.25, -lats[-1] - 0.25, len(NAMES) - 0.5, -0.5]
im = a.imshow(Z, aspect="auto", cmap=cm, vmin=125, vmax=170, extent=ext, interpolation="nearest")
LM = np.ma.masked_where(~LAND, np.ones_like(Z))
a.imshow(LM, aspect="auto", cmap=mpl.colors.ListedColormap(["#d9d9d9"]), extent=ext, interpolation="nearest")
a.set_yticks(range(len(NAMES))); a.set_yticklabels([n for _, n in NAMES])
a.set_xlabel("Point on the 7th arc, degrees south")
a.set_title("Sound loss from each point on the arc to each listening station", loc="left")
cb = fig.colorbar(im, ax=a, extend="max", pad=0.02); cb.set_label("Sound loss, dB (lower is louder at the station)")
a.text(1.0, -0.13, "grey = path crosses land", transform=a.transAxes, ha="right", va="top", fontsize=6, color="#555555")
panel_letter(a, "a")
cols = {"H01W": "#1f5fa8", "H08S": "#c46a00", "IMOS3315": "#3a8a3a", "SSEIR": "#8a3a8a"}
lab = []
for k, c in cols.items():
    i = [x for x, _ in NAMES].index(k); y = Z[i]
    b.plot(-lats, y, "-o", ms=2.5, lw=1.2, color=c)
    ok = np.where(np.isfinite(y))[0]
    if len(ok): lab.append([y[ok[-1]], -lats[ok[-1]], dict(NAMES)[k].split(",")[0].replace(" logger", ""), c])
lab.sort(key=lambda t: t[0]); 
for n in range(1, len(lab)): lab[n][0] = max(lab[n][0], lab[n-1][0] + 3.2)
for yv, xv, tx, c in lab: b.text(xv - 0.3, yv, tx, color=c, fontsize=7, va="center", ha="left")
# data-driven title: which stations have the lowest loss south of 35 S and north of 30 S
def best(sel):
    mm = {k: np.nanmedian(Z[[x for x, _ in NAMES].index(k)][sel]) for k in cols}
    return min(mm, key=mm.get), mm
bs, ms_ = best(lats <= -35); bn, mn_ = best(lats >= -30)
print("south best", bs, {k: round(v,1) for k,v in ms_.items()}); print("north best", bn, {k: round(v,1) for k,v in mn_.items()})
for xa, txt in ((32.0, "source over Broken Ridge flank\n(seabed 1.0 km deep)"), (22.0, "source over a seamount\n(seabed 2.5 km deep)")):
    yy = np.nanmin(Z[:, list(-lats).index(xa)][[ [x for x, _ in NAMES].index(k) for k in cols ]])
    b.annotate(txt, (xa, yy), xytext=((40.9, yy + 1.0) if xa > 30 else (xa - 0.6, yy - 2.0)), fontsize=6, color="#555555", ha="left", va="center",
               arrowprops=dict(arrowstyle="-", lw=0.6, color="#777777"))
b.set_xlim(41.5, 17.0); b.set_xlabel("Point on the 7th arc, degrees south"); b.set_ylabel("Sound loss, dB")
b.set_title(TITLE_B, loc="left"); b.invert_yaxis(); b.margins(y=0.06)
b.text(0.005, 0.02, "up = louder at the station", transform=b.transAxes, fontsize=6, va="bottom", color="#555555")
panel_letter(b, "b")
foot = ("Sound loss is the median over ten one-third-octave bands, 5 to 40 Hz (seven frequencies in each band), for a source 10 m below the sea surface. "
        "The model is a parabolic-equation sound model (RAM) run on the 3 November 2026 path sections: GEBCO 2026 seabed depth, World Ocean Atlas 2023 March sound speed, "
        "GlobSed v3 sediment over a layered seabed. Arc points every 0.5 degrees from 41 to 20 S, on the 7th-arc line of the run J searched-area grid. "
        "The model is not yet corrected for its known bias: on deep Indian Ocean paths with known sources it lost 5 to 14 dB too much, so true losses are probably lower. "
        "Losses above 170 dB are shown in the darkest colour. Paths that cross land are not computed. "
        "Two arc points lie over raised seabed (32.0 S, 22.0 S); there a shallow source couples into the deep sound channel, giving 10 to 16 dB less loss than the points beside them. This effect is local and the 0.5-degree spacing does not resolve it.")
import textwrap
fig.text(0.01, 0.005, "\n".join(textwrap.wrap(foot, 205)), fontsize=6, ha="left", va="bottom", color="#333333")
fig.subplots_adjust(left=0.30, right=0.97, top=0.96, bottom=0.14)
fig.savefig("dense/dense-sound-model-results.png", dpi=300)
print("cells filled", np.isfinite(Z).sum(), "land", LAND.sum())
