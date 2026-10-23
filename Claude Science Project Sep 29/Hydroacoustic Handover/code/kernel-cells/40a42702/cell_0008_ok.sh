cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
ls prepare | tr '\n' ' '; echo; echo ---
ls -la prepare/weak_signal/ ; echo ---
ls results-data/ ; ls results-data/windows_run_j/ 2>/dev/null; echo ---
ls data/; head -3 data/imos/recordings.csv; echo ---
python -c "
import json;m=json.load(open('data/imos_background/MANIFEST.json'));print(type(m), list(m)[:10] if isinstance(m,dict) else len(m))
"
echo --- disk
ls /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/ | head; du -sh /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/* 2>/dev/null | head -20
ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/