cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6
H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
grep -i "H11\|wake" "$H/data/stations.csv" | head; echo ---
sed -n 1,80p "$H/prepare/f35a_eta_calibration.py"; echo ---; ls "$H/results-data/f35a_cal/"; ls /Users/pete/Downloads/mh370-ocean-data/gebco/grid/; cat /Users/pete/Downloads/mh370-ocean-data/gebco/grid/gebco_2026_nwpac.json; ls /Users/pete/Downloads/mh370-exchange/ocean-transport/paths-calibration/ | head