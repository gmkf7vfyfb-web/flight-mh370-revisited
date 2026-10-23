cd "./.tmp/repo/ISO Sept 28 Status/results/worktree-hydroacoustics/hydroacoustics"; python3 - <<'EOF'
import json
k=json.load(open('kadri-tests/kadri-tests.json'))
for r in k['timing'][9:]:
    print(r)
for r in k['loudness'][:1]: print(r.keys()); print(r)
m=k['measurement']
for key in m:
    if key!='panels': print('meas.',key, json.dumps(m[key])[:800])
for p in m['panels']:
    print(p['panel'],p['station'],p['start_utc'],p['d1_peaks'],[(t['time_utc'][11:19],t['bearing_deg'],t.get('rank_in_panel'),t.get('peak_pa'),t.get('snr_db')) for t in p['table1']])
    print('   other keys', [x for x in p if x not in ('panel','station','start_utc','d1_peaks','top_peaks','table1')], {x:p[x] for x in p if x not in ('panel','station','start_utc','d1_peaks','top_peaks','table1')})
EOF