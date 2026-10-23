from matplotlib.patches import Patch
from matplotlib.lines import Line2D
def windows_fig(p, fname, optname, pre="c8b64a8"):
    bins=np.array(p["bins_s"])/60; c=0.5*(bins[1:]+bins[:-1])
    fig,axs=plt.subplots(5,1,figsize=(7.2,7.2),sharex=True)
    fig.subplots_adjust(left=0.07,right=0.98,top=0.925,bottom=0.215,hspace=0.36)
    for ax,(s,lab) in zip(axs,STN):
        r=p["windows"][s]["reweighted"]
        h0=np.array(r["hist_flight"]); hH=np.array(r["hist_H"])
        ax.fill_between(c,0,h0,step="mid",color=GRY,alpha=0.45,lw=0)
        ax.step(c,hH,where="mid",color=FOC,lw=1.3)
        ax.set_ylim(0,max(h0.max(),hH.max())*1.25)
        lg = {"3376":["3315","3376"],"3274":["3274","3275"]}.get(s,[])
        for L in lg:
            for (a_,b_) in ev[L]["scored_segments"]: ax.axvspan(a_/60,b_/60,color="#e3a21a",alpha=0.45,lw=0)
            for t,_ in ev[L]["events"]["loose"]: ax.axvline(t/60,color="k",lw=0.9,ls=":")
        if s=="H01W": ax.axvspan(27,57,color="#e3a21a",alpha=0.35,lw=0)
        if s in ("H01W","H08S"):
            lo,hi={"H01W":(25,140),"H08S":(45,170)}[s]; ax.axvspan(lo,hi,ymin=0.93,ymax=1.0,color="k",alpha=0.6,lw=0)
        q0,qH=r["q_flight"][1]/60, r["q_H"][1]/60
        ax.set_title(f"{lab}: overlap {r['ovl']:.2f}; median {qH:.0f} min with, {q0:.0f} min without",loc="left",fontsize=7)
        ax.set_yticks([]); ax.set_ylabel("density",fontsize=6)
    axs[-1].set_xlabel("Predicted arrival time of the impact sound (minutes after 00:00 UTC, 8 March 2014)")
    axs[0].set_xlim(15,190)
    hd=[Patch(color=GRY,alpha=0.45,lw=0),Line2D([],[],color=FOC,lw=1.3),Patch(color="#e3a21a",alpha=0.5,lw=0),Line2D([],[],color="k",ls=":",lw=0.9),Patch(color="k",alpha=0.6,lw=0)]
    lb=["without the Pléiades hypothesis (flight data only)","with the Pléiades hypothesis","time searched for a signal (data held)","weak event found (recorder 3275, loose threshold)","raw recording requested, not held"]
    axs[1].legend(hd,lb,frameon=False,fontsize=6,loc="upper right")
    fig.suptitle(f"With the Pléiades hypothesis the impact sound is predicted 9-10 minutes earlier (median), but the spreads overlap at every station ({optname})",fontsize=8,x=0.01,ha="left",y=0.985,wrap=True)
    ste=("The chart shows when the sound of the impact would arrive at each station. Grey uses the flight data only. Blue also uses the Pléiades and COSMO-SkyMed debris sightings. "
         "Orange shows the times that were searched; the Perth Canyon panel includes recorder 3315 and the Portland panel recorder 3275. Run by an architecture stand-in; the module must review it. Core run (b) is not converged.")
    tech=(f"Source package sources-0019-{fname}.npz (5,000 rows; defensive mixture; ESS w_flight {p['ess']['ess_w_flight']:.0f}, w_H {p['ess']['ess_w_H']:.0f}; {p['not_computed']} rows not computed, zero weight under H). "
          "EoF next-run on core (b) (3c6319f; prior track 289.7°), 4 strata x 4 seeds, strata re-weighted by Ẑ_00:19; log-on cause other, +alive. SOFAR group speed 1.482 ± 0.006 km/s, WGS84 geodesic, no path delay. "
          "Overlap = Σ min(p_H, p_0), 1-min bins. Pléiades: rating-5 objects in 6 clusters + COSMO-SkyMed F1-F4; GLORYS12 + GlobCurrent daily (+ERA5), measured transport error, windage 0-5 % as run (audit F1); transport errors treated as independent. Two-tank bookkeeping only. "
          f"IMOS scored segments: 2b windows, stage A 'or' detector, α 0.05/50 s. H01W: Kadri (2024) Fig. 9 span 00:27-00:57. Pre-registration {pre}.")
    wrapfoot(fig, ste, tech)
    fig.savefig(f"work/fig_windows_{fname}.png",dpi=200); return fig
fig=windows_fig(p,"r600-bto-only","00:19 R600 BTO Only")