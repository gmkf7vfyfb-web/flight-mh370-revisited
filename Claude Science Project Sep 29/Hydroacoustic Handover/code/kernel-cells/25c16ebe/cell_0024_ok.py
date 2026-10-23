import matplotlib as mpl, matplotlib.pyplot as plt
apply_figure_style(sizes=(9,8,7))
D = np.load("audit/figdata.npz")
fig = plt.figure(figsize=(11.2, 7.2))
gs = fig.add_gridspec(2, 3, hspace=0.42, wspace=0.30)
C_HELD, C_R600, C_BOTH = "#4A6FA5", "#C9A227", "#B3452C"

# (a) onset time, boundary spike
ax = fig.add_subplot(gs[0,0])
bins = np.linspace(640, 1800, 60)
for lab,wk,c in [("no 00:19 data used",D["w_none"],C_HELD),("00:19 R600 only",D["w_r600"],C_R600),("both 00:19 bursts",D["w_both"],C_BOTH)]:
    h,_ = np.histogram(D["t_onset"], bins=bins, weights=wk); h=h/h.sum()
    ax.step(bins[:-1], h, where="post", color=c, lw=1.6, label=lab)
ax.axvline(659, color="#333333", lw=1.1, ls=":")
ax.annotate("00:11 hand-off:\nearliest onset the\nsampler can reach",
            xy=(659,ax.get_ylim()[1]*0.78), xytext=(790,ax.get_ylim()[1]*0.92),
            arrowprops=dict(arrowstyle="-", lw=0.8, color="#333333"), fontsize=7, va="top")
ax.set_xticks([660,900,1200,1500,1800]); ax.set_xticklabels(["00:11","00:15","00:20","00:25","00:30"])
ax.set_xlabel("Start of the major descent (UTC)"); ax.set_ylabel("Probability per bin")
ax.set_title("All descents start at or after the hand-off"); ax.legend(frameon=False, fontsize=7, loc="center right")
panel_letter(ax,"a")

# (b) FPA vs speed joint coverage
ax = fig.add_subplot(gs[0,1])
m = D["w_none"]>0
ax.scatter(D["spd"][m][::40], D["fpa"][m][::40], s=1.5, alpha=0.08, c=C_HELD, lw=0, rasterized=True)
ax.set_yscale("log"); ax.set_xlabel("Speed at the sea surface (m/s)")
ax.set_ylabel("Flight-path angle below horizontal (deg)")
ax.set_title("Two separated arrival regimes"); ax.margins(0.04)
ax.annotate("shallow arrivals,\nditching-like", xy=(95,3.5), xytext=(150,1.6), fontsize=7,
            arrowprops=dict(arrowstyle="-", lw=0.8, color="#333333"))
ax.annotate("steep, high-energy\narrivals", xy=(320,45), xytext=(120,62), fontsize=7,
            arrowprops=dict(arrowstyle="-", lw=0.8, color="#333333"))
panel_letter(ax,"b")

# (c) vertical KE spread
ax = fig.add_subplot(gs[0,2])
for lab,wk,c in [("no 00:19 data used",D["w_none"],C_HELD),("both 00:19 bursts",D["w_both"],C_BOTH)]:
    v = np.log10(np.maximum(D["vke"],1e4)); b=np.linspace(4,10,60)
    h,_=np.histogram(v,bins=b,weights=wk); h=h/h.sum()
    ax.step(b[:-1],h,where="post",color=c,lw=1.6,label=lab)
ax.set_xlabel("Vertical kinetic energy at impact (J)")
ax.set_xticks([4,6,8,10]); ax.set_xticklabels(["10$^4$","10$^6$","10$^8$","10$^{10}$"])
ax.set_ylabel("Probability per bin"); ax.set_title("Impact severity spans six orders of magnitude")
ax.legend(frameon=False, fontsize=7, loc="upper left"); panel_letter(ax,"c")

