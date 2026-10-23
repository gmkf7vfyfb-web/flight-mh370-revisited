cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/ram_check"; cat convergence.json | head -c 1200; echo; python -c "
import json; v=json.load(open('verdicts.json')); print({k:(str(v[k])[:200]) for k in v})"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid; grep paths $OUT/raw/passB.log | tail -1; date -u