"""Shared helpers for the updated example charts (graphics track 'updated-examples', 22 Oct 2026).
Chart rule (Pete, 10 Oct 2026): no project jargon in titles, axes or legends; standard statistical terms as such;
two footnotes: (i) plain ASD-STE100, (ii) technical. fig.savefig only. PNG + PDF."""
import json, pathlib, sys, textwrap
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WS = pathlib.Path("/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/c0b15646-883a-4dcf-811b-7a832a957069")
HP = WS / "repo/Claude Science Project Sep 29/Hydroacoustic Handover/code/module/prepare"
RD = HP.parent / "results-data"
RES = WS / "repo/Claude Science Project Sep 29/results"
XH = pathlib.Path("/Users/pete/Downloads/mh370-exchange/hydroacoustics")
SR = XH / "run-j-searches"
LEV = XH / "run-j-levels"
LEV2 = XH / "run-j-imos-ram-grid/levels-rerun-v2"
GD = WS / "gfx/data"
OUT = WS / "gfx/out"
OUT.mkdir(parents=True, exist_ok=True)
if str(HP) not in sys.path: sys.path.insert(0, str(HP))
T0 = 1394236800.0
ETA_F35A = 2.26e-3
ETA_BROWN = 2.1e-4

STN = {"H01W": "Cape Leeuwin (H01W)", "H08S": "Diego Garcia South (H08S)", "H08N": "Diego Garcia North (H08N)",
       "3315": "Perth Canyon logger 3315", "3376": "Perth Canyon logger 3376", "3274": "Portland logger 3274",
       "3275": "Portland logger 3275", "3250": "Scott Reef logger 3250"}
OPT = {"D0": "00:19 data not used", "D2": "00:19 range and first frequency", "D3": "both 00:19 frequencies as recorded",
       "D4": "both 00:19 frequencies, shared start-up offset"}
OPT_CODE = {"D0": "D0′ (held out)", "D2": "D2 (R600 BTO + BFO)", "D3": "D3 (both BFOs raw)", "D4": "D4 (both BFOs + shared start-up offset)"}
OPT_COL = {"D0": "#1f4e9c", "D2": "#c7761a", "D3": "#2a8a6a", "D4": "#8a3d9c"}
ETA_COL = {1e-2: "#3f007d", 2.26e-3: "#6a51a3", 1e-3: "#6a51a3", 2.1e-4: "#9e9ac8", 1e-5: "#cbc9e2"}

CAV = ("PREDICTIVE, NOT CALIBRATED. C1: propagation slope misfit +10.4 / +7.4 dB per octave at H01W / H08S (after the EW0112 source "
       "result a source-term caveat; air9 verdict NOT EXPLAINED, gap G23). C2: coupling efficiency eta is not calibrated and is treated as a prior "
       "range over at least four decades (bounds not yet ruled); 2.26e-3 is this project's own inversion of the F-35A arrivals at H11 digitised from Metz, Obana & Fukao (2023; the paper gives no energy, "
       "source level or coupling) with the 900 +/- 200 MJ energy from the Brown et al. (2026) arXiv preprint, the module TL (KRAKEN + RAM, not calibrated), source depth 10 m and an f^-2 "
       "spectrum (single-factor spread 3.4e-4 to 5.4e-2); one point inside the prior range, NOT adopted and not from an authoritative source. 2.1e-4 is the Arons-equivalent coupling in the "
       "Brown et al. (2026) preprint, a different definition. "
       "No detection is claimed.")
PROV_J = ("Source posterior: end-of-flight run J (74 seeds, 313.6 M rows, four strata pooled by p_core/K) + northern supplement "
          "(impacts-ruleB.npz); weighted subsample 2 M draws per 00:19 option at dive probability p = 0.5 (run_j_levels.py, prereg 4277320).")
