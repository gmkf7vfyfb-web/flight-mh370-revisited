cd gfx && grep -c "pct(r.H01W_arrival_mass_D0, 3)" charts_kadri.py; python - <<'E'
s=open('common.py').read()
s=s.replace('decades; F-35A upper anchor 2.1e-4. No detection is claimed.")','decades; F-35A upper anchor eta = 2.1e-4 is provisional (from Brown 2026\'s quote of Metz 2023; re-derivation from Metz pending). "\n       "No detection is claimed.")')
open('common.py','w').write(s)
for f in ['charts_levels.py','charts_time.py','charts_kadri.py']:
    t=open(f).read()
    t=t.replace('(" (F-35A value)" if eta == ETA_F35A else "")','(" (F-35A value, provisional)" if eta == ETA_F35A else "")')
    t=t.replace('"coupling 0.00021 (F-35A), corrected"','"coupling 0.00021 (F-35A, provisional), corrected"')
    open(f,'w').write(t)
E
grep -n "provisional" common.py charts_levels.py | cut -c1-120