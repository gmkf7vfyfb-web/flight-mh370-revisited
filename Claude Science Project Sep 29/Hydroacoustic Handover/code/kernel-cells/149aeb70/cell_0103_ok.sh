cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/149aeb70-e4ae-4829-a477-5c291fc000a5" && python3 - <<'PY'
p="hydro-kadri-northern-conditional.md"; s=open(p).read()
old="""   correction. Do not fold it into the existing pair test; state the new time-difference span,
   1,390 to 1,710 s, which covers arc latitudes 28.9 S to 22 S."""
new="""   correction. Do not fold it into the existing pair test; state the new time-difference span,
   **1,346 to 1,710 s**, which covers arc latitudes 28.9 S to 22 S. The lower bound is set to abut
   the existing test's upper bound of 1,347 s so that the two searches are contiguous: on this arc
   1,346 s is 28.9 S and 1,710 s is 22.0 S. An earlier draft of this note gave the lower bound as
   1,390 s, which is 28.0 S and would have left 28.9 S to 28.0 S searched by neither test."""
assert old in s
s=s.replace(old,new); open(p,"w").write(s); print("patched")
PY