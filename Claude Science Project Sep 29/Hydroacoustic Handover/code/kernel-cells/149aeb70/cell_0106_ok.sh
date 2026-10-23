cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/149aeb70-e4ae-4829-a477-5c291fc000a5" && python3 - <<'PY'
p="hydro-kadri-northern-conditional.md"; s=open(p).read()
old="""- **Our own impacts do reach it, thinly.** Of the latest run's draw, 0.37 per cent lies within 100 km
  of the crossing, 1.19 per cent within 200 km and 2.31 per cent within 400 km."""
new="""- **Our own impacts do reach it, thinly.** Of the run I dive draw, 0.36 per cent lies within 100 km
  of the crossing, 1.21 per cent within 200 km and 2.31 per cent within 400 km. Run I gives
  0.37, 1.19 and 2.28 per cent for the same three radii."""
assert old in s
s=s.replace(old,new); open(p,"w").write(s); print("patched")
PY