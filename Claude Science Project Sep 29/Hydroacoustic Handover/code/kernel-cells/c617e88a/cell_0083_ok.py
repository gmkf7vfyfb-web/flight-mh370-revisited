ax.xaxis.labelpad=6; fig.subplots_adjust(bottom=0.38); fig.savefig("work/fig_result_rhyd.png",dpi=200)
r=fig.canvas.get_renderer()
T=[(t,t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
print([(a.get_text()[:30],b.get_text()[:30]) for i,(a,ba) in enumerate(T) for b,bb in T[i+1:] if ba.overlaps(bb)])
# windows and power for the other two options
for o,nm in (("held-out","00:19 Held Out"),("r600-bto-raw-bfo","00:19 R600 BTO + Raw BFO")):
    q=json.load(open(f"work/power/{o}/power_check.json")); windows_fig(q,o,nm); power_fig(q,o,nm); PW[o]=q
plt.close("all")