cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/149aeb70-e4ae-4829-a477-5c291fc000a5" && python3 - <<'PY'
a="run-i-loud-tail-estimability.md"; s=open(a).read()
s=s.replace("Every option has at least 746 effective parents there, and seven of the nine have more\nthan 10,000. There is no end-of-flight sampling problem standing in the way of the detectability work.",
 "Eight of the nine options have more than 2,000 effective parents there and seven have more than 10,000;\nthe ninth, `both/no-offset`, has 746. There is no end-of-flight sampling problem standing in the way of\nthe detectability work, with that one exception noted below.")
s=s.replace("- `both/no-offset` in the loud decile has 746 effective parents, just under the 1,000 threshold.\n  Report it at decile depth as marginal.",
 "- `both/no-offset` in the loud decile has 746 effective parents, BELOW the 1,000 threshold. It is not\n  estimable at loud-decile depth and must be reported as unconverged there, not as a result.")
open(a,"w").write(s)
b="hydro-next-run-priority-2026-10-13.md"; t=open(b).read()
t=t.replace("Two depth limits are declared instead: in the loud decile `both/no-offset` has 746\neffective parents, which is marginal, and at the top percentile neither of the two is estimable.",
 "Two depth limits are declared instead: in the loud decile `both/no-offset` has 746\neffective parents, below the 1,000 threshold, so it is not estimable at that depth; and at the top\npercentile neither of the two is estimable.")
open(b,"w").write(t)
print("marginal" in open(a).read(), "which is marginal" in open(b).read())
PY