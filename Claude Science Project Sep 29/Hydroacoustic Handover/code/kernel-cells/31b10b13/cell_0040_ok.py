
src=open("energy_chart.py").read()
rep=[
('OPTN = {"D0":"00:19 data held out","D2":"00:19 time only","D3":"both 00:19 frequencies as recorded","D4":"both 00:19 frequencies, shared start-up offset"}',
 'OPTN = {"D0":"00:19 data held out","D2":"00:19 time only","D3":"00:19 frequencies as recorded","D4":"00:19 frequencies, shared offset"}'),
("left=0.09, right=0.985, top=0.95, bottom=0.30","left=0.17, right=0.95, top=0.925, bottom=0.27"),
('axE[0].set_title("Simulated impact energy (median, 25-75 % and 5-95 %) for each way of using the 00:19 data", loc="left", x=0, fontsize=8)',
 'axE[0].set_title("Simulated impact energy for each way of using the 00:19 data (dot median; bars 25-75 % and 5-95 %)", loc="left", fontsize=7)'),
('''    xe = 2.4e10; ye = R_/xe
    if 1.5e-7 < ye < 20: ax.text(xe, ye*1.12, f"$10^{{{int(np.log10(R_))}}}$ J", fontsize=5.5, color="0.5", ha="right", va="bottom", rotation=-33)''',
 '''    xe = 1.25e8; ye = R_/xe
    if 2e-7 < ye < 0.5 and not (6e-7 < ye < 3e-6): ax.text(xe, ye, f"$10^{{{int(np.log10(R_))}}}$ J", fontsize=5.5, color="0.55", ha="left", va="center", bbox=dict(fc="white", ec="none", pad=0.3) if ye<1e-2 else dict(fc="0.92", ec="none", pad=0.3))'''),
('ax.text(E95*1.08, e50_new, "half detected\\n(this table)", fontsize=5.5, va="center")','ax.text(E5/1.08, e50_new, "half detected\\n(this table)", fontsize=5.5, va="center", ha="right")'),
('ax.text(E95*1.08, e50_old, "half detected\\n(earlier table)", fontsize=5.5, va="center", color="0.4")','ax.text(E5/1.08, e50_old*0.85, "half detected\\n(earlier table)", fontsize=5.5, va="top", ha="right", color="0.4")'),
('ax.text(EF35*0.85, ANCH*1.6, "aircraft crash\\n(upper bound;\\nprovisional)", fontsize=5.5, ha="right")','ax.text(EF35*1.3, ANCH*0.5, "reference crash\\n(upper bound;\\nprovisional)", fontsize=5.5, ha="left", va="center")'),
('axE[0].text(EF35*1.35, -0.45, "aircraft crash used as reference", va="center", fontsize=6)','axE[0].text(EF35*1.35, -0.45, "reference crash", va="center", fontsize=6)'),
('ax.set_title("Coupling each candidate would need", loc="left")','ax.set_title("Coupling each candidate signal would need", loc="left")'),
('for a_, L in zip([axE[0], axa], "ab"): panel_letter(a_, L)','for a_, L in zip([axE[0], axa, axb], "abc"): panel_letter(a_, L)'),
('fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.09, 0.205), ncol=2, frameon=False, fontsize=6)','fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.10, 0.175), ncol=2, frameon=False, fontsize=6)'),
('fig.text(0.02, 0.135,','fig.text(0.02, 0.165,'),('fig.text(0.02, 0.07,','fig.text(0.02, 0.095,'),
('y=0.985, fontsize=8)','y=0.99, fontsize=8)'),
]
for a,b in rep:
    assert a in src, a[:60]; src=src.replace(a,b)
# label de-overlap: collect labels then place
src=src.replace('''def band(ax, R_, col, lw, lab, yfac):
    ax.plot(Ex, yfac(R_, Ex), color=col, lw=lw, solid_capstyle="round", zorder=4)
    ax.text(Ex[-1]*1.06, yfac(R_, Ex[-1]), lab, color=col, fontsize=6, va="center", zorder=6)''',
'''LBL = {}
def band(ax, R_, col, lw, lab, yfac):
    ax.plot(Ex, yfac(R_, Ex), color=col, lw=lw, solid_capstyle="round", zorder=4)
    LBL.setdefault(ax, []).append([float(np.log10(yfac(R_, Ex[-1]))), lab, col])
def place(ax, sep=0.11):
    L = sorted(LBL[ax], key=lambda v: v[0]); ys = [v[0] for v in L]
    for i in range(1, len(ys)): ys[i] = max(ys[i], ys[i-1] + sep)
    for (y0, lab, col), y in zip(L, ys):
        ax.text(Ex[-1]*1.12, 10**y, lab, color=col, fontsize=6, va="center", zorder=6)
        ax.plot([Ex[-1]*1.01, Ex[-1]*1.11], [10**y0, 10**y], color=col, lw=0.4)''')
src=src.replace('ax.set_xlabel("Impact kinetic energy (J)"); ax.set_ylabel("Coupling efficiency','place(ax, 0.10); ax.set_xlabel("Impact kinetic energy (J)"); ax.set_ylabel("Coupling efficiency')
src=src.replace('ax.set_xlabel("Impact kinetic energy (J)"); ax.set_ylabel("Sound energy needed','place(ax, 0.14); ax.set_xlabel("Impact kinetic energy (J)"); ax.set_ylabel("Sound energy needed')
src=src.replace('textwrap.fill(F1, 175)','textwrap.fill(F1, 190)').replace('textwrap.fill(F2, 205)','textwrap.fill(F2, 225)')
open("energy_chart.py","w").write(src)
plt.close("all"); exec(src)
r=fig.canvas.get_renderer()
texts=[(t,t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
tick=set(); [tick.update(a.get_xticklabels()+a.get_yticklabels()) for a in fig.axes]
ov=[(a.get_text()[:25],b.get_text()[:25]) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb) and not (a in tick and b in tick)]
print(ov); fb=fig.bbox; print([t.get_text()[:30] for t,b in texts if b.x0<fb.x0-1 or b.x1>fb.x1+1 or b.y0<fb.y0-1 or b.y1>fb.y1+1])
