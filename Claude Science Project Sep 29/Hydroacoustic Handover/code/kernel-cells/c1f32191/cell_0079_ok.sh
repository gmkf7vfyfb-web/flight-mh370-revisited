cd "repo/Claude Science Project Sep 29/results" && python - <<'EOF'
p="hydroacoustics-composition-run-j.md"; s=open(p).read()
s=s.replace("11.1 % of rows (D0′-weighted 7.4 % of mass) have no scored window at any gated receiver and carry 0.0.","11.1 % of rows have no scored window at any gated receiver and carry 0.0 (the weighted share was not computed).")
open(p,"w").write(s); print("7.4" in s)
EOF