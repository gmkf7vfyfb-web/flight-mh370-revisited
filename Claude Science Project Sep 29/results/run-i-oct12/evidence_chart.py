import textwrap, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
out="repo/Claude Science Project Sep 29/results/run-i-oct12"
D=pd.read_csv(f"{out}/run-i-evidence-by-data-point.csv")
lab={'r0414':'18:04:14 radar','r0515':'18:05:15 radar','r0716':'18:07:16 radar','r1336':'18:13:36 radar',
     'b1815':'18:15 radar band','b1817':'18:17 radar band','b1819':'18:19 radar band','b1821':'18:21 radar band','r1822':'18:22:12 radar',
     'm1825':'18:25:34 BTO only (log-on)','m1828a':'18:28 BTO+BFO (a)','m1828b':'18:28 BTO+BFO (b)','m1839':'18:39 BFO only (phone call)','m1941':'19:41 BTO+BFO',
     'm2041':'20:41 BTO+BFO','m2141':'21:41 BTO+BFO','m2241':'22:41 BTO+BFO','m2315':'23:15 BFO only (phone call)','m0011':'00:11 BTO+BFO','m0019a':'00:19 (a)','m0019b':'00:19 (b)'}
cols=['free flight','descent-climb','reproduction (Davey)']; cc={'free flight':'#d95f02','descent-climb':'#7570b3','reproduction (Davey)':'#666666'}
apply_figure_style()
fig,axs=plt.subplots(1,2,figsize=(7.2,5.0),gridspec_kw=dict(width_ratios=[1.35,1]))
ax=axs[0]; y=np.arange(len(D))[::-1]; h=0.26
for i,cn in enumerate(cols):
    ax.barh(y+(1-i)*h, D[f'waypoints minus {cn}'], h, color=cc[cn], label=f"against {cn}", xerr=D[f'sd {cn}'], error_kw=dict(lw=0.5,capsize=0))
ax.axvline(0,color='k',lw=0.6); ax.set_yticks(y); ax.set_yticklabels([lab[e] for e in D.epoch]); ax.set_ylim(-0.6,len(D)-0.4)
ax.set_xlim(-3.2,1.9); ax.legend(frameon=False,loc='upper left',fontsize=6)
ax.set_xlabel("Gain in log-evidence for waypoints at this data point (nats)"); ax.set_title("Where the waypoint family gains its evidence",loc='left'); panel_letter(ax,'a')
ax=axs[1]
groups=[('Radar band VAMPI–MEKAR\n18:15–18:21',['b1815','b1817','b1819','b1821']),('Radar points\n18:04–18:22',['r0414','r0515','r0716','r1336','r1822']),
        ('18:25 BTO, 18:28\nBTO+BFO',['m1825','m1828a','m1828b']),('18:39 BFO\n(phone call)',['m1839']),('19:41',['m1941']),('20:41',['m2041']),('21:41–23:15',['m2141','m2241','m2315']),('00:11',['m0011']),('00:19',['m0019a','m0019b'])]
S=D.set_index('epoch'); gv=[(g,S.loc[e,'waypoints minus free flight'].sum()) for g,e in groups]; yy=np.arange(len(gv))[::-1]
ax.barh(yy,[v for _,v in gv],0.6,color=['#08519c' if v>0 else '#bdbdbd' for _,v in gv])
for yi,(g,v) in zip(yy,gv): ax.text(v+(0.05 if v>=0 else -0.05),yi,f"{v:+.2f}",va='center',ha='left' if v>=0 else 'right',fontsize=6)
ax.axvline(0,color='k',lw=0.6); ax.set_yticks(yy); ax.set_yticklabels([g for g,_ in gv]); ax.set_xlim(-1.7,3.3)
ax.set_xlabel("Gain against free flight (nats)"); ax.set_title(f"Waypoints against free flight: total {sum(v for _,v in gv):+.2f}",loc='left'); panel_letter(ax,'b')
fig.subplots_adjust(left=0.17,right=0.98,top=0.93,bottom=0.33,wspace=0.75)
ste=("Simple version (ASD-STE100): Each bar shows how much better the waypoint paths agree with one item of data than the other paths do. "
     "A bar to the right helps the waypoint paths. The largest gains are at the radar band between VAMPI and MEKAR (18:15 to 18:21), at the "
     "frequency data of the 18:39 phone call, and at the satellite data at 19:41. The waypoint paths fly exactly on the line from VAMPI to MEKAR, and the radar band is on that line. "
     "The total gain against free flight is 6.8. This gives the waypoint paths 99.8 % of the probability when the four groups have the same prior probability.")
tech=("Technical version: Core run I, 8 seeds per family. Per data point, the stratum's sequential log-evidence increment ln p(y_k | y_1..k-1), "
      "modes combined by their prior weights; bars are waypoints minus the other family, mean over seeds, error bars the seed standard deviation "
      "(zero where all seeds share the same early particles). The increments sum exactly to the difference in total log-evidence; each is conditional "
      "on all earlier items, so the split depends on data order. Radar band = across-track scores against the VAMPI–MEKAR great circle at four times, "
      "sd 1.5 NM (radar-full.toml). The waypoint family flies the VAMPI–MEKAR prefix with no lateral randomness from 18:01:49 to 18:21; the other families "
      "carry lateral dispersion there. 18:39 and 23:15 are C-channel calls: BFO only, no BTO. 00:19: core, Davey both-BTO no-BFO.")
fig.text(0.02,0.215,'\n'.join(textwrap.wrap(ste,165)),fontsize=6,va='top')
fig.text(0.02,0.115,'\n'.join(textwrap.wrap(tech,165)),fontsize=6,va='top',color=META_GREY)
fig.canvas.draw(); r=fig.canvas.get_renderer()
texts=[t for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
print('overlaps', [(a.get_text()[:20],b.get_text()[:20]) for i,a in enumerate(texts) for b in texts[i+1:] if a.get_window_extent(r).overlaps(b.get_window_extent(r))])
fig.savefig(f"{out}/run-i-evidence-by-data-point.png",dpi=300); fig.savefig(f"{out}/run-i-evidence-by-data-point.pdf")
