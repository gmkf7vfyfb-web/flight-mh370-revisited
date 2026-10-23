a1.set_title('Impact near the crossing: about a 40 % chance the debris was missed',loc='left')
fig.savefig('fig2-surface-search-locality.png',dpi=200); fig.savefig('fig2-surface-search-locality.pdf')
r=fig.canvas.get_renderer(); bb1=a1.title.get_window_extent(r); bl=[t for t in fig.findobj(mpl.text.Text) if t.get_text()=='b'][0].get_window_extent(r); print(bb1.overlaps(bl))