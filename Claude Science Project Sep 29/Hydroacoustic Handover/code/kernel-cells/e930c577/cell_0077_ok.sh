cd leg; python -c "
import json; m=json.load(open('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1/run.json')); print(json.dumps(m['compact'])[:600])"; python - <<'E'
s=open('analyse_L.py').read()
s=s.replace('T0_COMPACT = float(json.load(open(sys.argv[3]))["T0"]) if len(sys.argv) > 3 else None;','T0_COMPACT = 1394236800.0;   # compact_impacts.T0 (end-of-flight 5d060f0): impacts32 times are seconds after 00:00 UTC 8 Mar; checked against the restored flame-out times')
open('analyse_L.py','w').write(s)
E
cd ..; python leg/analyse_L.py leg/scan_dev leg/out_dev 2>&1 | grep -v -i -E 'proj|ca_bundle' | python -c "
import sys; s=sys.stdin.read(); i=s.find('{\"T|core'); print(s[i:i+1300])"; python -c "
import json; r=json.load(open('leg/out_dev/L_regions.json'))['regions']; print(r['D2|strip']['t_impact_q'], r['D2|strip']['mass'])"