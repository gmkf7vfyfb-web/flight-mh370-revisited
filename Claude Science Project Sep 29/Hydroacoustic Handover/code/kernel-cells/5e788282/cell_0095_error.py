import matplotlib as mpl
_orig_save = save
def save(fig, name):
    r = fig.canvas.get_renderer()
    texts=[(t,t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
    tl={ax:set(ax.get_xticklabels(which='both')+ax.get_yticklabels(which='both')) for ax in fig.axes}
    ov=[(a.get_text()[:30],b.get_text()[:30]) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb)]
    fb=fig.bbox; out=[t.get_text()[:30] for t,bt in texts if bt.x1>fb.x1+1 or bt.x0<fb.x0-1 or bt.y1>fb.y1+1]
    print(name, "overlaps:", ov[:6], "outside:", out[:4])
    _orig_save(fig, name)
src=open(MOD+"/prepare/metz_f35a/charts.py").read().replace("def save(fig, name):","def _save_unused(fig, name):")
exec(src)