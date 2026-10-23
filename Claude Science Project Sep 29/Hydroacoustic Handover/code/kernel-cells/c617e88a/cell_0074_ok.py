SCN=[("A","Data held: IMOS recorders + Kadri's H01W event list (the test as pre-registered)"),
     ("A-IMOS","Data held: IMOS recorders only"),
     ("B","Data held, more of it searched: every IMOS recording of the night"),
     ("C","Data not held: raw H01W and H08S array recordings, with bearings (planning)")]
def power_fig(p, fname, optname, pre="c8b64a8"):
    fig,axs=plt.subplots(2,2,figsize=(7.2,5.6),sharex=True)
    fig.subplots_adjust(left=0.08,right=0.98,top=0.89,bottom=0.30,hspace=0.42,wspace=0.12)
    edges=np.arange(-8,5.01,0.2)
    for ax,(sc,lab) in zip(axs.flat,SCN):
        S=p["synthetic"][sc]
        vH=np.clip(S["H"]["reweighted"]["values"],-7.99,4.99); v0=np.clip(S["noH"]["reweighted"]["values"],-7.99,4.99)
        ax.hist(v0,edges,density=True,color=GRY,alpha=0.5,lw=0)
        ax.hist(vH,edges,density=True,histtype="step",color=FOC,lw=1.3)
        for b in (0.5,1,2.3):
            for sg in (-1,1): ax.axvline(sg*b,color="k",lw=0.4,ls="--",alpha=0.5)
        ax.set_yscale("log"); ax.set_ylim(1e-3,30)
        mH,m0=S["H"]["reweighted"]["mean"],S["noH"]["reweighted"]["mean"]
        ax.set_title("\n".join(textwrap.wrap(lab,58)),loc="left",fontsize=7)
        ax.text(0.02,0.96,f"mean ln R: {mH:+.2f} if H is true, {m0:+.2f} if not\nP(|ln R| ≥ 0.5): {S['H']['reweighted']['p_abs_ge_0p5']:.2f} / {S['noH']['reweighted']['p_abs_ge_0p5']:.2f}",
                transform=ax.transAxes,va="top",fontsize=6)
    for ax in axs[1]: ax.set_xlabel("ln R_hyd (log Bayes factor component; > 0 favours H)")
    for ax in axs[:,0]: ax.set_ylabel("density (log scale)")
    hd=[Line2D([],[],color=FOC,lw=1.3),Patch(color=GRY,alpha=0.5,lw=0),Line2D([],[],color="k",lw=0.4,ls="--")]
    axs[0,1].legend(hd,["synthetic data drawn with H true","synthetic data drawn from the flight posterior (no H)","reading bands |ln R| = 0.5, 1, 2.3"],frameon=False,fontsize=6,loc="center right")
    fig.suptitle(f"The data held can give a weak result at most; raw H01W and H08S recordings would often give a moderate or strong one ({optname})",fontsize=8,x=0.01,ha="left",y=0.985,wrap=True)
    ste=("The chart shows the result that the sound test would give, from 2,000 sets of made-up data for each case. Blue: the debris sightings are from the aircraft. Grey: they are not. "
         "A result near 0 tells nothing. The held data are weak because only short times were searched and the event list from H01W is incomplete. Run by an architecture stand-in; the module must review it. Core run (b) is not converged.")
    tech=(f"Power check, pre-registration {pre} §6. Source package sources-0019-{fname}.npz, 5,000 rows × 8 nuisance replicas, truth row left out; strata re-weighted by Ẑ_00:19 (fixed-weight results within 0.03 in mean). "
          "L_hyd: soft Poisson-background mixture, α 0.05/50 s; F-35A η (RAM-corrected TL); total kinetic energy; IMS noise and P_D are proxies (3376 median, 3274 fit, +4.8 dB triad gain); bearing t₃, 3.3°; pick 10 s. "
          "H01W (A, B): Kadri Table 1 over 00:27-00:57, background 18/(998 s×108.5°). C: raw-request windows H01W 00:25-02:20, H08S 00:45-02:50, λ 0.001 s⁻¹. "
          "EoF 3c6319f; core (b); log-on cause other, +alive. Pléiades + COSMO-SkyMed F1-F4, transport errors independent; GlobCurrent windage as run (F1); two-tank bookkeeping only. Values beyond the axis are drawn at its edge.")
    wrapfoot(fig, ste, tech)
    fig.savefig(f"work/fig_power_{fname}.png",dpi=200); return fig
fig=power_fig(p,"r600-bto-only","00:19 R600 BTO Only")