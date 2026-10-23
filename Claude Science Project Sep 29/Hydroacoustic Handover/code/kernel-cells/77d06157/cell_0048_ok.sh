cd gfx && python - <<'E'
s=open('charts_levels.py').read()
s=s.replace('f"detectable at the best station\\nη 0.001: ','f"detectable at the best station\\ncoupling 0.001: ').replace('f"η 0.00021: {pct(bb.loc[2.1e-4]','f"coupling 0.00021: {pct(bb.loc[2.1e-4]')
s=s.replace('cb.set_label(f"Signal-to-noise ratio at the best station, η = {eta_map:g} (dB)", fontsize=7)','cb.set_label(f"Signal-to-noise ratio at the best station,\\ncoupling efficiency {eta_map:g} (dB)", fontsize=7)')
s=s.replace('(η = 0.001)")','(coupling 0.001)")')
open('charts_levels.py','w').write(s)
E
grep -n "η" charts_levels.py | cut -c1-150