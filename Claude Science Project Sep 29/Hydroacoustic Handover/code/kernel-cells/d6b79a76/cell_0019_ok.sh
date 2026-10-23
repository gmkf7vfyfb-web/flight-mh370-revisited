cd ~/Downloads/mh370-exchange/end-of-flight/run-j; grep -o "run-j-[a-z-]*=[0-9.e-]*" -r summary/*.log ../run-j/*/README.md 2>/dev/null | sort | uniq | head; grep -rho "0\.998[0-9]*" summary/*.json | sort | uniq -c | head; cat run-j-waypoints/README.md | head -40; python3 - <<'E'
import json
d=json.load(open('summary/table-0019-mixture.json'))
c=d['cells']['D0 total q=0.333 (C2 silent)']
print(c['seed_sd_ln_Z_by_stratum']); print(c['seed_ln_Z'][:2])
E
cat "$OLDPWD/repo/Claude Science Project Sep 29/results/drift-runj-2026-10-17/README.md" | grep -n "0.99\|P(family)\|stratum" | head