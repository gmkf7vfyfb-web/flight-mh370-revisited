cd gfx && python - <<'E'
s=open('charts_levels.py').read()
s=s.replace('top = 0.90; mh = 0.25; wd = 0.205\n    pos = [[0.055 + c * 0.228, top - mh, wd, mh] for c in range(4)]','top = 0.90; mh = 0.25; wd = 0.2\n    pos = [[0.05 + c * 0.222, top - mh, wd, mh] for c in range(4)]')
s=s.replace('cax = fig.add_axes([pos[3][0] + wd + 0.012, pos[3][1] + 0.05 * mh, 0.008, 0.9 * mh])','cax = fig.add_axes([pos[3][0] + wd + 0.006, pos[3][1] + 0.05 * mh, 0.008, 0.9 * mh])')
s=s.replace('"open marker: before the correction"], fontsize=6, frameon=False, loc="lower right")','"open marker: before the correction"], fontsize=6, frameon=False, loc="upper right")')
s=s.replace('ax.set_yticks(range(4)); ax.set_yticklabels([]); ax.invert_yaxis(); ax.set_xlim(0, 1.12)','ax.set_yticks(range(4)); ax.set_yticklabels([OPT[o].replace("both 00:19 frequencies, ", "both frequencies,\\n").replace("both 00:19 frequencies as", "both frequencies as\\n") for o in opts], fontsize=6.5); ax.invert_yaxis(); ax.set_xlim(0, 1.12)')
s=s.replace('pos_f = [0.64, b + 0.085, 0.30, pos_e[3]]','pos_f = [0.64, b + 0.085, 0.31, pos_e[3]]')
open('charts_levels.py','w').write(s)
E