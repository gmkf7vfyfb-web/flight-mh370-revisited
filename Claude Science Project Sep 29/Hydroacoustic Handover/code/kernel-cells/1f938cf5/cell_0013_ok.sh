cd ~/Downloads/mh370-exchange/end-of-flight/run-j/; ls run-j-waypoints | head -5; ls run-j-waypoints/seed-1; cat run-j-waypoints/seed-1/COLUMNS.txt 2>/dev/null | head -60; ls summary | head -30
python3 -c "
import json;d=json.load(open('run-j-waypoints/seed-1/run.json'));print(list(d.keys()));
for k,v in d.items():
  s=json.dumps(v); print(k, s[:300])
"