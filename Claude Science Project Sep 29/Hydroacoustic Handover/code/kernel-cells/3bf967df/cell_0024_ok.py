for c_ in (cb,cb2): c_.ax.set_position(c_.ax.get_position().translated(0,-0.035))
fig.savefig('kadri-crossing-impact-map.png',dpi=200,bbox_inches='tight')
r=fig.canvas.get_renderer()
texts=[(tt,tt.get_window_extent(r)) for tt in fig.findobj(mpl.text.Text) if tt.get_text().strip() and tt.get_visible()]
print([(a.get_text()[:25],b.get_text()[:25]) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb)][:6])