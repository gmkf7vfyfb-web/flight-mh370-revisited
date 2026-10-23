cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
python - <<'EOF'
s=open('charts.py').read()
s=s.replace('''"the rest point further north. The 306° row is uninformative on this impact set, not disfavoured as on the earlier stand-in.", y1=0.085)
         "(ii) Source posterior run J (waypoints''','''"the rest point further north. The 306° row is uninformative on this impact set, not disfavoured as on the earlier stand-in.",
         "(ii) Source posterior run J (waypoints''')
s=s.replace('''"bearings not reproducible from the published single channel. Caveats C1, C2; pre-registration a4cdab0; PREDICTIVE, NOT CALIBRATED.")''','''"bearings not reproducible from the published single channel. Caveats C1, C2; pre-registration a4cdab0; PREDICTIVE, NOT CALIBRATED.", y1=0.085)''')
open('charts.py','w').write(s)
EOF
python charts.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches "$PWD/../../../../../../../repo/Claude Science Project Sep 29/results" 2>&1 | tail -1