# (d) ESS collapse
ax = fig.add_subplot(gs[1,0])
labs = ["no 00:19\ndata used","R600 BFO\nonly","R1200 BFO\nonly","both, start-up\noffset model","both, raw\nBFO"]
vals = [50966.1, 3982.9, 1433.4*0.142, 170.3, 38.8]
vals = [50966.1, 3982.9, 216.0, 170.3, 38.8]
cols_ = [C_HELD, C_R600, "#7F8C8D", "#8E6FA5", C_BOTH]
ax.scatter(range(5), vals, s=46, c=cols_, zorder=3)
for i,v in enumerate(vals): ax.plot([i,i],[1,v], color=META_GREY, lw=0.9, zorder=1)
ax.set_yscale("log"); ax.set_ylim(10, 2e5)
ax.set_xticks(range(5)); ax.set_xticklabels(labs, fontsize=7)
ax.set_ylabel("Effective sample size")
ax.axhline(1000, color="#B3452C", lw=1.0, ls="--")
ax.text(4.35, 1150, "1,000 gate", fontsize=7, ha="right", color="#B3452C")
ax.set_title("Evidence that discriminates descent also destroys the sample")
ax.annotate("39 of 100,000\ntrajectories", xy=(4,38.8), xytext=(2.6,15), fontsize=7,
            arrowprops=dict(arrowstyle="-", lw=0.8, color="#333333"))
panel_letter(ax,"d")

# (e) impact time
ax = fig.add_subplot(gs[1,1])
b = np.linspace(900, 3600, 70)
for lab,wk,c in [("no 00:19 data used",D["w_none"],C_HELD),("00:19 R600 only",D["w_r600"],C_R600),("both 00:19 bursts",D["w_both"],C_BOTH)]:
    h,_=np.histogram(D["t_impact"],bins=b,weights=wk); h=h/h.sum()
    ax.step(b[:-1],h,where="post",color=c,lw=1.6,label=lab)
ax.axvline(1177, color="#333333", lw=1.0, ls=":")
ax.text(1200, ax.get_ylim()[1]*0.93, "last transmission\n00:19:37", fontsize=7, va="top")
ax.set_xticks([900,1500,2100,2700,3300]); ax.set_xticklabels(["00:15","00:25","00:35","00:45","00:55"])
ax.set_xlabel("Time of sea-surface impact (UTC)"); ax.set_ylabel("Probability per bin")
ax.set_title("Impact time stays wide and is set by the evidence option")
ax.legend(frameon=False, fontsize=7, loc="upper right"); panel_letter(ax,"e")

# (f) bank point mass
ax = fig.add_subplot(gs[1,2])
bk = np.abs(D["bank"]); wn = D["w_none"]
share0 = wn[bk<1e-6].sum()/wn.sum()
b=np.linspace(0,90,46); h,_=np.histogram(bk[bk>=1e-6],bins=b,weights=wn[bk>=1e-6]); h=h/wn.sum()
ax.bar([0], [share0], width=2.0, color=C_BOTH, zorder=3)
ax.step(b[:-1],h,where="post",color=C_HELD,lw=1.6)
ax.set_xlabel("Bank angle at impact (deg)"); ax.set_ylabel("Probability")
ax.set_title("Half the weight carries exactly zero bank")
ax.annotate(f"{share0*100:.0f}% set to wings level\nby construction", xy=(2,share0), xytext=(22,share0*0.92),
            fontsize=7, arrowprops=dict(arrowstyle="-", lw=0.8, color="#333333"))
panel_letter(ax,"f")

fig.suptitle("End-of-flight module, current full sweep: what the impact ensemble covers and where it is thin", fontsize=10, y=0.985)
fig.text(0.5, 0.005,
 "Source: run-i-dive, waypoints stratum, seed 1 (6.40 M simulated descents from 100,000 trajectories handed over at 00:11 UTC). Weights are the sampling weight times the likelihood of the "
 "named 00:19 option. Physics labelled provisional by the module: interim parametric pitch-down, no transonic drag rise, provisional turn and in-flight structural models. Core particle filter "
 "not converged. Panel (d) effective sample size is over the 100,000 parent trajectories of this stratum and seed.",
 ha="center", fontsize=6.0, color="#444444", wrap=True)
fig.savefig("eof-audit-coverage.png", dpi=200, bbox_inches="tight")
fig.savefig("eof-audit-coverage.pdf", bbox_inches="tight")
print("ok", share0)
