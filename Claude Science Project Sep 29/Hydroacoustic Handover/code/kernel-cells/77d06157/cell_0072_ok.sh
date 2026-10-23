cd gfx && python - <<'E'
s=open('charts_table.py').read()
s=s.replace('cols = [("hypothesis", "Hypothesis and source", 0.17, 34), ("implied_position", "Implied position", 0.13, 26), ("implied_impact_utc", "Implied impact, UTC", 0.105, 20),\n            ("arrivals_utc", "Arrival(s), UTC", 0.105, 20), ("trace_assessment", "Our trace assessment (22 Oct searches)", 0.215, 44),\n            ("eta_needed", "Coupling needed", 0.10, 20), ("bearing", "Bearing consistency", 0.155, 31)]',
 'cols = [("hypothesis", "Hypothesis and source", 0.16, 0), ("implied_position", "Implied position", 0.125, 0), ("implied_impact_utc", "Implied impact, UTC", 0.10, 0),\n            ("arrivals_utc", "Arrival(s), UTC", 0.105, 0), ("trace_assessment", "Our trace assessment (22 Oct searches)", 0.235, 0),\n            ("eta_needed", "Coupling needed", 0.105, 0), ("bearing", "Bearing consistency", 0.165, 0)]\n    FS = 7.3; cols = [(k, h, w_, int(w_ * 16 / (FS * 0.52 / 72)) - 1) for k, h, w_, _ in cols]')
s=s.replace('lh = 6.4 * 1.18 / 72 / fig.get_size_inches()[1]','lh = FS * 1.18 / 72 / fig.get_size_inches()[1]')
s=s.replace('fig.text(x + 0.003, y, cell, fontsize=6.4, va="top"','fig.text(x + 0.003, y, cell, fontsize=FS, va="top"')
s=s.replace('fig = plt.figure(figsize=(16, 9.6))','fig = plt.figure(figsize=(16, 9.0))')
open('charts_table.py','w').write(s)
E