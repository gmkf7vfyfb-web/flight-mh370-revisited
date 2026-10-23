import matplotlib.dates as mdates
d0,d1=pd.Timestamp("2014-03-08"),pd.Timestamp("2014-04-30 23:59")
tt={k:pd.to_datetime(v).tz_localize(None) for k,v in mod.items()}
fig,ax=plt.subplots(figsize=(7.2,3.6))
rows=[("Terra 250 m pass (MODIS)",tt["MODIS Terra 250m (MOD02QKM 6.1)"],"0.35"),
      ("Aqua 250 m pass (MODIS)",tt["MODIS Aqua 250m (MYD02QKM 6.1)"],"0.35"),
      ("Suomi NPP 375 m pass (VIIRS)",tt["VIIRS VNP02IMG"],"0.35")]
labels=[]
for i,(lab,t_,c) in enumerate(rows):
    y=7-i; ax.plot(t_,[y]*len(t_),"|",color=c,ms=7,mew=0.8); labels.append((y,lab))
# zero rows
zero=[(4,"Landsat 7/8 scenes: none listed"),(3,"Maxar 0.3-2 m scenes (CSDA): none listed"),(2,"Sentinel-1A radar: none public before 15 Jun")]
for y,lab in zero:
    ax.plot([d0,d1],[y,y],color="0.8",lw=0.6,ls=":"); labels.append((y,lab))
ax.plot(pd.Timestamp("2014-04-03 21:02"),2,marker="^",color="k",ms=5); ax.text(pd.Timestamp("2014-04-04 12:00"),2.18,"launch 3 Apr",fontsize=6)
# events row
ev=[("2014-04-04 08:00","contact 1"),("2014-04-05 07:47","contact 2"),("2014-04-05 03:05","objects seen")]
ax.plot(pd.to_datetime(["2014-04-04 08:00","2014-04-05 07:47"]),[1,1],"*",color="k",ms=8)
ax.plot(pd.Timestamp("2014-04-05 03:05"),0.55,"o",mfc="#e7298a",mec="#e7298a",ms=5)
ax.plot(pd.to_datetime(["2014-04-06 12:00","2014-04-08 12:00"]),[1,1],"x",color="0.2",ms=5)
ax.plot(pd.Timestamp("2014-04-08 12:00"),0.55,"v",color="0.2",ms=5)
ax.axvspan(pd.Timestamp("2014-04-13"),pd.Timestamp("2014-04-18"),ymin=0.02,ymax=0.18,color="#d95f02",alpha=0.25,lw=0)
ax.text(pd.Timestamp("2014-04-13 06:00"),0.0,"air search of drifted area 13-17 Apr",fontsize=6,color="#a6400a",va="center")
ax.text(pd.Timestamp("2014-03-21"),1.0,"acoustic contacts (★), ship checks 6 and 8 Apr (×)",fontsize=6,va="center")
ax.text(pd.Timestamp("2014-03-21"),0.5,"white objects ~90 km away (●); sonobuoys 8 Apr (▼)",fontsize=6,va="center")
for dd,lab in [("2014-04-07","30-day beacon minimum"),("2014-04-17","40-day maximum")]:
    ax.axvline(pd.Timestamp(dd),color="0.5",lw=0.6,ls="--"); ax.text(pd.Timestamp(dd)+pd.Timedelta(hours=8),7.55,lab,fontsize=6,color="0.35")
ax.set_yticks([y for y,_ in labels]+[0.75]); ax.set_yticklabels([l for _,l in labels]+["events at the contact site"])
ax.set_ylim(-0.4,7.9); ax.set_xlim(d0-pd.Timedelta(days=0.5),d1)
ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=[8,15,22,29,1])); ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
ax.set_xlabel("Date in 2014 (UTC)")
ax.set_title("Only coarse daily imagery is listed for the study area",loc="left")
f1="Plain: Each mark is one saved satellite picture of the study area (25-26.5° S, 100-102.5° E). Coarse pictures cannot show objects of a few metres."
f2=("Technical: NASA CMR granules MOD02QKM/MYD02QKM v6.1, VNP02IMG (n = 65/64/160, 8 Mar-30 Apr 2014); USGS Landsat STAC landsat-c2l1 0; NASA CSDA "
    "WV01/WV02/GE01/QB02/IKONOS L1B 0 (archive subset); ASF and Copernicus Sentinel-1 0. Event times: ATSB 2017 pp.29-39, JACC 6 Apr 2014 (contact 2 at 15:47 AWST); "
    "contact 1 hour not published (bar placed at 08:00 UTC). No posterior or ocean model used.")
fig.text(0.01,0.075,"\n".join(textwrap.wrap(f1,170)),fontsize=6); fig.text(0.01,0.0,"\n".join(textwrap.wrap(f2,185)),fontsize=5.5)
fig.subplots_adjust(left=0.30,right=0.98,top=0.9,bottom=0.30)
fig.savefig("out/fig-locality-imagery-timeline.png",dpi=300)
r=fig.canvas.get_renderer()
texts_=[(t,t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
ticks=set(ax.get_xticklabels()+ax.get_yticklabels())
print([(a.get_text()[:25],b.get_text()[:25]) for i,(a,ba) in enumerate(texts_) for b,bb in texts_[i+1:] if ba.overlaps(bb) and not (a in ticks and b in ticks)])