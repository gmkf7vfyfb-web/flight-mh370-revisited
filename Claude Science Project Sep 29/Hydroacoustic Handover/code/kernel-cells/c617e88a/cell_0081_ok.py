O=json.load(open("work/result/rhyd_mixture.json"))
opts=list(O)
fig,ax=plt.subplots(figsize=(7.2,4.4)); fig.subplots_adjust(left=0.27,right=0.97,top=0.86,bottom=0.36)
ax.axvspan(-0.5,0.5,color="#eeeeee",lw=0,zorder=0); ax.axvline(0,color="k",lw=0.6)
for b in (0.5,1.0):
    for sg in (-1,1): ax.axvline(sg*b,color="k",lw=0.4,ls="--",alpha=0.5)
SENS=[("A-IMOS","IMOS recorders only","s"),("A-VKE","vertical kinetic energy only","^"),("H01W-only","Kadri H01W list only","D")]
yt=[]
for i,o in enumerate(opts):
    y=len(opts)-1-i; d=O[o]
    for dy,lab,col,mk in ((0.12,"reweighted",FOC,"o"),(-0.12,"fixed",GRY,"o")):
        r=d[f"{lab}|A"]; ax.errorbar(r["lnR"],y+dy,xerr=2*r["split_half_se"],fmt=mk,color=col,ms=5,capsize=2,lw=1.2,zorder=3)
        if lab=="reweighted": ax.text(r["lnR"],y+0.3,f"{r['lnR']:+.3f} ± {r['split_half_se']:.3f}",ha="center",fontsize=6,color=FOC)
    for k,(v,lab,mk) in enumerate(SENS):
        r=d[f"reweighted|{v}"]; ax.plot(r["lnR"],y-0.33,mk,mfc="none",mec="k",ms=4,mew=0.7)
ax.set_yticks(range(len(opts))); ax.set_yticklabels(opts[::-1]); ax.set_ylim(-0.6,len(opts)-0.4)
ax.set_xlim(-0.65,0.65); ax.set_xlabel("ln R_hyd (log Bayes factor component; > 0 favours H, < 0 favours no H)")
ax.text(0,len(opts)-0.48,"within noise (|ln R| < 0.5)",ha="center",fontsize=6,va="bottom")
hd=[Line2D([],[],color=FOC,marker="o",lw=1.2),Line2D([],[],color=GRY,marker="o",lw=1.2)]+[Line2D([],[],ls="",marker=mk,mfc="none",mec="k") for _,_,mk in SENS]
fig.legend(hd,["strata re-weighted by the 00:19 data (± 2 split-half σ)","strata at fixed core weights (± 2 split-half σ)"]+[f"sensitivity: {l}" for _,l,_ in SENS],frameon=False,fontsize=6,ncol=3,loc="lower center",bbox_to_anchor=(0.6,0.215))
fig.suptitle("The sound data held neither favour nor disfavour the Pléiades hypothesis: every 00:19 option is within noise",fontsize=8,x=0.01,ha="left",y=0.975)
ste=("The chart shows how much the sound data change the odds that the Pléiades and COSMO-SkyMed objects are debris from the aircraft. Values between -0.5 and +0.5 tell nothing. "
     "All results are in that band; the small negative values come from no signal at the IMOS recorders. Run by an architecture stand-in; the module must review it. Core run (b) is not converged.")
tech=("R_hyd = E_H[L_hyd]/E_flight[L_hyd] on EoF next-run impacts (3c6319f; core (b), prior track 289.7°), 4 strata × 4 seeds × 3.2 M rows; weights EoF option_posteriors, log-on cause other, +alive; Holland H1/H2 excluded (not yet estimable). "
      "L_P = exp(lnL_both_mean), Pléiades rating-5 6 clusters + COSMO-SkyMed F1-F4, GLORYS12 + GlobCurrent daily (+ERA5), transport errors independent, windage as run (F1); not-computed rows (0.5-2 % of weight) excluded under H. "
      "L_hyd: IMOS 3315/3376/3274/3275 at α 0.05/50 s in scored segments + Kadri Table 1 at H01W; F-35A η, RAM TL, total KE; proxies for IMS noise and P_D. Error = RMS split-half over 3 balanced seed partitions. Two-tank bookkeeping only. Pre-registration c8b64a8.")
wrapfoot(fig, ste, tech)
fig.savefig("work/fig_result_rhyd.png",dpi=200)