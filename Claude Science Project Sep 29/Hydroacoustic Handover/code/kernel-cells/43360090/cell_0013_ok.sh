cd "./.tmp/repo/ISO Sept 28 Status/results/worktree-hydroacoustics/hydroacoustics"; python3 - <<'EOF'
import json
k=json.load(open('kadri-tests/kadri-tests.json'))
print(list(k.keys()))
for r in k['loudness']:
    print({x:r.get(x) for x in ['crash','station','range_km','kinetic_energy_mj','predicted_peak_pa_favourable','observed_peak_pa','implied_extra_loss_db','timing_offset_min','timing_consistent','distinct_in_figure','note']})
print('timing:')
for r in k['timing']:
    print(r['time_utc'][11:19], r['bearing_deg'], r['kadri_dt_min'], round(r['our_dt_min'],2) if r['our_dt_min'] is not None else None, r['residual_min'] if r['residual_min'] is None else round(r['residual_min'],2), round(r['arc_lat'],2) if r['arc_lat'] else None)
for key in k:
    if key not in ('timing','measurement','loudness'): print(key, json.dumps(k[key])[:1500])
m=k['measurement']
for key in m:
    if key!='panels': print('meas.',key, json.dumps(m[key])[:800])
for p in m['panels']:
    print(p['panel'],p['station'],p['start_utc'],p['d1_peaks'],[ (t['time_utc'][11:19],t['bearing_deg'],t.get('rank_in_panel'),t.get('peak_pa'),t.get('snr_db')) for t in p['table1']])
EOF
cat imos/earthquake-controls.json | python3 -c "import json,sys; [print(e['logger'],e['event'],e['distance_km'],{b:(v['s_max_db'],v['above_threshold']) for b,v in e['bands'].items()}) for e in json.load(sys.stdin)]"