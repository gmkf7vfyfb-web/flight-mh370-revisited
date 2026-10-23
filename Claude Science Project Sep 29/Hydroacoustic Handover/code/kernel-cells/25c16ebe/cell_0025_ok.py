axs = fig.axes
axs[3].set_title("Descent-discriminating evidence collapses the sample")
axs[3].set_xticklabels(["none","R600\nBFO","R1200\nBFO","both,\noffset","both,\nraw"], fontsize=7)
axs[4].set_title("Impact time stays wide")
axs[5].set_title("Half the weight at zero bank")
for a in (axs[3],axs[4],axs[5]): a.title.set_fontsize(9)
fig.savefig("eof-audit-coverage.png", dpi=200, bbox_inches="tight")
fig.savefig("eof-audit-coverage.pdf", bbox_inches="tight")
r = fig.canvas.get_renderer()
texts=[(t,t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
ov=[(a.get_text()[:22],b.get_text()[:22]) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb)]
print(len(ov), ov[:8])
