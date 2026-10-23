cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
head -5 data/imos/recordings.csv; wc -l data/imos/recordings.csv
python - <<'EOF'
import csv,collections
rows=list(csv.DictReader(open('data/imos/recordings.csv')))
print(rows[0].keys())
by=collections.defaultdict(list)
for r in rows: by[r.get('logger') or r.get('site') or list(r.values())[0]].append(r)
for k,v in by.items(): print(k,len(v),v[0],v[-1])
EOF
echo ==== request.json
python -c "
import json;d=json.load(open('data/ocean_paths/request.json'));print([ (p['name'],p['a'],p['b']) for p in d['paths']][:12])"
echo ==== royer
R=../../../../../repo/"Claude Science Project Sep 29/results/evidence-sweep-2026-10-17"; ls "$R"; python -c "import json;print(json.dumps(json.load(open('$R/royer_table5.json')),indent=1)[:2500])"