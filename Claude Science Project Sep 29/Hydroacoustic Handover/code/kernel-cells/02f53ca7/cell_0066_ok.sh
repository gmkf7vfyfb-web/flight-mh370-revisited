cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import pandas as pd, numpy as np, json
D='../results-data/tl_recal_block9/'
R=pd.concat([pd.read_csv(D+'air7_ram.csv'),pd.read_csv(D+'air7_ram_ext.csv')]); C=pd.read_csv(D+'air7_corridor.csv').set_index('fc_hz')
a9=R[R.tag=='builder_air9_H01W'].set_index('fc_hz')
out={}
for tag in ('air7off+0_H01W','air7off+20_H01W','air7off+50_H01W'):
    r=R[R.tag==tag].set_index('fc_hz').sort_index(); d=r.tl_ram_db-a9.tl_ram_db.reindex(r.index); ex=d-C.dtl_obs_db.reindex(r.index)
    dk=r.tl_kraken_noabs_db-a9.tl_kraken_noabs_db.reindex(r.index)
    out[tag]=dict(ram_excess_by_band=ex.round(1).to_dict(), ram_excess_median=float(ex.median()), kraken_noabs_diff_median=float(dk.median()), ram_minus_kraken_on_path=(r.tl_ram_db-r.tl_kraken_noabs_db).round(1).to_dict())
out['air9_ram_minus_kraken']=(a9.tl_ram_db-a9.tl_kraken_noabs_db).round(1).to_dict()
json.dump(out,open(D+'air7_ram_summary.json','w'),indent=1); print(json.dumps(out,indent=1))
EOF
RES="$PWD/../../../../../../repo/Claude Science Project Sep 29/results"
python tl_recal_block9_charts.py ../results-data/tl_recal_block9 "$RES" "$RES/hydroacoustics-audit/data/air9_residuals.csv" | tail -1
ls ../results-data/digitised 2>/dev/null; git fetch -q origin hypothesis/hydroacoustics 2>/dev/null; git ls-tree -r --name-only origin/hypothesis/hydroacoustics | grep -i "digitised/\|brown" | head -5; ls -R /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-digitisation | head; date -u