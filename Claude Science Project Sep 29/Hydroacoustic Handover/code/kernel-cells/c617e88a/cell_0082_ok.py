for t in ax.texts:
    if t.get_text().startswith("within noise"): t.set_position((0.27,len(opts)-0.55))
fig.subplots_adjust(top=0.92); fig.savefig("work/fig_result_rhyd.png",dpi=200)
r=fig.canvas.get_renderer()
T=[(t,t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
print([(a.get_text()[:30],b.get_text()[:30]) for i,(a,ba) in enumerate(T) for b,bb in T[i+1:] if ba.overlaps(bb)])