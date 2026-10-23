cd /Users/pete/Downloads/mh370-ocean-data/products; python -c "
import json
for d in ['hydro-paths-2001-10','hydro-paths-2001-10-ausseabed']:
    m=json.load(open(d+'/air9-H01W_meta.json')); print(d, {k:(v if len(str(v))<200 else str(v)[:200]) for k,v in m.items()})
    print(open(d+'/request.json').read()[:600])
"
head -3 hydro-paths-2001-10/air9-H01W_bathymetry.csv; head -3 hydro-paths-2001-10/air9-H01W_soundspeed.csv
sed -n '/^def build/,$p' "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/../../../../dev/null" 2>/dev/null
cd - >/dev/null; sed -n '/^def build/,$p' "repo/Claude Science Project Sep 29/results/hydroacoustics-audit/scripts/paths.py" | head -60; grep -n "GEBCO\|WOA\|Downloads" "repo/Claude Science Project Sep 29/results/hydroacoustics-audit/scripts/paths.py" | head