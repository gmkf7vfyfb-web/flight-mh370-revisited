cd gfx && python - <<'E'
s=open('charts_time.py').read()
s=s.replace('''        if l99 not in ("", "None"): axb.axhline(float(l99), color=OPT_COL[opt], lw=0.7, ls="--", xmax=0.97)''','''        if l99 not in ("", "None"): axb.axhline(float(l99), color=OPT_COL[opt], lw=0.7, ls="--", xmax=0.97, label="99th-percentile northern latitude of the impacts (colours as in a)" if j == 0 else None)''')
open('charts_time.py','w').write(s)
E