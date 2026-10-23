figsrc2 = r'''
def fig_backward(ODd, lons_, lats_, title, n1b, n2b, fn='out/fig-backward-origin-ring', xl=(95.5,107), yl=(-31.5,-20.5)):
    fig,axs=plt.subplots(1,2,figsize=(7.2,4.0),sharey=True,gridspec_kw=dict(wspace=0.06))
    dl=lons_[1]-lons_[0]
    for ax,(m,lab) in zip(axs,[('globcurrent','GlobCurrent currents + ERA5 wind'),('glorys12','GLORYS12 currents + ERA5 wind')]):
        od=ODd[m]; LLg,LOg=np.meshgrid(lats_,lons_,indexing='ij'); post=od*np.cos(np.radians(LLg))
        t50,t90,t99=hpd_levels(post)
        ax.contourf(lons_,lats_,post,levels=[t99,t90,t50,post.max()*1.0001],colors=['#d9d9d9','#969696','#404040'],zorder=1)
        ax.add_patch(mpl.patches.Rectangle((lons_[0]-dl/2,lats_[0]-dl/2),lons_[-1]-lons_[0]+dl,lats_[-1]-lats_[0]+dl,fill=False,ec='#777777',lw=0.6,ls='-.',zorder=2))
        context(ax,xl,yl); ax.set_title(lab,loc='left')
    axs[0].set_ylabel('latitude (deg)')
    hh=[mpl.patches.Patch(color='#404040',label='50 %'),mpl.patches.Patch(color='#969696',label='90 %'),mpl.patches.Patch(color='#d9d9d9',label='99 % HPD of start point on 8 Mar'),
        mpl.lines.Line2D([],[],color='#777777',ls='-.',lw=0.6,label='edge of the start-point grid'),
        mpl.lines.Line2D([],[],color='k',lw=0.6,label='70 and 110 km from the Haixun 01 contact (triangle)'),
        mpl.lines.Line2D([],[],marker='*',color='#b2182b',ls='none',mec='k',label='bearing-arc crossing; dots 50-200 km inside'),
        mpl.lines.Line2D([],[],color='#1f4e9a',lw=1,label='7th arc at sea level'),mpl.lines.Line2D([],[],color='#e08214',lw=0.9,label='306.18 deg bearing from H01W')]
    fig.legend(handles=hh,loc='upper left',ncol=2,frameon=False,bbox_to_anchor=(0.08,0.12),fontsize=6)
    fig.suptitle(title,x=0.08,ha='left',fontsize=8,y=0.95)
    fig.text(0.08,-0.06,"\n".join(textwrap.wrap(n1b,170)),fontsize=6,va='top'); fig.text(0.08,-0.15,"\n".join(textwrap.wrap(n2b,170)),fontsize=6,va='top')
    fig.savefig(fn+'.png',dpi=300,bbox_inches='tight'); fig.savefig(fn+'.pdf',bbox_inches='tight'); plt.close(fig)
'''
open('figs.py','a').write(figsrc2); exec(figsrc2)
n1b=("Plain: We put floating objects at 1,763 start points on a 0.25 deg grid on 8 Mar 2014 at 00:35 UTC and found which start points give objects 70-110 km from the Haixun 01 contact at 03:15 UTC on 5 Apr 2014, "
     "when white objects were seen about 90 km from the contact (they were checked and were not from the aircraft). The shading is the probability of the start point, with equal weight for each area. "
     "The start points on the bearing and at the arc crossing are outside the 99 % region. PROVISIONAL: some probability is at the edge of the grid; a larger grid is in the queue.")
n2b=("Technical: forward-connectivity inversion with the debris-drift engine snapshot harness (drift d51d80a), 1,200 objects per start point (3 classes x 4 realisations x 100), 28-day forcing, "
     "GLORYS12V1 0.494 m or GlobCurrent 0 m + ERA5 U10 (GlobCurrent windage U(-0.75,-0.60) % U10), K log-uniform 100-1000 m2/s, refloat off. P(start | ring) proportional to P(ring | start) x cos(lat). "
     "Edge share of probability 10 % (GlobCurrent), 15 % (GLORYS12). No flight-path posterior, no 00:19 option, no search case. Sighting: JACC 5-6 Apr 2014 (grade A), direction not published.")
fig_backward(OD, lons, lats, 'Objects 70-110 km from the Haixun 01 contact on 5 April started away from the bearing-arc crossing on 8 March (provisional grid)', n1b, n2b)
