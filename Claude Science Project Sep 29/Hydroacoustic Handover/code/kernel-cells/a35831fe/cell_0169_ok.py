a="About one third of the 50 % red area mass is not on searched sea floor; in total 33 % of the impact probability is on sea floor that is not searched (49 % if the bearing error is 0.4 deg)."
b="14 % of the probability inside the 50 % red area is on sea floor that is not searched. In total, 33 % of the impact probability is on sea floor that is not searched (49 % if the bearing error is 0.4 deg)."
assert src2d.count(a)==1; src2e=src2d.replace(a,b)
a2="loc='lower right')"; assert src2e.count(a2)==1
src2e=src2e.replace(a2,"loc=('upper left' if k=='A' else 'lower right'),bbox_to_anchor=((1.01,1.0) if k=='A' else None))")
a3="linewidths=0.8,linestyles=[(0,(1,1.5))]"; assert src2e.count(a3)==1
src2e=src2e.replace(a3,"linewidths=1.1,linestyles=[(0,(1,1))]")
a4="Line2D([0],[0],color='#a50f15',lw=0.8,ls=(0,(1,1.5))"; assert src2e.count(a4)==1
src2e=src2e.replace(a4,"Line2D([0],[0],color='#a50f15',lw=1.1,ls=(0,(1,1))")
t_old='ax.set_title(f"Candidate {k}: impact point, searched seabed and sea-floor PDF (00:19 data held out)"'
assert src2e.count(t_old)==1
src2e=src2e.replace(t_old,'ax.set_title((f"Candidate {k}: impact location with bearing, timing and arc uncertainty, searched seabed (00:19 data held out)" if k=="A" else f"Candidate {k}: impact point, searched seabed and sea-floor PDF (00:19 data held out)")')
exec(src2e); fnA=chart2('A'); plt.close('all'); host.view_image(fnA)