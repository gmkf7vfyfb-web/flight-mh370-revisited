import matplotlib as mpl, matplotlib.pyplot as plt, textwrap
apply_figure_style(sizes=(8,7,6))
FOC, GRY = "#1f5fa8", "#8c8c8c"
ev=json.load(open("work/imos_events_searched.json"))
STN=[("H01W","H01W hydrophone array, Cape Leeuwin (IMS)"),("3376","Perth Canyon recorder (IMOS)"),("3274","Portland recorder (IMOS)"),("H08S","H08S hydrophone array, Diego Garcia south (IMS)"),("H08N","H08N hydrophone array, Diego Garcia north (IMS)")]
def wrapfoot(fig, ste, tech, y0=0.005, width=175):
    a="\n".join(textwrap.wrap("(i) "+ste, width)); b="\n".join(textwrap.wrap("(ii) "+tech, width))
    fig.text(0.01, y0, a+"\n"+b, fontsize=6, va="bottom", ha="left", linespacing=1.25)
def windows_fig(p, fname, optname):
    bins=np.array(p["bins_s"])/60; c=0.5*(bins[1:]+bins[:-1])
    fig,axs=plt.subplots(5,1,figsize=(7.2,7.6),sharex=True)
    fig.subplots_adjust(left=0.09,right=0.98,top=0.93,bottom=0.25,hspace=0.32)
    for ax,(s,lab) in zip(axs,STN):
        r=p["windows"][s]["reweighted"]
        h0=np.array(r["hist_flight"]); hH=np.array(r["hist_H"])
        ax.fill_between(c,0,h0,step="mid",color=GRY,alpha=0.45,lw=0,label="without the Pléiades hypothesis (flight data only)")
        ax.step(c,hH,where="mid",color=FOC,lw=1.3,label="with the Pléiades hypothesis")
        top=max(h0.max(),hH.max())*1.15; ax.set_ylim(0,top)
        if s in ("3376","3274"):
            for k,(a_,b_) in enumerate(ev[s]["scored_segments"]):
                ax.axvspan(a_/60,b_/60,color="#e3a21a",alpha=0.55,lw=0,label="time searched for a signal" if k==0 else None)
            for t,_ in ev[s]["events"]["loose"]: ax.axvline(t/60,color="k",lw=0.8,ls=":")
        if s=="H01W": ax.axvspan(27,57,color="#e3a21a",alpha=0.35,lw=0,label="time searched for a signal")
        if s in ("H01W","H08S"):
            lo,hi={"H01W":(25,140),"H08S":(45,170)}[s]; ax.axvspan(lo,hi,ymin=0.93,ymax=1.0,color="k",alpha=0.6,lw=0)
        ax.set_title(f"{lab}: overlap {r['ovl']:.2f}",loc="left",fontsize=7)
        ax.set_yticks([])
    axs[2].text(1.0,0.5,"",transform=axs[2].transAxes)
    axs[-1].set_xlabel("Predicted arrival time of the impact sound (minutes after 00:00 UTC, 8 March 2014)")
    axs[0].set_xlim(15,190)
    for ax in axs: ax.set_ylabel("density",fontsize=6)
    h,l=axs[1].get_legend_handles_labels(); axs[0].legend(h,l,frameon=False,fontsize=6,loc="upper right")
    axs[3].text(0.995,0.98,"black bar: raw recording requested, not held",transform=axs[3].transAxes,ha="right",va="top",fontsize=6)
    axs[3].legend([],[],frameon=False)
    fig.suptitle(f"Predicted impact-sound arrival times are about 10 minutes earlier with the Pléiades hypothesis, but the two spreads overlap at every station ({optname})",fontsize=8,x=0.01,ha="left",y=0.985,wrap=True)
    ste=("The chart shows when the sound of the impact would arrive at each station. The grey area uses the flight data only. The blue line also uses the Pléiades and COSMO-SkyMed debris sightings. "
         "Orange shows the times that were searched. Dotted lines are the two weak events found at the second Portland recorder (3275, next to 3274). Run by an architecture stand-in; the module must review it. Core run (b) is not converged.")
    tech=(f"Source package sources-0019-{fname}.npz (5,000 rows; defensive mixture; ESS w_flight {p['ess']['ess_w_flight']:.0f}, w_H {p['ess']['ess_w_H']:.0f}; {p['not_computed']} rows not computed, zero weight under H). "
          "EoF next-run on core (b) (3c6319f; prior track 289.7°), 4 strata x 4 seeds, strata re-weighted by Ẑ_00:19; log-on cause other, +alive. SOFAR group speed 1.482 ± 0.006 km/s, WGS84 geodesic, no path delay. "
          "Overlap = Σ min(p_H, p_0), 1-min bins. Pléiades: rating-5 objects in 6 clusters + COSMO-SkyMed F1-F4; GLORYS12 + GlobCurrent daily (+ERA5), measured transport error, windage 0-5 % as run (audit F1); transport errors treated as independent. Two-tank bookkeeping only. "
          "IMOS scored segments: 2b windows, stage A 'or' detector. H01W: Kadri (2024) Fig. 9 span 00:27-00:57. Pre-registration c8b64a8.")
    wrapfoot(fig, ste, tech)
    fig.savefig(f"work/fig_windows_{fname}.png",dpi=200); return fig
fig=windows_fig(p,"r600-bto-only","00:19 R600 BTO Only")