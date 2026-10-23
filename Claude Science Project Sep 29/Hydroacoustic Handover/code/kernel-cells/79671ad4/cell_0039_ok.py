FOOT_B=("(i) Plain: The number in each cell shows how much the ship reports, and the later failure of other ships to hear the signal again, change the odds that the "
        "aircraft recorders were on the sea floor there. A value below 1 makes that less likely. A value above 1 makes it more likely. We do not use a flight-path estimate here.\n"
        "(ii) Technical: B_H = P(contacts 4-5 Apr, no reacquisition | recorders within 2 km) / P(same | no recorders), shared nuisance parameters marginalised; "
        "first-principles sonar calibration (A); f = P(false 37.5-kHz-like contact in a listening day); q = product of miss probabilities of HMS Echo (6, 8 Apr), the submarine and sonobuoys "
        "given a transmitting beacon; battery failure by day 29-31 0.05-0.3. Prior-free; no 00:19 option; physics provisional; Ocean Shield's towed locator did not work at this site.")
fcent=np.sqrt(f_edges[:-1]*f_edges[1:])
fig,axs=plt.subplots(1,2,figsize=(7.2,3.5),gridspec_kw={"width_ratios":[1.25,1],"wspace":0.45})
lg=np.log10(grid); vmax=np.abs(lg).max()
im=axs[0].imshow(lg,cmap="RdBu_r",vmin=-vmax,vmax=vmax,origin="lower",aspect="auto")
for i in range(grid.shape[0]):
    for j in range(grid.shape[1]):
        axs[0].text(j,i,f"{grid[i,j]:.2f}",ha="center",va="center",fontsize=6,color="k")
axs[0].set_xticks(range(len(fcent)),[f"{f_edges[j]:g}-{f_edges[j+1]:g}" for j in range(len(fcent))],rotation=35,ha="right")
axs[0].set_yticks(range(len(q_vals)),[f"{q:g}" for q in q_vals])
axs[0].set_xlabel("False-contact probability per listening day"); axs[0].set_ylabel("Joint miss probability of the follow-up searches")
cb=fig.colorbar(im,ax=axs[0],fraction=0.05,pad=0.02); cb.set_label("log10 Bayes factor (0 = no information)")
# decomposition per calibration
names=[("A","first principles"),("C","ATSB favourable"),("B","maker's range")]
y=np.arange(3)
for k,(c,nm) in enumerate(names):
    rr=res[c]
    axs[1].plot([rr["B_H_contacts_only"]],[k+0.18],"o",color="0.55",ms=4)
    axs[1].plot([rr["B_H_reacq_only"]],[k],"s",color="0.55",ms=4,mfc="white")
    lo,mid,hi=rr["B_conditional_pct_5_50_95"]
    axs[1].plot([lo,hi],[k-0.18,k-0.18],color="k",lw=1); axs[1].plot([rr["B_H_marginal"]],[k-0.18],"D",color="k",ms=4)
axs[1].set_yticks(y,[n for _,n in names]); axs[1].set_xscale("log"); axs[1].axvline(1,color="0.3",lw=0.6)
axs[1].set_xlim(0.2,4); axs[1].set_xticks([0.25,0.5,1,2,4],["0.25","0.5","1","2","4"])
axs[1].set_xlabel("Bayes factor for recorders within 2 km")
from matplotlib.lines import Line2D
h=[Line2D([],[],marker="D",color="k",lw=1,ms=4,label="all evidence (5-95 % range)"),
   Line2D([],[],marker="o",color="0.55",lw=0,ms=4,label="ship contacts only"),
   Line2D([],[],marker="s",color="0.55",mfc="white",lw=0,ms=4,label="follow-up misses only")]
axs[1].legend(handles=h,frameon=False,fontsize=6,loc="upper right",bbox_to_anchor=(1.0,1.18))
axs[1].set_ylim(-0.6,2.6)
panel_letter(axs[0],"a"); panel_letter(axs[1],"b")
fig.suptitle("The contacts carry little weight; the failed follow-ups weakly disfavour recorders at the site",x=0.06,ha="left",fontsize=8)
fig.text(0.01,-0.04,FOOT_B,fontsize=6,va="top",wrap=True)
fig.subplots_adjust(top=0.84,bottom=0.22,left=0.1,right=0.98)
fig.savefig(f"{OUTD}/haixun-bayes-factor-sensitivity.png",dpi=300,bbox_inches="tight")
plt.close(fig)