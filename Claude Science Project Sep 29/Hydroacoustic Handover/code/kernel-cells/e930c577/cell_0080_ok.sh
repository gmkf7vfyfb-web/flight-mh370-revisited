cd leg; python - <<'E'
s=open('analyse_L.py').read()
s=s.replace('DAY0 = 1394236800.0; T0_COMPACT = 1394236800.0;   # compact_impacts.T0 (end-of-flight 5d060f0): impacts32 times are seconds after 00:00 UTC 8 Mar; checked against the restored flame-out times T_OBS','# compact_impacts.T0 (end-of-flight 5d060f0): impacts32 times are seconds after 00:00 UTC 8 Mar; checked against restored flame-out times\nDAY0 = 1394236800.0; T0_COMPACT = 1394236800.0; T_OBS')
open('analyse_L.py','w').write(s)
E
sed -n 8,11p analyse_L.py; cd ..; python leg/analyse_L.py leg/scan_dev leg/out_dev > leg/out_dev/log.txt 2>&1; tail -3 leg/out_dev/log.txt | cut -c1-300; python -c "
import json; q=json.load(open('leg/out_dev/q2_crosscheck.json')); print({k:(None if v['log10_B'] is None else round(v['log10_B'],2), round(v['ess_wL'],1), v['impact_q'], v['lat_q']) for k,v in q.items() if 'D2' in k or 'D5' in k})"