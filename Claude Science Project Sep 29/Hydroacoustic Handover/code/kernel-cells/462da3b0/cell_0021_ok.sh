set -e; WS=/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/462da3b0-2381-4cf6-84db-fe178606bed4; cd $WS/repo; E="Claude Science Project Sep 29/engine"
mkdir -p $WS/stage/hydro-438c9e9 $WS/stage/eof-15ba915
git archive 438c9e9 "$E/hypotheses/hydroacoustics/prepare/search_windows.py" "$E/hypotheses/hydroacoustics/data/stations.csv" "$E/hypotheses/hydroacoustics/data/ocean_paths/request.json" | tar -x -C $WS/stage/hydro-438c9e9
git archive 15ba915 "$E/hypotheses/end-of-flight/smoke" "$E/data/satcom-observations.csv" | tar -x -C $WS/stage/eof-15ba915
shasum -a 256 $WS/stage/hydro-438c9e9/"$E"/hypotheses/hydroacoustics/prepare/search_windows.py $WS/stage/eof-15ba915/"$E"/hypotheses/end-of-flight/smoke/displacement_hist.py
MW=/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/d74bf70e-a424-46a9-8149-902d027e782a/hydro-wt/"$E"/hypotheses/hydroacoustics
shasum -a 256 "$MW/prepare/search_windows.py" "$MW/data/stations.csv" $WS/stage/hydro-438c9e9/"$E"/hypotheses/hydroacoustics/data/stations.csv
N=/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run
for s in next-free next-repro-radar next-descent-climb next-routes; do for k in 1 2 3 4; do (cd $N/$s/seed-$k && grep -v impacts.npy SHA256SUMS | shasum -a 256 -c --quiet && echo "$s/$k meta ok"); done; done 2>&1 | tail -16
python3 -c "
import json; m=json.load(open('$N/next-free/seed-1/run.json')); print(m.get('code_revision'), len(m['impact_columns']), [c for c in m['impact_columns'] if c in ('unix_s','latitude_deg','longitude_deg')]); print(m['config_paths'])"