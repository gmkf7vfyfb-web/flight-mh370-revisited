cd gfx && python - <<'E'
s=open('charts_levels.py').read()
s=s.replace('ax.set_yticks(range(4)); ax.set_yticklabels(["D0′", "D2", "D3", "D4"]); ax.invert_yaxis(); ax.set_xlim(0, 1.12)','ax.set_yticks(range(4)); ax.set_yticklabels([]); ax.invert_yaxis(); ax.set_xlim(0, 1.12)')
s=s.replace('ax = fig.add_axes([pos[5][0] + 0.05, pos[5][1], wd - 0.05, hgt])','ax = fig.add_axes([pos[5][0] - 0.02, pos[5][1], wd + 0.02, hgt])')
open('charts_levels.py','w').write(s)
E