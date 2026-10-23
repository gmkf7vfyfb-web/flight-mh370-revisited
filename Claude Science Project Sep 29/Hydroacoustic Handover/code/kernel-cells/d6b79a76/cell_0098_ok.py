s=open(f'{OUTD}/README.md').read()
reps=[('209,197 (00:52:03) and 222,368 (00:54:30)','209,210 (00:52:03) and 222,410 (00:54:30)'),
('(6-sigma joint gate, s_b 1 deg: 209,197 rows for T, 222,368 for C)','(6-sigma joint gate, s_b 1 deg: 209,210 rows for T, 222,410 for C)'),
('acoustically compatible rows 209,197 (T) / 222,368 (C)','acoustically compatible rows 209,210 (T) / 222,410 (C)'),
('Haixun 01 is 28.5 km outside the arc and inside the 99 % region of every estimable-direction panel. That is a sensitivity check only.',
 'Haixun 01 is 28.5 km outside the arc. Its 0.05 deg cell (± 1 cell) lies in the 50 % region for D0 and D1 (00:52:03), in the 90 % region for the caption reading and for D2, in the 99 % region for D4, and outside the 99 % region for D3 and D5 (effective samples 1–6). This is a sensitivity check only; none of these maps is estimable.'),
('is 0.105 % / 0.255 % / 0.700 % / 1.20 %','is 0.105 % / 0.308 % / 0.700 % / 1.22 % (around X: 0.093 % / 0.294 % / 0.679 % / 1.19 %)'),
('maximum time aloft after final flame-out is about 37 min, there is no flight at all beyond about 01:42,','the longest time aloft after final flame-out among the stored rows is 37 min and the latest stored impact is 01:42.7 (stored rows = the locality, acoustically compatible and top-ranked rows, not the whole posterior);'),
('   Glide from FL350–FL400 at L/D about 17–20 lasts 20–30 min (Boeing performance data as used in end of flight\'s descent-idle-floor/round-3 laws: grade C here, not re-read in this leg).',
 '   A clean glide from FL350–FL400 lasts roughly 20–30 min (engineering estimate from a lift-to-drag ratio of about 17–20; not a sourced bound: grade C, not re-read in this leg).')]
for a,b in reps:
    assert a in s, a[:40]; s=s.replace(a,b)
open(f'{OUTD}/README.md','w').write(s); print('ok')