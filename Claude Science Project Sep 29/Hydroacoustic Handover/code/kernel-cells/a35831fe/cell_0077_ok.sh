cd review && python - <<'E'
f='hydroacoustics-take2-critical-review-2026-10-22.md'; t=open(f).read()
reps=[("At median energy it needs about 25 ×.","At the D0′ median energy there (about 1 GJ) it needs about 80 × (strained)."),
("is about 380 × the new anchor even at 12 GJ","is about 370 × the new anchor even at 12 GJ"),
("110 contain neither H08S nor Scott Reef; 27 of those pass all screens; 18 distinct after known-event removal","110 contain neither H08S nor Scott Reef; 27 rows (23 distinct pairs) pass all screens; 17 remain after known-event removal")]
for a,b in reps:
    assert t.count(a)==1,a; t=t.replace(a,b)
open(f,'w').write(t); print('ok')
E