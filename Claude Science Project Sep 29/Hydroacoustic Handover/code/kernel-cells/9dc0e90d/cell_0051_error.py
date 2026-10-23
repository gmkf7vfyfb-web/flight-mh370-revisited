import re, matplotlib as mpl, matplotlib.pyplot as plt, matplotlib.dates as mdates
import cartopy.crs as ccrs, cartopy.feature as cfeature
from shapely.geometry import shape
apply_figure_style(sizes=(8,7,6))
base = pd.Timestamp('2014-03-07')
recs=[]
for ft in feats:
    n=int(re.match(r'D(\d+)', ft['properties']['Name']).group(1)); recs.append((base+pd.Timedelta(days=n), shape(ft['geometry'])))
dates=[r[0] for r in recs]; dmin,dmax=min(dates),max(dates)
cmap=mpl.colormaps['viridis']; norm=mpl.colors.Normalize(mdates.date2num(dmin), mdates.date2num(dmax))
fig=plt.figure(figsize=(7.2,7.4)); ax=fig.add_axes([0.07,0.27,0.80,0.68], projection=ccrs.PlateCarree())
ax.set_extent([76,116,-49,-17], crs=ccrs.PlateCarree())
try:
    ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor='0.88', zorder=1); ax.coastlines('50m', lw=0.5, zorder=2); coast='ok'
except Exception as e: coast=str(e)
for d,g in sorted(recs, key=lambda r:r[0]):
    geoms = g.geoms if g.geom_type=='MultiPolygon' else [g]
    for gg in geoms:
        x,y=gg.exterior.xy; ax.fill(x,y,facecolor=cmap(norm(mdates.date2num(d))),alpha=0.18,edgecolor=cmap(norm(mdates.date2num(d))),lw=0.4,transform=ccrs.PlateCarree(),zorder=3)
ax.plot(arc7.lon,arc7.lat,color='k',lw=1.4,transform=ccrs.PlateCarree(),zorder=5)
ax.text(84.6,-40.6,'7th arc (00:19 UTC, sea level)',fontsize=7,rotation=-52,transform=ccrs.PlateCarree(),zorder=6)
sat=[(-43.976,90.960,'16 Mar'),(-44.051,91.224,None),(-44.95,90.217,'18 Mar'),(-44.68,90.52,'23 Mar'),(-46.50,89.50,'24 Mar'),(-44.283,90.933,'26 Mar')]
for la,lo,l in sat: ax.plot(lo,la,marker='*',ms=9,mfc='#d62728',mec='k',mew=0.4,ls='none',transform=ccrs.PlateCarree(),zorder=7)
ax.annotate('Satellite sightings\n16-26 Mar (5 sensors)',xy=(90.5,-44.6),xytext=(95.5,-47.3),fontsize=7,arrowprops=dict(arrowstyle='-',lw=0.6),transform=ccrs.PlateCarree(),zorder=8)
ax.plot(90.95,-34.85,marker='*',ms=10,mfc='#ff7f0e',mec='k',mew=0.4,transform=ccrs.PlateCarree(),zorder=7)
ax.annotate('Pléiades objects, 23 Mar',xy=(90.95,-34.85),xytext=(78.0,-31.5),fontsize=7,arrowprops=dict(arrowstyle='-',lw=0.6),transform=ccrs.PlateCarree(),zorder=8)
rn=[(-28.3927,97.7750),(-29.19333,95.1250),(-28.3176,97.8234),(-28.8867,96.0844),(-29.1936,95.1094)]
for la,lo in rn: ax.plot(lo,la,marker='D',ms=4.5,mfc='#9467bd',mec='k',mew=0.4,transform=ccrs.PlateCarree(),zorder=7)
ax.annotate('Aircraft photographs, 29 Mar\n(not official)',xy=(96.0,-28.9),xytext=(80.0,-24.5),fontsize=7,arrowprops=dict(arrowstyle='-',lw=0.6),transform=ccrs.PlateCarree(),zorder=8)
ax.plot(101.461,-25.975,marker='^',ms=6,mfc='w',mec='k',transform=ccrs.PlateCarree(),zorder=7)
ax.plot(104.1,-21.1,marker='^',ms=6,mfc='w',mec='k',transform=ccrs.PlateCarree(),zorder=7)
ax.annotate('Pinger contacts, Apr\n(all discounted)',xy=(104.1,-21.1),xytext=(106.5,-18.3),fontsize=7,arrowprops=dict(arrowstyle='-',lw=0.6),transform=ccrs.PlateCarree(),zorder=8)
ax.annotate('',xy=(101.461,-25.975),xytext=(107.0,-19.2),arrowprops=dict(arrowstyle='-',lw=0.6),transform=ccrs.PlateCarree())
ax.plot(115.86,-31.95,'ko',ms=3,transform=ccrs.PlateCarree(),zorder=7); ax.text(113.9,-31.4,'Perth',fontsize=7,transform=ccrs.PlateCarree(),ha='right')
gl=ax.gridlines(draw_labels=True,lw=0.3,color='0.6',xlocs=range(75,121,5),ylocs=range(-50,-14,5)); gl.top_labels=gl.right_labels=False
gl.xlabel_style=gl.ylabel_style={'size':6}
cax=fig.add_axes([0.89,0.35,0.018,0.52]); cb=mpl.colorbar.ColorbarBase(cax,cmap=cmap,norm=norm)
cb.ax.yaxis.set_major_locator(mdates.DayLocator(bymonthday=[18,25,1,8,15,22,28])); cb.ax.yaxis.set_major_formatter(mdates.DateFormatter('%d %b')); cb.ax.tick_params(labelsize=6)
cb.set_label('Search day (2014)',fontsize=7)
fig.text(0.07,0.965,'The 2014 aircraft and ship surface search moved from 44–46° S to 20–33° S on 28 March',fontsize=8,ha='left')
foot=("Note (plain): Each coloured box is one daily search area of the 2014 aircraft and ship search, 18 Mar to 28 Apr (387 boxes). Later days are yellower. "
"The black line is the 7th arc at sea level. Stars are possible objects seen by satellites; none was found again by aircraft or ships. Diamonds are objects photographed by a "
"New Zealand aircraft on 29 Mar (independent source only). Triangles are pinger contacts that were later discounted. A box shows where aircraft looked, not how well they could see.\n"
"Note (technical): Polygons: GA/AMSA ArcGIS service Search_And_Rescue_Search_Area2014 (© AMSA; day n = 7 Mar + n). Boxes carry no POD, sweep width or tracks; AMSA's daily POD was "
"not published. 7th arc: ring of constant satellite range from BTO 18,400 µs at 00:19:29 (corrected value), Inmarsat ephemeris, Perth GES, h = 0 km, WGS84. Sightings: DIGO sheets "
"(16 Mar 04:16Z), SASTIND (18 Mar), MRSA table centroid (23 Mar), GISTDA THEOS (24 Mar, positions provisional), Japan CSICE (26 Mar). Pléiades: GA Record 2017/13 rating-5 "
"centre. Photos: Iannello 2017 (grade C). Pinger contacts: ATSB 2017 pp. 38-39; ATSB Jun 2014 Fig. 12 (approx.).")
fig.text(0.07,0.015,foot,fontsize=6,ha='left',va='bottom',wrap=True)
fig.savefig("surface-search-2014-map.png",dpi=200); print(coast)