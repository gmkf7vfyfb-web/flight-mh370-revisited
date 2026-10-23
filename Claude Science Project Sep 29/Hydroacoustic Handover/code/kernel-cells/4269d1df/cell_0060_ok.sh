cd scorer; python3 -c "
import json;d=json.load(open('compact-columns.json'));print(list(d)); print({k:(v if not isinstance(v,(list,dict)) or len(str(v))<400 else str(v)[:400]) for k,v in d.items()})
"; sed -n 14,22p compact_impacts.py; python3 -c "
import json;m=json.load(open('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1/run.json'));print(m.get('compact',{}).get('T0_unix_s'), m['compact'].get('time_columns'))"