cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/149aeb70-e4ae-4829-a477-5c291fc000a5" && python3 - <<'PY'
p="make_h08s_fig.py"; s=open(p).read()
old=('"shot_low 01:11:39 z=-4.17, 01:13:09 z=-4.91, 01:13:59 z=-3.16; all four are flagged coincident under the loose and "\n'
     '        "table1-gated conditions, none under strict. The pre-registered H01W x H08S pair span (dt 856-1,347 s from 00:52:03) ends "')
new=('"shot_low 01:11:39 z=-4.17, 01:13:09 z=-4.91, 01:13:59 z=-3.16. All four are flagged coincident under the loose and "\n'
     '        "table1-gated conditions; the 01:11:39 deficit is ALSO flagged under the strict condition, the other three are not. "\n'
     '        "The pre-registered H01W x H08S pair span (dt 856-1,347 s from 00:52:03) ends "')
assert old in s, "pattern not found"
s=s.replace(old,new); open(p,"w").write(s); print("patched")
PY