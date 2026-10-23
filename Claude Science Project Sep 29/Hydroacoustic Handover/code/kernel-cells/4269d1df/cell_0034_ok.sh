cd "repo/Claude Science Project Sep 29/results/drift-runj-2026-10-17"; python3 -c "
import json
a=json.load(open('aus160-both.json')); print(list(a['cells']['D0'])); print(a['models'])
"; sed -n 1,74p apply_australia.py; sed -n 1,40p analyze_runj.py