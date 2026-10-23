cd /Users/pete/Downloads/mh370-exchange/end-of-flight
ls bin/scripts | head; ls run-j/ ; ls run-j/summary | head -30
python - <<'EOF'
import json
r=json.load(open('run-j/run-j-waypoints/seed-1/run.json')); print(json.dumps(r['compact'])[:1500]); print(r['code_revision'], r.get('source_run'))
EOF
find . -maxdepth 4 -name "compact_impacts.py" | head