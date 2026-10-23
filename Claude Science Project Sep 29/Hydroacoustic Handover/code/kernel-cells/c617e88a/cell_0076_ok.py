src2=src.replace('axs[0,1].legend(hd,','fig.legend(hd,').replace('frameon=False,fontsize=6,loc="lower left")','frameon=False,fontsize=6,loc="lower center",ncol=3,bbox_to_anchor=(0.53,0.205))')
src2=src2.replace('bottom=0.28','bottom=0.31')
exec(src2); fig=power_fig(p,"r600-bto-only","00:19 R600 BTO Only")