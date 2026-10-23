v = D["vke"]; wn=D["w_none"]
m = wn>0
print("vke min/max (wt>0):", f"{v[m].min():.3e}", f"{v[m].max():.3e}")
print("q01..q99:", [f"{x:.3e}" for x in wq(v,wn,(0.01,0.05,0.5,0.95,0.99))])
print("orders q05-q95:", np.log10(wq(v,wn,(0.95,))[0]/wq(v,wn,(0.05,))[0]))
axs[2].set_title("Impact severity spans four orders of magnitude")
fig.savefig("eof-audit-coverage.png", dpi=200, bbox_inches="tight"); fig.savefig("eof-audit-coverage.pdf", bbox_inches="tight")
print("ok")
