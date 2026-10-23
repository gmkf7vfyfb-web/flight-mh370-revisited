import textwrap
for t in fig.findobj(mpl.text.Text):
    s=t.get_text()
    if s.startswith("archived high-resolution"): t.set_position((93.0,-26.4)); t.set_ha("left")
    if s.startswith("7th arc"): t.set_position((95.2,-32.6)); t.set_rotation(55)
    if s.startswith("306.18"): t.set_position((99.9,-27.15)); 
    if s.startswith("objects reported"): t.set_position((101.75,-26.75))
    if s.startswith("Plain:"): t.set_text("\n".join(textwrap.wrap(foot1,175))); t.set_position((0.01,0.075)); t.set_wrap(False)
    if s.startswith("Technical:"): t.set_text("\n".join(textwrap.wrap(foot2,190))); t.set_position((0.01,0.005)); t.set_wrap(False)
fig.subplots_adjust(bottom=0.27)
fig.savefig("out/fig-locality-sources-map.png",dpi=300)
r=fig.canvas.get_renderer()
texts_=[(t,t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
ticks=set(sum([a.get_xticklabels()+a.get_yticklabels() for a in fig.axes],[]))
ov=[(a.get_text()[:25],b.get_text()[:25]) for i,(a,ba) in enumerate(texts_) for b,bb in texts_[i+1:] if ba.overlaps(bb) and not (a in ticks and b in ticks)]
print(ov)