
dv=pd.read_csv('work/davey_fig10_3_vector.csv')
edges=np.arange(-45,-14.95,0.1); hc,_=np.histogram(slat,bins=edges,weights=sw); xc=0.5*(edges[1:]+edges[:-1])
pdf=gaussian_filter(hc,1.0)/0.1   # per degree
def dens(l): return np.interp(l,xc,pdf)
def massband(l,h=0.5): return sw[np.abs(slat-l)<h].sum()
VL=[('G','pair locus (time difference)',G['lat'],C_G,'-',2.0),('00:52:50','Table 1 00:52:50, 274.84°',-32.24,C_T1,'-',1.2),
    ('D',"Kadri 306.18° (D)",-25.68,C_KADRI,'--',1.4),('00:39:02','Table 1 00:39:02',-33.78,'#8c8c8c',':',1.0),
    ('A','A',LOCI['A']['lat'],'#8c8c8c','-',0.9),('B','B',LOCI['B']['lat'],'#8c8c8c','-',0.9),('E','E',LOCI['E']['lat'],'#5e5e5e','-.',0.9),('F','F',LOCI['F']['lat'],'#5e5e5e','-.',0.9)]
def chart5():
    fig=plt.figure(figsize=(8.6,6.4)); ax=fig.add_axes([0.08,0.40,0.62,0.53])
    ax.fill_between(xc,pdf,color=HPD_FILL[1],alpha=0.8,lw=0); ax.plot(xc,pdf,color=HPD_FILL[2],lw=1.2,label='simulated impacts, latitude density')
    ax.plot(dv.latitude_deg,dv.density_per_deg,color='#444444',lw=1.0,ls='--',label='Davey et al. (2016), Fig. 10.3')
    ymax=max(pdf.max(),dv.density_per_deg.max())*1.12
    rows=[]
    for k,lab,l,c,ls,lw in VL:
        ax.axvline(l,color=c,ls=ls,lw=lw,zorder=3); ax.scatter([l],[dens(l)],s=18,c=c,zorder=5,edgecolors='white',lw=0.5)
        rows.append((k,lab,l,dens(l),massband(l)))
    for k,y in [('G',0.93),('00:52:50',0.80),('D',0.93),('00:39:02',0.67)]:
        l=[r for r in VL if r[0]==k][0][2]; c=[r for r in VL if r[0]==k][0][3]
        ax.text(l+0.15,ymax*y,{'G':'pair locus\n33.6°S','00:52:50':'Table 1\n00:52:50','D':"Kadri 306.18°\n(D), 25.7°S",'00:39:02':'Table 1\n00:39:02'}[k],color=c,fontsize=6.5,va='top')
    for k,l in [('A',LOCI['A']['lat']),('B',LOCI['B']['lat']),('E',LOCI['E']['lat']),('F',LOCI['F']['lat'])]:
        ax.text(l,-ymax*0.035,k,color='#5e5e5e',fontsize=6.5,ha='center',va='top')
    ax.set_xlim(-42,-20); ax.set_ylim(-ymax*0.09,ymax); ax.axhline(0,color='#999999',lw=0.5)
    ax.set_xlabel('Latitude of the arc crossing (°; south negative)'); ax.set_ylabel('Probability density per degree')
    ax.set_title('The pair locus sits on the northern shoulder of the impact density; Kadri\'s 306.18° crossing sits in its tail',loc='left',fontsize=8)
    ax.legend(loc='upper left',frameon=False,fontsize=6.5)
    # table on the right
    tx=fig.add_axes([0.72,0.40,0.27,0.53]); tx.axis('off')
    lines=['Arc crossing        lat °S  density  mass ±0.5°']
    for k,lab,l,d,m in rows: lines.append(f"{k:<9}{'':<11}{-l:5.2f}   {d:5.3f}   {m:5.3f}")
    tx.text(0,1,'\n'.join(lines),family='monospace',fontsize=6.3,va='top')
    tx.text(0,0.55,"A, B: Table 1 bearings 00:49:58, 00:53:31\nE: Cape Leeuwin 00:52:04 x Diego Garcia 01:10:01\nF: Cape Leeuwin 00:54:27 x Diego Garcia 01:12:49\nmass ±0.5°: share of simulated impacts\nwithin 0.5° of latitude",fontsize=6.3,va='top',color='#333333')
    ste=("The blue curve shows where the simulated impacts are along the arc. The vertical lines show where each sound gives a point on the arc. "
         "The pair point (33.6°S) is where the curve is about half its peak height. Kadri's direction 306.18° gives 25.7°S, where there are few simulated impacts. "+PAIR_STE)
    tech=(PAIR_TECH+" Density: run J impact latitudes (geometry/sample.npz, waypoints seeds 1-8 stride 6 + northern supplement, Kish ESS 110k), D0', 0.1° bins, "
          "Gaussian smoothing sigma 0.1°. The x-axis is the latitude of the impact for the density and of the arc crossing for the lines. Davey et al. (2016), Fig. 10.3, recovered "
          "from the PDF vector paths (BTO + BFO). Loci E, F, G solved from the lag on the module TL-grid arc at c = 1.482 km/s. Locus C of the earlier chart is not legible and is not redrawn. "+COMMON_TECH)
    footnotes(fig,ste,tech,width=170)
    return fig, rows
fig,rows5=chart5(); save(fig,'chart5-latitudes-pair-g')
for r in rows5: print(r)
