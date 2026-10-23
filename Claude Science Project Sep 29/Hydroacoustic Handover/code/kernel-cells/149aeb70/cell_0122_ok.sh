cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/149aeb70-e4ae-4829-a477-5c291fc000a5" && python3 - <<'PY'
p="make_h08s_fig.py"; s=open(p).read()
old='"The pre-registered H01W x H08S pair span (dt 856-1,347 s from 00:52:03) ends "\n        "at 01:14:29, leaving 21 of the 107 cycles unsearched.'
new='"The pre-registered H01W x H08S pair span is dt 856-1,347 s from 00:52:03 and the largest pair "\n        "actually tested is 1,346 s, so the search stops at 01:14:29, leaving 21 of the 107 cycles unsearched.'
assert old in s, "pattern not found"
s=s.replace(old,new); open(p,"w").write(s); print("patched")
PY