import json, textwrap, numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
EX="/Users/pete/Downloads/mh370-exchange/core/run-i"; out="repo/Claude Science Project Sep 29/results/run-i-oct12"
FAMS={'waypoints':'next-i-waypoints','free flight':'next-i-free','reproduction (Davey)':'next-i-repro-radar','descent-climb':'next-i-descent-climb'}
share={'waypoints':0.998217,'free flight':0.001134,'reproduction (Davey)':0.000437,'descent-climb':0.000212}
sh={'waypoints':0.916,'free flight':0.830,'reproduction (Davey)':0.891,'descent-climb':0.794}
col={'waypoints':'#08519c','free flight':'#d95f02','reproduction (Davey)':'#666666','descent-climb':'#7570b3'}
fmt=lambda p:f"{100*p:.1f} %" if p>0.1 else f"{100*p:.2f} %"
apply_figure_style()
fig,ax=plt.subplots(figsize=(7.2,5.6))
for f,d in FAMS.items():
    s=json.load(open(f"{EX}/{d}/summary.json")); g=s['grid']; c=s['cases'][0]; dn=np.array(c['density']); x=np.linspace(g['min'],g['max'],len(dn))
    for r_ in c['replicates']: ax.plot(x,r_['density'],color=col[f],lw=0.35,alpha=0.4)
    ax.plot(x,dn,color=col[f],lw=1.8 if f=='waypoints' else 1.2,label=f"{f}: median {c['stats']['median']:.2f}°, posterior {fmt(share[f])}, split-half {sh[f]:.2f}")
ref=json.load(open(f"{EX}/next-i-waypoints/summary.json"))['reference']; gr=json.load(open(f"{EX}/next-i-waypoints/summary.json"))['grid']
dv=np.array(ref['density']); xd=np.linspace(gr['min'],gr['max'],len(dv))
ax.plot(xd,dv,color='#e7298a',ls=(0,(5,2)),lw=1.4,label=f"Davey et al. (2016) Fig. 10.3, digitised: median {ref['stats']['median']:.2f}°")
ax.set_xlim(-39,-34); ax.set_ylim(0,2.3); ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(0.5))
ax.set_xlabel("Latitude at 00:19 UTC (degrees; negative = south)"); ax.set_ylabel("Probability density (per degree)")
ax.set_title("The four families against Davey Fig. 10.3, 39°S to 34°S: the waypoint family is narrower and 0.4° further north",loc='left')
ax.legend(frameon=False,fontsize=6,loc='upper right')
fig.subplots_adjust(left=0.09,right=0.98,top=0.95,bottom=0.30)
ste=("Simple version (ASD-STE100): The thick curves show where the aircraft probably was at 00:19 UTC for each group of possible early flights. "
     "The thin curves are the eight separate runs of each group. When the thin curves of a group are close together, the result for that group is sure. "
     "The waypoint group has 99.8 % of the probability. The dashed curve is the published result of Davey and others (2016, Figure 10.3).")
tech=("Technical version: Core run I, 12 Oct 2026; 8 seeds per family (7M particles per seed for free and waypoints, 3.5M for descent-climb and reproduction). "
      "Densities of 00:19 latitude from summary.json (0.1° smoothing); core 00:19 treatment, Davey both-BTO, no BFO. Family posteriors at equal prior from pooled "
      "log-evidence. Split-half is the mean overlap over 35 balanced seed partitions; the 8-seed floor is 0.924. Same data as Figure run-i-0019-latitude panel b, "
      "with the latitude range 39°S–34°S and the vertical scale doubled. Davey et al. (2016) Fig. 10.3 as digitised in the engine's reference (summary.json), on the same latitude grid; its southern tail continues past 39°S (2.5 % quantile 39.38°S).")
fig.text(0.02,0.20,'\n'.join(textwrap.wrap(ste,165)),fontsize=6,va='top')
fig.text(0.02,0.12,'\n'.join(textwrap.wrap(tech,165)),fontsize=6,va='top',color=META_GREY)
fig.canvas.draw(); r=fig.canvas.get_renderer(); texts=[t for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
print('overlaps',[(a.get_text()[:20],b.get_text()[:20]) for i,a in enumerate(texts) for b in texts[i+1:] if a.get_window_extent(r).overlaps(b.get_window_extent(r))])
fig.savefig(f"{out}/run-i-0019-latitude-zoom.png",dpi=300); fig.savefig(f"{out}/run-i-0019-latitude-zoom.pdf")
