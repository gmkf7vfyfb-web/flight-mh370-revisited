FOOT_B=FOOT_B.replace("Ocean Shield's towed locator did not work at this site","Ocean Shield's towed locator was not used at this site")
fig,axs=plt.subplots(1,2,figsize=(7.4,3.6),gridspec_kw={"width_ratios":[1.3,1],"wspace":0.75})
im=axs[0].imshow(lg,cmap="RdBu_r",vmin=-vmax,vmax=vmax,origin="lower",aspect="auto")
for i in range(grid.shape[0]):
    for j in range(grid.shape[1]):
        axs[0].text(j,i,f"{grid[i,j]:.2f}",ha="center",va="center",fontsize=6,color="k")
axs[0].set_xticks(range(len(fcent)),[f"{f_edges[j]:g}-{f_edges[j+1]:g}" for j in range(len(fcent))],rotation=35,ha="right")
axs[0].set_yticks(range(len(q_vals)),[f"{q:g}" for q in q_vals])
axs[0].set_xlabel("False-contact probability per listening day"); axs[0].set_ylabel("Joint miss probability, follow-up searches")
cb=fig.colorbar(im,ax=axs[0],fraction=0.05,pad=0.03); cb.set_label("log10 Bayes factor")
for k,(c,nm) in enumerate(names):
    rr=res[c]
    axs[1].plot([rr["B_H_contacts_only"]],[k+0.2],"o",color="0.55",ms=4)
    axs[1].plot([rr["B_H_reacq_only"]],[k],"s",color="0.55",ms=4,mfc="white")
    lo,mid,hi=rr["B_conditional_pct_5_50_95"]
    axs[1].plot([lo,hi],[k-0.2,k-0.2],color="k",lw=1); axs[1].plot([rr["B_H_marginal"]],[k-0.2],"D",color="k",ms=4)
axs[1].set_yticks(y,[n for _,n in names]); axs[1].set_xscale("log"); axs[1].axvline(1,color="0.3",lw=0.6)
axs[1].set_xlim(0.2,4); axs[1].xaxis.set_minor_locator(mpl.ticker.NullLocator())
axs[1].set_xticks([0.25,0.5,1,2,4]); axs[1].set_xticklabels(["0.25","0.5","1","2","4"])
axs[1].set_xlabel("Bayes factor, recorders within 2 km")
axs[1].legend(handles=h,frameon=False,fontsize=6,loc="lower left",bbox_to_anchor=(0.0,1.0))
axs[1].set_ylim(-0.6,2.6)
panel_letter(axs[0],"a",x=-0.32); panel_letter(axs[1],"b",x=-0.55)
fig.suptitle("The contacts carry little weight; the failed follow-ups weakly disfavour recorders at the site",x=0.06,ha="left",fontsize=8)
fig.text(0.01,-0.04,FOOT_B,fontsize=6,va="top",wrap=True)
fig.subplots_adjust(top=0.80,bottom=0.22,left=0.12,right=0.98)
fig.savefig(f"{OUTD}/haixun-bayes-factor-sensitivity.png",dpi=300,bbox_inches="tight")
plt.close(fig)