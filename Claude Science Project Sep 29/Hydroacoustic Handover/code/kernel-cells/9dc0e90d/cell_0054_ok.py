for tx in list(ax.texts):
    if tx.get_text().startswith('7th arc'): tx.remove()
for an in list(ax.texts):
    if an.get_text().startswith('Pinger') or an.get_text()=='' : an.remove()
ax.set_position([0.07,0.20,0.80,0.74]); cax.set_position([0.89,0.30,0.018,0.56])
# arc label rotation from display slope
lat_a=np.interp([78,82],arc7.lon,arc7.lat) if np.all(np.diff(arc7.lon)>0) else None
la_s=arc7.sort_values('lon'); y1,y2=np.interp([78.5,82.5],la_s.lon,la_s.lat)
p1=ax.transData.transform(ccrs.PlateCarree().transform_point(78.5,y1,ccrs.PlateCarree())); p2=ax.transData.transform((82.5,y2))
ang=np.degrees(np.arctan2(p2[1]-p1[1],p2[0]-p1[0]))
ax.text(78.6,y1+0.45,'7th arc (00:19 UTC, sea level)',fontsize=7,rotation=ang,rotation_mode='anchor',transform=ccrs.PlateCarree(),zorder=6)
ax.annotate('Pinger contacts, Apr 2014 (all discounted)',xy=(104.1,-21.1),xytext=(99.0,-18.0),fontsize=7,ha='center',arrowprops=dict(arrowstyle='-',lw=0.6),transform=ccrs.PlateCarree(),zorder=8)
ax.annotate('',xy=(101.461,-25.975),xytext=(99.0,-18.6),arrowprops=dict(arrowstyle='-',lw=0.6),transform=ccrs.PlateCarree(),zorder=8)
fig.texts[0].set_text('The 2014 surface search began at 37–46° S and moved north to 20–33° S on 28 March')
fig.savefig("surface-search-2014-map.png",dpi=200)
r=fig.canvas.get_renderer(); texts=[(tx,tx.get_window_extent(r)) for tx in fig.findobj(mpl.text.Text) if tx.get_text().strip() and tx.get_visible()]
print([tx.get_text()[:25] for tx,b in texts if b.y0<fig.bbox.y0 or b.y1>fig.bbox.y1 or b.x1>fig.bbox.x1])