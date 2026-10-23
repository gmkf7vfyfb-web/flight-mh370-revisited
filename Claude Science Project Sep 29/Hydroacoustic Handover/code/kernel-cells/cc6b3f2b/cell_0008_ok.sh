cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
echo "--- imos_preregistration constants"; grep -n "^IMOS\|^FS\|^DAY0\|^STA\|^LTA\|^SOS_D1\|FS_D\s*=" prepare/imos_preregistration.py prepare/imos_detectors.py prepare/imos_noise.py | head
echo "--- bg manifest"; python -c "
import json;m=json.load(open('data/imos_background/MANIFEST.json'));print(type(m), list(m)[:10] if isinstance(m,dict) else len(m))
import itertools
if isinstance(m,dict):
    for k,v in list(m.items())[:3]: print(k, str(v)[:300])
"
echo "--- disk"; ls /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/ ; du -sh /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/* 2>/dev/null
for d in /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/*/; do echo $d; ls $d | head -3; done
echo "--- head of recordings.csv"; head -3 data/imos/recordings.csv
echo "--- results-data"; ls results-data; ls results-data/imos3* 2>/dev/null | head
echo "--- kadri traces"; export GIT_CONFIG_GLOBAL=/dev/null; git ls-tree -r --name-only origin/hypothesis/hydroacoustics | grep -i "figure9-vector-traces" | head -20
df -k /System/Volumes/Data | tail -1