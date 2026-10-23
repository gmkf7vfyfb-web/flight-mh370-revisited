plt.close('all')
fig,axs=plt.subplots(1,2,figsize=(11.5,6.0),sharey=True,gridspec_kw={'wspace':0.05})
sc=axs[0].scatter(lo[idx],la[idx],c=tu[idx]/60,s=0.6,cmap='viridis',vmin=20,vmax=45,rasterized=True,lw=0)
cb=fig.colorbar(sc,ax=axs[0],orientation='horizontal',pad=0.09,fraction=0.045,extend='both'); cb.set_label('Impact time (minutes after 00:00 UTC, 8 Mar 2014)')
hb=axs[1].hexbin(lo,la,C=w,reduce_C_function=np.sum,gridsize=(70,60),extent=ext,cmap='Greys',norm=LogNorm(vmin=w.sum()*1e-6),mincnt=1,linewidths=0)
cb2=fig.colorbar(hb,ax=axs[1],orientation='horizontal',pad=0.09,fraction=0.045); cb2.set_label('Posterior probability per cell (log scale)')
for ax in axs:
    for az,ls in [(305.18,':'),(305.68,'--'),(306.68,'--'),(307.18,':')]:
        x,y=bline(az); ax.plot(x,y,ls,color='tab:red',lw=0.8)
    x,y=bline(306.18); ax.plot(x,y,'-',color='tab:red',lw=1.3)
    ax.fill_betweenx(lats,arc7m,arc7p,color='tab:blue',alpha=0.18,lw=0)
    ax.plot(arc7,lats,'-',color='tab:blue',lw=1.5); ax.plot(arc6,lats,'-',color='tab:cyan',lw=1.2)
    ax.plot(seg['C'][:,0],seg['C'][:,1],'-',color='magenta',lw=7,alpha=0.55,solid_capstyle='butt')
    ax.plot(seg['T'][:,0],seg['T'][:,1],'-',color='darkorange',lw=2.6,solid_capstyle='butt')
    for nm,col in (('T','darkorange'),('C','magenta')):
        ax.plot(*seg[nm][-1],'o',ms=4,color=col,mec='k',mew=0.5)
    ax.plot(*X,'o',ms=8,mfc='white',mec='tab:red',mew=2)
    ax.plot(*hx,'*',ms=13,color='gold',mec='k',mew=0.8)
    ax.set_xlim(ext[0],ext[1]); ax.set_ylim(ext[2],ext[3]); ax.set_aspect(1/np.cos(np.radians(25.5))); ax.set_xlabel('Longitude (°E)')
axs[0].set_ylabel('Latitude (°; south is negative)')
axs[0].set_title('Simulated impacts near the bearing–arc crossing, by impact time',loc='left')
axs[1].set_title('Same impacts weighted by the flight-path posterior',loc='left')
h[7]=Line2D([],[],color='darkorange',lw=2.6,label='Kadri impact, text time 00:52:03 (0–188 km)')
h[8]=Line2D([],[],color='magenta',lw=7,alpha=0.55,label='Kadri impact, caption time 00:54:30 (0–219 km)')
fig.legend(handles=h,loc='upper center',bbox_to_anchor=(0.5,0.115),ncol=3,frameon=False,fontsize=7.5)
foot=("Note (plain): Dots are simulated impact points from the flight model. Left: the colour shows the impact time. Right: darker cells have more probability. "
 "The red line is the direction of Kadri's sound from Cape Leeuwin. The orange and pink lines show where his equation puts the impact for his two printed times, "
 "for aircraft speeds from 0 to 250 m/s along the line. The star is the Haixun 01 sound contact. It is shown only for comparison.\n"
 "Note (technical): Run J end of flight, waypoints family (P = 0.998), 24 seeds pooled at equal weight; 3.08 M of 153.6 M rows in 22–29 S, 97–105 E. Left: unweighted, random 150 k subsample; "
 "colour clipped at 00:20 and 00:45. Right: hand-off weight × within-parent weight; 00:19 BTO/BFO likelihood, log-on cause factor and D5 not applied (00:19 data held out); share in box 1.6 %, "
 "within 100 km of the crossing 0.33 %, weighted median impact time there 00:27 (5–95 %: 00:15–00:47). Times from run.json T0_unix_s = 1394236800 (00:00 UTC). "
 "Arcs: corrected BTO 18,400 µs (00:19:29) and 18,040 µs (00:10:59), Inmarsat ephemeris, Perth GES, WGS84, h = 0. Bearing: WGS84 geodesic from the H01W triad centroid (34.8903 S, 114.1426 E). "
 "Kadri eq. 4 with c = 1.48 km/s. Haixun: ATSB 2017 p. 38. Physics provisional; no search, drift or acoustic evidence applied.")
fig.text(0.06,0.0,foot,ha='left',va='top',fontsize=7,wrap=True)
fig.subplots_adjust(bottom=0.24)
fig.savefig('kadri-crossing-impact-map.png',dpi=200,bbox_inches='tight')
r=fig.canvas.get_renderer()
texts=[(tt,tt.get_window_extent(r)) for tt in fig.findobj(mpl.text.Text) if tt.get_text().strip() and tt.get_visible()]
ov=[(a.get_text()[:30],b.get_text()[:30]) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb)]
print('overlaps',ov[:6])