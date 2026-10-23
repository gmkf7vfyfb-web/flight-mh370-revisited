import csv, json, pathlib, textwrap, numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
WS=pathlib.Path("/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/462da3b0-2381-4cf6-84db-fe178606bed4")
O=WS/"out/next-run-b"
MW=pathlib.Path("/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/d74bf70e-a424-46a9-8149-902d027e782a/hydro-wt/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/search_windows/reference-289")
rows=list(csv.DictReader(open(O/"mixture/windows_by_arm.csv"))); rec=list(csv.DictReader(open(O/"mixture/recommended_windows.csv")))
rows289=list(csv.DictReader(open(MW/"windows_by_arm.csv"))); rec289=list(csv.DictReader(open(MW/"recommended_windows.csv")))
summ=json.load(open(O/"mixture/summary.json"))["arms"]
s2m=lambda h:(sum(int(x)*m for x,m in zip(h.split(":"),(3600,60,1)))/60.0)
apply_figure_style(sizes=(8,7,6))
C_AL,C_SI,C_REF="#1f4e9c","#d08c2a","0.55"
sel=[r for r in rows if r["branch"]=="sofar" and r["variant"]=="alive" and int(r["ess_pooled"])>=1000 and r["receiver"]=="H01W"]
arms=sorted({r["arm"] for r in sel}, key=lambda a:-summ[a+"+alive"]["ess_mixture_kish"])
pick=lambda R,arm,var,st,br="sofar":[x for x in R if x["arm"]==arm and x["variant"]==var and x["receiver"]==st and x["branch"]==br][0]
kadri={"H01W":(27,57),"H08S":(60,80)}
fig=plt.figure(figsize=(7.2,8.9))
gs=fig.add_gridspec(2,2,height_ratios=[2.3,1.15],hspace=0.3,wspace=0.06,left=0.25,right=0.98,top=0.885,bottom=0.25)
axa,axb=fig.add_subplot(gs[0,0]),fig.add_subplot(gs[0,1]); axc=fig.add_subplot(gs[1,:])
xl={"H01W":(20,125,30,121),"H08S":(45,150,60,151)}
for ax,st,let in ((axa,"H01W","a"),(axb,"H08S","b")):
    ax.axvspan(*kadri[st],color="0.9",zorder=0,lw=0)
    for i,arm in enumerate(arms):
        r0=pick(rows289,arm,"alive",st); ax.plot([s2m(r0["q0.5"]),s2m(r0["q99.5"])],[i-0.36]*2,color=C_REF,lw=0.7)
        ax.plot(s2m(r0["q99.5"]),i-0.36,"|",color=C_REF,ms=3)
        for var,col,dy in (("alive",C_AL,-0.12),("silent",C_SI,0.22)):
            r=pick(rows,arm,var,st); y=i+dy
            ax.plot([s2m(r["q0.5"]),s2m(r["q99.5"])],[y,y],color=col,lw=0.8,alpha=0.6)
            ax.plot([s2m(r["q5"]),s2m(r["q95"])],[y,y],color=col,lw=2.6,solid_capstyle="butt")
            ax.plot(s2m(r["q50"]),y,"o",ms=3.2,mfc="white",mec=col,mew=0.9,zorder=3)
            if r["converged"]=="no": ax.plot(s2m(r["q99.5"])+2.5,y,marker=(3,0,30),ms=3.5,color="0.35",ls="none")
    a0,a1,t0,t1=xl[st]; ax.set_xlim(a0,a1); ax.set_ylim(len(arms)-0.4,-0.7)
    t=np.arange(t0,t1,15); ax.set_xticks(t); ax.set_xticklabels([f"{int(m//60):02d}:{int(m%60):02d}" for m in t])
    ax.set_xlabel(f"SOFAR arrival at {st} (UTC, 8 Mar 2014)")
    ax.set_yticks(range(len(arms))); ax.set_yticklabels([a.replace("__"," · ") for a in arms] if st=="H01W" else [])
    panel_letter(ax,let)
recs=["H01W","H08S","H08N","3315","3376","3250","3274","3275"]
lab={"3315":"IMOS 3315 Perth Cyn","3376":"IMOS 3376 Perth Cyn","3250":"IMOS 3250 Scott Reef","3274":"IMOS 3274 Portland","3275":"IMOS 3275 Portland"}
pr=lambda R,var,rx,br:[x for x in R if x["variant"]==var and x["receiver"]==rx and x["branch"]==br][0]
for i,rx in enumerate(recs):
    for var,col,dy in (("alive",C_AL,-0.2),("silent",C_SI,0.12)):
        r=pr(rec,var,rx,"sofar"); a_=pr(rec,var,rx,"agw")
        axc.barh(i+dy,s2m(r["window_end"])-s2m(r["window_start"]),left=s2m(r["window_start"]),height=0.26,color=col,lw=0)
        axc.plot([s2m(a_["window_end"])]*2,[i+dy-0.13,i+dy+0.13],color="0.2",lw=0.8)
    r0=pr(rec289,"alive",rx,"sofar"); axc.plot([s2m(r0["window_start"]),s2m(r0["window_end"])],[i+0.36]*2,color=C_REF,lw=1.2)
