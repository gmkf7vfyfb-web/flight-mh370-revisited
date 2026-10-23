cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/windows_run_j"
python - <<'EOF'
import csv, json
ess=json.load(open('ess.json'))
for k,v in ess.items():
    print(k, 'ESS %.0f strata-only %.0f supp %.0f share %.3f'%(v['ess'],v['ess_strata_only'],v['ess_supplement'],v['supplement_share']),
          {f:'%.3f/%.0f'%(d['share'],d['ess']) for f,d in v['family'].items()}, {s:'%.4f'%x for s,x in v['strata_share'].items()})
rows=list(csv.DictReader(open('windows.csv')))
print('--- impact rows')
for r in rows:
    if r['receiver']=='impact': print(r['option'],r['p'],r['q0.5'],r['q5'],r['q50'],r['q95'],r['q99.5'],'lat99',r['lat99_north_deg'],'beyond',r['mass_beyond_grid'])
print('--- unconverged rows (SOFAR, p=0.5)')
for r in rows:
    if r['unconverged']=='1' and r['p']=='0.5': print(r['receiver'],r['option'],r['branch'],r['seed_spread_q0.5_s'],r['seed_spread_q99.5_s'])
print('--- coverage p=0.5 SOFAR')
for c in csv.DictReader(open('coverage.csv')):
    if c['p']=='0.5' and c['branch']=='SOFAR' and c['receiver'] in ('H01W','H08S','H08N','3315','3376','3274','3275','3250'): print(c['receiver'],c['option'],'%.3f'%float(c['held_fraction']),c['n_held_records'],c['held_seconds'])
EOF