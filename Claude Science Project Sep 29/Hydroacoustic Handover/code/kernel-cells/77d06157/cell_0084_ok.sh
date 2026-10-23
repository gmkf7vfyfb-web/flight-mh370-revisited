cd gfx && python - <<'E'
s=open('charts_air9.py').read()
s=s.replace('dB per octave ({g.g_slope.lower()}); offset {g.level:+.1f} dB (not interpretable, see note)"','dB per octave ({g.g_slope.lower()});\\noffset {g.level:+.1f} dB (not interpretable: units differ, see note)"')
s=s.replace('"Received level (dB; measured: peak-based, predicted: spectrum level)"','"Received level (dB; the two curves use different units)"')
open('charts_air9.py','w').write(s)
E