zd=np.load(f'ocean/drift_dense_{REF_A}.npz'); cells_d=zd['cells']
wT=hT[cells_d]/hT[cells_d].sum(); wC=hC[cells_d]/hC[cells_d].sum(); wS=hs[cells_d]/hs[cells_d].sum()
drows=[]
for dn in sorted(byday):
    ins=zd[f'inbox|{dn}']; u_=unary_union([g for _,g in byday[dn]])
    drows.append(dict(date=(dt.date(2014,3,7)+dt.timedelta(days=dn)).isoformat(),day_index=dn,n_boxes=len(byday[dn]),weather='poor' if dn in POOR else 'fair or good',
        pod_csiro=0.15 if dn in POOR else 1.0, strip_area_in_boxes=strip_poly.intersection(u_).area/strip_poly.area, disc200_area_in_boxes=X200.intersection(u_).area/X200.area,
        debris_in_boxes_strip=float(wS@ins), debris_in_boxes_T=float(wT@ins), debris_in_boxes_C=float(wC@ins)))
DD=pd.DataFrame(drows); DD.to_csv('surface-search-days-locality.csv',index=False)
fig,(a1,a2)=plt.subplots(1,2,figsize=(11,6.4),gridspec_kw={'width_ratios':[1.15,1]})
Lg=Lgrid[(REF_A,'csiro')]
cl=GLAT0+(np.arange(GNY*GNX+1)//GNX+0.5)*GST; cn=GLON0+(np.arange(GNY*GNX+1)%GNX+0.5)*GST
img=np.full((GNY,GNX),np.nan); okk=np.isfinite(Lg[:-1]); img.ravel()[okk]=Lg[:-1][okk]
im_=a1.imshow(img,origin='lower',extent=[GLON0,GLON0+GNX*GST,GLAT0,GLAT0+GNY*GST],cmap='viridis',vmin=0,vmax=1,zorder=1)
for dn in sorted(byday):
    for _,g in byday[dn]:
        for q in getattr(g,'geoms',[g]):
            if q.geom_type=='Polygon': x_,y_=q.exterior.xy; a1.plot(x_,y_,c='white',lw=0.3,alpha=0.6,zorder=2)
a1.plot(arc_lon,arc_lat,':',c='k',lw=1.2,zorder=3); a1.plot(*zip(*bline),c='#1f4e9c',lw=1.1,zorder=3)
a1.plot(101.369,-25.732,marker='*',ms=13,mfc='white',mec='k',zorder=5); a1.plot(101.461,-25.975,'o',ms=6,mfc='none',mec='#e0553a',mew=1.4,zorder=5)
la,lo=trk['2014-04-13']; a1.scatter(lo,la,s=3,c='#ff9f1c',zorder=4,label='debris from the crossing on 13 Apr (1.2 % windage)')
a1.set_xlim(90,106); a1.set_ylim(-35,-18); a1.set_aspect(1/np.cos(np.radians(26)))
a1.set_xlabel('longitude (deg E)'); a1.set_ylabel('latitude (deg)'); a1.set_title('Debris from the north of the arc was likely to drift into searched boxes',loc='left')
cb=fig.colorbar(im_,ax=a1,shrink=0.7,pad=0.02); cb.set_label('probability that the search saw no debris\n(impact in this cell)')
a1.legend(loc='lower right',frameon=False,fontsize=7)
x=np.arange(len(DD)); col=['#c9c9c9' if w=='poor' else '#1f4e9c' for w in DD.weather]
a2.bar(x,DD.debris_in_boxes_T,color=col,width=0.75)
a2.plot(x,DD.debris_in_boxes_C,ls='none',marker='o',ms=4,mfc='white',mec='k')
a2.set_xticks(x[::3]); a2.set_xticklabels([d[5:] for d in DD.date[::3]],rotation=60)
a2.set_ylabel('share of floating debris inside that day\'s boxes'); a2.set_xlabel('search day (2014, month-day)')
a2.set_title('Most of the exposure fell on 28-30 Mar, 13-14 Apr and 21-26 Apr',loc='left')
a2.legend(handles=[Patch(fc='#1f4e9c',label='fair or good day, 00:52:03 reception'),Patch(fc='#c9c9c9',label='poor-weather day, 00:52:03 reception'),
                   Line2D([],[],ls='none',marker='o',mfc='white',mec='k',label='00:54:30 reception')],frameon=False,loc='upper left',fontsize=7)
a2.margins(x=0.02)
panel_letter(a1,'a'); panel_letter(a2,'b')
f1=("Plain: Each day in March-April 2014, aircraft and ships searched boxes on the sea for floating debris. We moved debris from each possible impact "
    "point with ocean currents and wind and counted the days on which it was inside a box. Colour shows the chance that nobody saw the debris. "
    "Low values mean the search argues against an impact there. The daily detection chance was not published; we used the CSIRO assumption.")
f2=("Technical: 387 GA/AMSA ArcGIS polygons D11-D52 (grade A geometry, no POD); POD per box-day 1.0 / 0.15 on poor days (CSIRO 2016 Part I p.23, 2017 Part IV pp.1-2), "
    "averaged over parcels. Drift: GlobCurrent 0 m daily + 0.5 % of CMEMS L4 hourly 10 m wind (product-relative, as the drift module; 1.2 % and 2.5 % sensitivities), "
    "K 100 m2/s, 256 parcels per 0.25 deg cell. Panel b weights: run J, 00:19 data held out, q=1/3 (C2 silent), x pre-registered acoustic likelihood (core). Physics not calibrated.")
fig.subplots_adjust(left=0.06,right=0.98,top=0.92,bottom=0.27,wspace=0.28)
fig.text(0.05,0.14,'\n'.join(textwrap.wrap(f1,190)),fontsize=7,va='top'); fig.text(0.05,0.075,'\n'.join(textwrap.wrap(f2,200)),fontsize=6.5,va='top',color='#444')
fig.savefig('fig2-surface-search-locality.png',dpi=200); fig.savefig('fig2-surface-search-locality.pdf')
print(DD[DD.debris_in_boxes_T>0.01][['date','weather','debris_in_boxes_T','debris_in_boxes_C','strip_area_in_boxes','disc200_area_in_boxes']].round(3).to_string(index=False))