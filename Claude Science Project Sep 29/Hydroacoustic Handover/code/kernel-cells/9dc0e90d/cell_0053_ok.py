shp.natural_earth('50m','physical','coastline')
fig.savefig("surface-search-2014-map.png",dpi=200)
r=fig.canvas.get_renderer()
texts=[(tx,tx.get_window_extent(r)) for tx in fig.findobj(mpl.text.Text) if tx.get_text().strip() and tx.get_visible()]
fb=fig.bbox; out=[tx.get_text()[:30] for tx,b in texts if b.x0<fb.x0-1 or b.x1>fb.x1+1 or b.y0<fb.y0-1 or b.y1>fb.y1+1]
print("outside:",out)