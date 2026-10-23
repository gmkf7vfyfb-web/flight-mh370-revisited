import pandas as pd, numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
apply_figure_style(sizes=(8,7,6))
df = pd.read_csv("hydro/sct/synthetic-composer-test.csv")
order = ["H08S","H01W","H08S+H08N","H01W+H08S","H01W+H08S+H08N"]
names = {"H08S":"Diego Garcia S alone","H01W":"Cape Leeuwin alone","H08S+H08N":"Diego Garcia S + N",
         "H01W+H08S":"Cape Leeuwin + Diego Garcia S","H01W+H08S+H08N":"all three"}
col_t, col_b = "#3b6ea8", "#d08a2e"
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw=dict(width_ratios=[1.25, 1], wspace=0.55))
base = df[df.config=="base"]
for j,(bear,c,lab,off) in enumerate([(False,col_t,"arrival time only",-0.13),(True,col_b,"time + bearing (3.3° sd)",0.13)]):
    d = base[base.bearing==bear].set_index("stations").loc[order]
    y = np.arange(len(order))+off
    a.hlines(y, d.info_bits_q10, d.info_bits_q90, color=c, lw=1.2)
    a.plot(d.info_bits_median, y, "o", color=c, ms=4.5, label=lab)
for v in (0.25, 1.0): a.axvline(v, color=META_GREY, lw=0.7, ls="--", zorder=0)
a.text(0.25, len(order)-0.35, "negligible\n< 0.25", ha="right", va="top", fontsize=6, color=META_GREY)
a.text(1.0, len(order)-0.35, " material\n ≥ 1 bit", ha="left", va="top", fontsize=6, color=META_GREY)
a.set_yticks(range(len(order))); a.set_yticklabels([names[o] for o in order])
a.set_xlabel("information gain on impact PDF (bits)"); a.set_xlim(-0.1, 6.0); a.set_ylim(-0.6, len(order)-0.1)
a.legend(loc="lower right", frameon=False, fontsize=7)
a.set_title("Only a cross-ocean pair moves the PDF", loc="left")
panel_letter(a, "a")
st = df[(df.bearing==False) & ((df.config=="base") | df.config.str.startswith("sigma_t_s"))]
for s, c in [("H01W","#7a7a7a"),("H08S+H08N","#b5b5b5"),("H01W+H08S",col_t)]:
    d = st[st.stations==s].sort_values("sigma_t_s")
    b.plot(d.sigma_t_s, d.info_bits_median, "o-", color=c, ms=4, lw=1.3)
    b.text(d.sigma_t_s.iloc[-1]+15, d.info_bits_median.iloc[-1], names[s].replace("Cape Leeuwin + Diego Garcia S","Leeuwin + DG S"), va="center", fontsize=7, color=c)
b.axhline(1.0, color=META_GREY, lw=0.7, ls="--", zorder=0); b.axhline(0.25, color=META_GREY, lw=0.7, ls="--", zorder=0)
b.set_xlabel("impact-time uncertainty σ_t (s)"); b.set_ylabel("information gain (bits)")
b.set_xlim(-30, 900); b.set_xticks([0,60,180,600]); b.margins(y=0.08)
b.set_title("Arrival time alone needs impact time, a pair does not", loc="left")
panel_letter(b, "b")
fig.savefig("hydro/sct/synthetic-composer-test.png", dpi=300, bbox_inches="tight")
fig.savefig("hydro/sct/synthetic-composer-test.pdf", bbox_inches="tight")
r = fig.canvas.get_renderer()
texts=[(t,t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
ov=[(x.get_text()[:20],y.get_text()[:20]) for i,(x,bx) in enumerate(texts) for y,by in texts[i+1:] if bx.overlaps(by)]
print(ov)
