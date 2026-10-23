cd repo/"Claude Science Project Sep 29/results/evidence-sweep-2026-10-17"
sed -n 296,300p research-radar-infrasound-ohasisbio.md | cut -c1-200
python -c "
import json;d=json.load(open('royer_table5.json'));print(list(d.keys()));[print(k,d[k]) for k in ['12','13','14','15'] if k in d]"
cd ../../../../hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; cat data/stations.csv | head -20
echo; df -k /System/Volumes/Data | tail -1; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/