IMOS_CORR = ("IMOS transmission loss: corrected RAM-along-the-arc table imos_tl_ram_arc.csv (imos_ram_grid.py, run_j_levels amendment 2; "
             "replaces imos_tl_ramcorr_arc.csv); IMS (H01W/H08S/H08N) loss unchanged.")


def style():
    apply_figure_style(sizes=(8, 7, 6))  # noqa: F821  (figure-style skill, loaded in the kernel)
    plt.rcParams.update({"axes.titlesize": 8, "figure.dpi": 150, "savefig.dpi": 200, "pdf.fonttype": 42, "axes.titlelocation": "left"})


def footnotes(fig, plain, tech, y0=0.006, width=None, fs=(6.4, 5.9)):
    """(i) plain ASD-STE100 note above (ii) technical note, bottom-left; returns the top of the block (figure fraction)."""
    fw, fh = fig.get_size_inches(); width = width or int(fw * 19.5)
    t2 = textwrap.fill("Technical note: " + tech, width); n2 = t2.count("\n") + 1
    t1 = textwrap.fill("Plain note: " + plain, int(width * fs[1] / fs[0])); n1 = t1.count("\n") + 1
    lh2 = fs[1] / 72 * 1.32 / fh; lh1 = fs[0] / 72 * 1.32 / fh
    fig.text(0.01, y0, t2, fontsize=fs[1], va="bottom", ha="left", color="#333333")
    fig.text(0.01, y0 + lh2 * n2 + 0.5 * lh1, t1, fontsize=fs[0], va="bottom", ha="left", color="#222222")
    return y0 + lh2 * n2 + lh1 * (n1 + 0.5)


def need_bottom(fig, plain, tech, width=None, fs=(6.4, 5.9)):
    fw, fh = fig.get_size_inches(); width = width or int(fw * 19.5)
    n2 = textwrap.fill("Technical note: " + tech, width).count("\n") + 1
    n1 = textwrap.fill("Plain note: " + plain, int(width * fs[1] / fs[0])).count("\n") + 1
    return 0.006 + (fs[1] * n2 + fs[0] * (n1 + 0.5)) / 72 * 1.32 / fh


def overlaps(fig):
    """figure-style 9.1: overlapping visible text boxes (excluding tick labels on their own axis)."""
    fig.canvas.draw(); r = fig.canvas.get_renderer()
    texts = [(t, t.get_window_extent(r)) for t in fig.findobj(matplotlib.text.Text) if t.get_text().strip() and t.get_visible()]
    bad = []
    for i, (a, ba) in enumerate(texts):
        for b, bb in texts[i + 1:]:
            if ba.overlaps(bb): bad.append((a.get_text()[:40], b.get_text()[:40]))
    fb = fig.bbox; out = [t.get_text()[:40] for t, bt in texts if bt.x0 < fb.x0 - 1 or bt.x1 > fb.x1 + 1 or bt.y0 < fb.y0 - 1 or bt.y1 > fb.y1 + 1]
    return bad, out


def save(fig, name, check=True):
    rep = overlaps(fig) if check else ([], [])
    fig.savefig(OUT / f"{name}.png"); fig.savefig(OUT / f"{name}.pdf"); plt.close(fig)
    return rep


def hms(t, ms=False):
    s = t - T0; s %= 86400; h = int(s // 3600); m = int((s % 3600) // 60); sec = s - 3600 * h - 60 * m
    return f"{h:02d}:{m:02d}:{sec:06.3f}" if ms else f"{h:02d}:{m:02d}:{int(round(sec)) if round(sec) < 60 else 59:02d}"


def unix(s):
    h, m, sec = s.split(":"); return T0 + 3600 * int(h) + 60 * int(m) + float(sec)


def tfmt(x, _=None):
    s = int(round(x - T0)) % 86400
    return f"{s // 3600:02d}:{(s % 3600) // 60:02d}"


def pct(x, d=1):
    if x == 0: return "0 %"
    if x < 10 ** (-d) / 100: return f"< {10 ** (-d):g} %"
    return f"{100 * x:.{d}f} %"
