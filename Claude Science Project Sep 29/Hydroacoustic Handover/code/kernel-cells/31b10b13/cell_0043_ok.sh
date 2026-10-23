cat > table_figs.py <<'EOF'
import textwrap, matplotlib.pyplot as plt, numpy as np, pandas as pd
apply_figure_style(sizes=(8,7,6))
def fmt_eta(e):
    if not np.isfinite(e): return "none (P_D never 0.5)" if e==np.inf else "n/a"
    return f"{e:.2g} ({e/ANCH:,.0f}×)"
def nm(rx): return RXN.get(rx, rx)
def bear_short(s):
    if not isinstance(s,str) or not s: return "no H01W"
    if "no Kadri" in s: return "no bearing within 30 s"
    if "CONSISTENT (<=" in s and "INCONSISTENT" not in s: v="consistent"
    else: v="inconsistent"
    import re
    m=re.search(r"predicted ([\d.]+) deg",s); d=re.findall(r"\|d\|=([\d.]+)",s)
    return f"{v}: predicted {float(m.group(1)):.0f}°, nearest |Δ| {min(map(float,d)):.0f}°" if m and d else v
def render(rows, cols, widths, title, F1, F2, fn, highlight=None):
    fig = plt.figure(figsize=(11.7, 8.3)); ax = fig.add_axes([0.02, 0.2, 0.96, 0.72]); ax.axis("off")
    cell = [[textwrap.fill(str(r[c]), w) for c, w in zip(cols, widths)] for r in rows]
    tb = ax.table(cellText=cell, colLabels=[textwrap.fill(c, w) for c, w in zip(cols, widths)], colWidths=[w/sum(widths) for w in widths], loc="upper left", cellLoc="left")
    tb.auto_set_font_size(False); tb.set_fontsize(5.6)
    nlines = [max(1+str(x).count("\n") for x in rr) for rr in [[textwrap.fill(c,w) for c,w in zip(cols,widths)]]+cell]
    H = 0.98/ (sum(nlines)+2)
    for (i, j), c in tb.get_celld().items():
        c.set_height(H*nlines[i]+0.004); c.set_edgecolor("0.8"); c.set_linewidth(0.4)
        if i == 0: c.set_facecolor("0.9"); c.get_text().set_fontweight("bold")
        elif highlight is not None and (i-1) in highlight: c.set_facecolor("#efe6f5")
    fig.text(0.02, 0.965, title, fontsize=8, ha="left", va="top")
    fig.text(0.02, 0.165, textwrap.fill(F1, 230), fontsize=6, va="top")
    fig.text(0.02, 0.095, textwrap.fill(F2, 270), fontsize=5, va="top", color="0.25")
    for f in ("png","pdf"): fig.savefig(f"figs/{fn}.{f}", dpi=300)
    return fig
EOF
echo ok