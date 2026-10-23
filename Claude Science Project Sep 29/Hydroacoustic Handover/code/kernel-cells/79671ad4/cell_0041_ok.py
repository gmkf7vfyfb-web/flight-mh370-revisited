for a,l,xx in [(axs[0],"a",-0.33),(axs[1],"b",-0.6)]:
    a.text(xx,1.04,l,transform=a.transAxes,fontsize=9,fontweight="bold",va="bottom")
fig.suptitle("The contacts carry little weight; the failed follow-ups weakly disfavour recorders at the site",x=0.06,ha="left",fontsize=8)
fig.text(0.01,-0.04,FOOT_B,fontsize=6,va="top",wrap=True)
fig.subplots_adjust(top=0.80,bottom=0.22,left=0.12,right=0.98)
fig.savefig(f"{OUTD}/haixun-bayes-factor-sensitivity.png",dpi=300,bbox_inches="tight")
plt.close(fig)