fig.set_size_inches(7.2,6.5)
ax.set_position([0.07,0.215,0.80,0.735]); cax.set_position([0.89,0.33,0.018,0.52])
for an in list(ax.texts):
    if an.get_text().startswith('Pinger') or an.get_text()=='': an.remove()
ax.annotate('Pinger contacts, Apr 2014 (all discounted)',xy=(104.1,-21.1),xytext=(96.5,-18.0),fontsize=7,ha='center',arrowprops=dict(arrowstyle='-',lw=0.6),transform=ccrs.PlateCarree(),zorder=8)
ax.annotate('',xy=(101.461,-25.975),xytext=(96.5,-18.6),arrowprops=dict(arrowstyle='-',lw=0.6),transform=ccrs.PlateCarree(),zorder=8)
fig.texts[0].set_position((0.07,0.975))
fig.savefig("surface-search-2014-map.png",dpi=200)
r=fig.canvas.get_renderer(); texts=[(tx,tx.get_window_extent(r)) for tx in fig.findobj(mpl.text.Text) if tx.get_text().strip() and tx.get_visible()]
foot_b=[b for tx,b in texts if tx.get_text().startswith('Note (plain)')][0]; axb=ax.get_window_extent(r)
print("outside:",[tx.get_text()[:25] for tx,b in texts if b.y0<fig.bbox.y0 or b.y1>fig.bbox.y1 or b.x1>fig.bbox.x1], "footnote top vs map bottom px:", foot_b.y1, axb.y0)