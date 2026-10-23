cd /Users/pete/Downloads/mh370-exchange; ls -la pleiades/run-j | head -30; echo; ls core/run-j | head; ls core/run-j/* | head -40; python - <<'E'
import json
d=json.load(open('composer/run-j-views-v3.2/views-v3-run-j.json'))
print(list(d.keys())[:40])
for k in d:
    if 'grid' in k.lower() or 'map' in k.lower(): print(k, str(d[k])[:600])
E