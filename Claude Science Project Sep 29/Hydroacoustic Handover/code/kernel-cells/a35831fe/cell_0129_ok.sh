cd cand && python - <<'E'
f='candidates-A-F-charts-note-2026-10-22.md'; t=open(f).read()
m={'e26922a1-feff-4e38-8adf-604b188adbee':'03e3638a-89a7-4466-a9db-3f2d3683c49d','a8d98ace-e48f-44e0-a03f-408b158cd6bc':'a391dd15-03d9-42b8-9bc7-3508b68b7aa4',
   '1db56eb8-0e53-4971-be05-f34288c78150':'619e2716-f15a-4a2b-a137-ed535b047ea1','a5cecfe7-d07d-4011-8998-1619f98b4828':'cf0a863d-35bc-409a-bbdd-68ef2bac4892',
   '01270481-b1a3-4ea6-83dd-00c4ab7276a2':'96a6262e-8629-47a3-99d9-26d8baffa714','f4b17aa7-e936-4c23-9001-35282e7c4bf4':'5aa7e664-e546-4f04-bb1a-15ad1ed5f5c9',
   'd51d2e74-229a-42d1-9e14-1383dc24ee90':'3d369b1b-0a16-41b3-afb6-088e184b4367'}
for a,b in m.items(): assert t.count(a)==1,a; t=t.replace(a,b)
open(f,'w').write(t); print('ok')
E