
src=open("energy_chart.py").read()
rep=[('ax.text(E5/1.08, e50_new, "half detected\\n(this table)", fontsize=5.5, va="center", ha="right")','ax.text(2.2e9, e50_new*1.3, "half of simulated impacts detected (this table)", fontsize=5.5, va="bottom", ha="center")'),
('ax.text(E5/1.08, e50_old*0.85, "half detected\\n(earlier table)", fontsize=5.5, va="top", ha="right", color="0.4")','ax.text(2.2e9, e50_old*1.3, "half detected (earlier table)", fontsize=5.5, va="bottom", ha="center", color="0.4")'),
(', bbox=dict(fc="white", ec="none", pad=0.3) if ye<1e-2 else dict(fc="0.92", ec="none", pad=0.3))',')'),
('place(ax, 0.10)','place(ax, 0.19)'),('place(ax, 0.14)','place(ax, 0.23)'),
('xy=(1.2e9, Rfoc/RF35), xytext=(1.3e8, 2.5e4)','xy=(5e8, Rfoc/RF35), xytext=(1.15e8, 1.1e2)'),
('ax.text(EF35*1.3, ANCH*0.5, "reference crash\\n(upper bound;\\nprovisional)", fontsize=5.5, ha="left", va="center")','ax.text(EF35*1.3, ANCH*0.45, "reference crash\\n(upper bound; provisional)", fontsize=5.5, ha="left", va="center")'),
]
for a,b in rep:
    assert a in src, a[:70]; src=src.replace(a,b)
open("energy_chart.py","w").write(src); plt.close("all"); exec(src)
