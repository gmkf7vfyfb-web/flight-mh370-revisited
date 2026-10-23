WS=/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/462da3b0-2381-4cf6-84db-fe178606bed4; R="$WS/repo/Claude Science Project Sep 29/results"; D="$R/hydroacoustics-next-run-b-standin"
mkdir -p "$D"; for s in mixture next-free next-repro-radar next-descent-climb next-routes; do mkdir -p "$D/$s"; cp $WS/out/next-run-b/$s/* "$D/$s/"; done
cp $WS/standin_mixture.py "$D/"; cp $WS/hydroacoustics-search-windows-next-run-b-standin.png $WS/hydroacoustics-search-windows-next-run-b-standin.pdf "$R/"
du -sh "$D"; ls "$D"/*; shasum -a 256 $WS/standin_mixture.py