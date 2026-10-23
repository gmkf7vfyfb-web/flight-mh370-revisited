
SO.to_csv('out/settling_ocean_sensitivity_at_haixun.csv',index=False)
SOx=SO.copy()
order=['GLORYS12V1 baseline','HYCOM GOFS 3.1 (53.X)','current x0.5','current x1.5','current x2','current rotated +90 deg','current rotated 180 deg']
SOx['ocean']=pd.Categorical(SOx.ocean,order,ordered=True); SOx=SOx.sort_values('ocean'); SOx['ocean']=SOx.ocean.astype(str)
def render_disp(fname, SOx):
    fig,axs=plt.subplots(1,2,figsize=(7.2,4.0),gridspec_kw=dict(width_ratios=[1.3,1]))
    ax=axs[0]; yl=[]; y=0
    famc={'intact':'#2166ac','broken':'#5aae61','fragmented':'#762a83'}
    for cls in CLASSES:
        o=RES['runJ_L'][cls]
        for f,fn in enumerate(['intact','broken','fragmented']):
            D=o['D'][o['fam']==f]; q=np.nanpercentile(D,[10,50,90,99])
            ax.plot([q[0],q[2]],[y,y],color=famc[fn],lw=1.6,solid_capstyle='butt')
            ax.plot(q[1],y,'o',color=famc[fn],ms=4); ax.plot(q[3],y,'|',color=famc[fn],ms=6,mew=1.2)
            yl.append((y,f'{CLS_LABEL[cls]}, {fn}')); y-=1
        y-=0.6
    ax.set_yticks([a for a,_ in yl]); ax.set_yticklabels([b for _,b in yl],fontsize=6)
    ax.set_ylim(y+0.4,1.2)
    ax.set_xscale('log'); ax.set_xlim(0.03,30); ax.set_xticks([0.1,0.3,1,3,10]); ax.set_xticklabels(['0.1','0.3','1','3','10'])
    ax.set_xlabel('Distance from impact to rest on sea floor (km)')
    ax.set_title('Dense parts rest within 0.6 km',loc='left',fontsize=8)
    ax.text(0.035,0.75,'dot: median; bar: 10–90 %; tick: 99 %',fontsize=6)
    ax.axvline(2.0,color='#b2182b',lw=0.6,ls='--'); ax.text(2.15,-2.0,'2 km',color='#b2182b',fontsize=6)
    panel_letter(ax,'a')
    ax=axs[1]
    labs=list(dict.fromkeys(SOx.ocean)); yy=np.arange(len(labs))[::-1]
    for cls,col,mk in (('recorder-detached','k','o'),('fuselage-section','0.5','s')):
        s=SOx[SOx.cls==cls].set_index('ocean').loc[labs]
        ax.plot(s.p90.values,yy,mk,color=col,ms=4,ls='none',label={'recorder-detached':'detached recorder','fuselage-section':'recorder kept in aft fuselage'}[cls])
        ax.plot(s.p99.values,yy,mk,mfc='white',mec=col,ms=4,ls='none')
    ax.set_yticks(yy); ax.set_yticklabels(labs,fontsize=6); ax.set_ylim(-0.6,len(labs)+0.9)
    ax.set_xscale('log'); ax.set_xlim(0.2,30); ax.set_xticks([0.3,1,3,10]); ax.set_xticklabels(['0.3','1','3','10'])
    ax.set_xlabel('Distance, 90 % filled, 99 % open (km)')
    ax.set_title('Current changes move recorders little',loc='left',fontsize=8)
    ax.legend(frameon=False,fontsize=6,loc='upper left',ncol=1,bbox_to_anchor=(0.0,1.0))
    panel_letter(ax,'b')
    fn1=("(i) The chart shows how far parts of the aircraft move between the impact and the sea floor. Engines, landing gear and a recorder that comes off sink in 20-50 minutes "
         "and stay within about 0.6 km. A recorder that stays in an aft fuselage part that floats for some hours can move up to about 12 km. A different ocean model or current changes these distances by a small amount.")
    fn2=("(ii) Panel a: run J rows in L (strip R7-60..R7+250 km, half-width 1 deg, or within 100 km of the arc crossing or Haixun), four route strata equal, 'weight' column (no 00:19 option term), GLORYS12V1, 40,000 draws per class. "
         "Panel b: impacts at the Haixun contact, 20,000 draws; HYCOM 53.X 00Z/03Z 8 Mar 2014 only (later times held at 03Z); scalings and rotations of GLORYS12V1 are bounding sensitivities. "
         "Settling physics PROVISIONAL (educated-estimate element table; recorder class declared here). Seabed AusSeabed 150 m / GEBCO_2026. Not a posterior.")
    fig.subplots_adjust(left=0.27,right=0.98,top=0.92,bottom=0.30,wspace=0.78)
    fig.text(0.01,0.155,textwrap.fill(fn1,205),fontsize=5.5,va='top')
    fig.text(0.01,0.085,textwrap.fill(fn2,215),fontsize=5.5,va='top',color='0.25')
    fig.savefig(fname,dpi=300); return fig
fig=render_disp('out/fig_settling_displacement.png',SOx)
r_=fig.canvas.get_renderer()
texts=[(t,t.get_window_extent(r_)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
print([(a.get_text()[:25],b.get_text()[:25]) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb)])
fn1=("(i) The map shows the sea-floor depth. Panel b shows where the aircraft must hit the water if a recorder on the sea floor is within 2 km of the Haixun 01 contact. "
     "A recorder that comes off moves less than 1 km while it sinks. A recorder that stays in a floating fuselage part can move up to about 12 km. The Kadri impact points are at least 21 km from the Haixun contact.")
fig2=render_map('out/fig_settling_haixun_map.png')