axc.set_yticks(range(len(recs))); axc.set_yticklabels([lab.get(r,r) for r in recs]); axc.set_ylim(len(recs)-0.45,-0.6)
t=np.arange(15,181,15); axc.set_xticks(t); axc.set_xticklabels([f"{int(m//60):02d}:{int(m%60):02d}" for m in t]); axc.set_xlim(15,180)
axc.set_xlabel("Request window, SOFAR (UTC, 8 Mar 2014); black tick = end of AGW window")
axc.set_title("Request windows end 5–20 min earlier than on reference-289; starts unchanged",loc="left",fontsize=8)
panel_letter(axc,"c")
fig.text(0.25,0.985,"Predicted SOFAR arrivals from core (b) impacts, P(family) mixture, against reference-289",fontsize=8,ha="left",va="top")
fig.legend(handles=[Line2D([],[],color=C_AL,lw=2.6,label="+alive (reference)"),Line2D([],[],color=C_SI,lw=2.6,label="+silent (sensitivity)"),
    Line2D([],[],color=C_REF,lw=1.0,label="reference-289 +alive (0.5–99.5 %; window in c)"),
    Line2D([],[],color="0.3",lw=2.6,label="5–95 %"),Line2D([],[],color="0.3",lw=0.8,label="0.5–99.5 %"),
    Line2D([],[],marker="o",mfc="white",mec="0.3",ls="none",label="median"),
    Line2D([],[],marker=(3,0,30),color="0.35",ls="none",ms=4,label="tail unconverged (> 5 min replicate spread)"),
    Patch(color="0.9",label="Kadri (2024) Fig. 9 panel span")],
    loc="upper left",bbox_to_anchor=(0.24,0.965),ncol=3,frameon=False,fontsize=6,handlelength=1.8,columnspacing=1.0)
foot=("Run: hydroacoustics search windows, run by an architecture stand-in on the module's behalf; module to review. Labels: core (b): split-half NOT converged; two-tank bookkeeping only; PROVISIONAL-OVERNIGHT; EoF sweep run by a stand-in; uncorrected fuel; provisional sampler.\n"
"Impacts: mh370-exchange/end-of-flight/next-run (EoF 3c6319f, binary bcb6b252…), 4 strata x 4 seeds, ~3.2M rows/seed, from core (b) m0011 hand-offs; descent idle floor ON (off in reference-289); core s6-tanks dropped; single fuel pool, no one-engine phase. Prior track 289.7 ± 1.0 deg, deskstar, Inmarsat ephemeris, internal-v1 fuel.\n"
"Strata combined by core's P(family), held fixed and unconverged: free 0.6948, Davey dynamics + radar 0.1527, descent-climb 0.1376, routes 0.0149; seeds equal-weight within stratum. Replicate k = seed k of every stratum mixed by P(family); convergence rule applied to the 4 replicates.\n"
"Method: prepare/search_windows.py @ 438c9e9 (sha256 1b05492b…, unchanged), weights from EoF option_posteriors (displacement_hist.py @ 15ba915, sha256 f964a9b9…), SATCOM sha256 8ec8c211…; stand-in mixture wrapper standin_mixture.py reproduces the script per stratum exactly (0 of 4,896 quantiles differ).\n"
"Arrival: WGS84 geodesic / c, c ~ N(1.482, 0.006) km/s (SOFAR); AGW c ~ U(1.40, 1.50) km/s, an allowance not a model; no refraction or blockage lengthening. Window = [q0.5 − 10 min, q99.5 + 20 min], 5-min rounding, widened to replicate envelope if spread > 5 min; union over 20 arms with mixture Kish ESS ≥ 1,000.\n"
"Variants: +alive = airborne at 00:19:37.443; +silent = +alive and unpowered at 01:15:56 (EoF 04:05 UTC 10 Oct, provisional). Arms ordered by mixture ESS. Holland H1/H2 (both_startup-offset·fuel-exhaustion, ESS 86; both_no-offset·other, ESS 124) not estimable, not shown. Reference-289: module run 438c9e9 on eof-289-full (snap289-m0011).")
fig.text(0.01,0.006,"\n".join(textwrap.fill(p,215) for p in foot.split("\n")),fontsize=4.6,color=META_GREY,va="bottom",ha="left")
FIG=WS/"hydroacoustics-search-windows-next-run-b-standin"
fig.savefig(str(FIG)+".png",dpi=300); fig.savefig(str(FIG)+".pdf")
r_=fig.canvas.get_renderer()
T=[(t,t.get_window_extent(r_)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
print([(a.get_text()[:25],b.get_text()[:25]) for i,(a,ba) in enumerate(T) for b,bb in T[i+1:] if ba.overlaps(bb)])