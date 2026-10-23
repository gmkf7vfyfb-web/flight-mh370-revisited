for t in list(ax.texts):
    s=t.get_text()
    if s.startswith("acoustic contacts"): t.set_position((pd.Timestamp("2014-03-08 06:00"),1.0))
    if s.startswith("white objects"): t.set_position((pd.Timestamp("2014-03-08 06:00"),0.5))
    if s=="30-day beacon minimum": t.set_text("30-day minimum"); t.set_position((pd.Timestamp("2014-04-07")-pd.Timedelta(hours=8),7.55)); t.set_ha("right")
    if s=="40-day maximum": t.set_text("40-day maximum (beacon battery)")
yl=[x.get_text() for x in ax.get_yticklabels()]
ax.set_yticklabels([s.replace("Maxar 0.3-2 m","Maxar 0.4-0.8 m") for s in yl])
ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=[8,15,22,29]))
for t in fig.texts:
    if t.get_text().startswith("Plain:"): t.set_position((0.01,0.09))
fig.savefig("out/fig-locality-imagery-timeline.png",dpi=300)
r=fig.canvas.get_renderer()
texts_=[(t,t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
ticks=set(ax.get_xticklabels()+ax.get_yticklabels())
print([(a.get_text()[:25],b.get_text()[:25]) for i,(a,ba) in enumerate(texts_) for b,bb in texts_[i+1:] if ba.overlaps(bb) and not (a in ticks and b in ticks)])