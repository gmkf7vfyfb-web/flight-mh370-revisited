cd gfx && python - <<'E'
s=open('charts_levels.py').read()
s=s.replace('''    blocked = max(float(H[f"{st}/band{fc:g}_blocked"]) for fc in RL.BANDS)''','''    bl = {fc: float(H[f"{st}/band{fc:g}_blocked"]) for fc in RL.BANDS}; fcb = max(bl, key=bl.get); blocked = bl[fcb]''')
s=s.replace('''    if blocked > 0.005: lines.append(f"path blocked for {pct(blocked, 0)} of impacts")''','''    if blocked > 0.005: lines.append(f"no sound path (blocked) for up to {pct(blocked, 0)}" + ("\\n" if compact else " ") + f"of impacts ({fcb:g} Hz band); shapes = open paths")''')
open('charts_levels.py','w').write(s)
E
grep -n "no sound path" charts_levels.py