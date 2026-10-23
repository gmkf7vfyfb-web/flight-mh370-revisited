cd gfx && python - <<'E'
s=open('charts_table.py').read()
s=s.replace('("G", "00:52:04.35", "01:12:49.3", "Tonight','("G", "00:52:04", "01:12:49", "Tonight')
s=s.replace('nl = [max(c.count("\\n") + 1 for c in cells) for cells in wrapped]; lh = avail / (sum(nl) + 0.9 * len(nl))','nl = [max(c.count("\\n") + 1 for c in cells) for cells in wrapped]; lh = 6.4 * 1.18 / 72 / fig.get_size_inches()[1]')
s=s.replace('fig = plt.figure(figsize=(16, 11.5))','fig = plt.figure(figsize=(16, 9.6))')
open('charts_table.py','w').write(s)
E