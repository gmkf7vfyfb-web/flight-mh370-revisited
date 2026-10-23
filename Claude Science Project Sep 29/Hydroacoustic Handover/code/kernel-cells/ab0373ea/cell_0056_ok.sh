OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
# acceptance file for note_fill: build from main rows + timing + accept38p5
python - <<'EOF'
import pandas as pd, numpy as np
OUT="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid"
rows=pd.concat([pd.read_csv(f"{OUT}/ram_grid_rows.csv",on_bad_lines="skip"),pd.read_csv(f"{OUT}/accept38p5/ram_grid_rows_timing.csv")]).drop_duplicates(["tag","fc_hz"])
sub=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/ram-subset/ram_subset.csv"); sub=sub[sub.tag.str.split("-").str[-1].isin(["3315","3376","3274","3275","3250"])]
m=sub.merge(rows[rows.status=="ok"][["tag","fc_hz","tl_ram_db","tl_kraken_noabs_db"]],on=["tag","fc_hz"],suffixes=("_subset","_grid"))
m["diff_ram_db"]=m.tl_ram_db_grid-m.tl_ram_db_subset; m["diff_kraken_db"]=m.tl_kraken_noabs_db_grid-m.tl_kraken_noabs_db_subset; m["pass_0p5"]=m.diff_ram_db.abs()<=0.5
m.to_csv(f"{OUT}/acceptance_check.csv",index=False); print(m[["tag","fc_hz","tl_ram_db_subset","tl_ram_db_grid","diff_ram_db","diff_kraken_db","pass_0p5"]].round(4).to_string(index=False))
EOF
cp $OUT/wall_timing.json /tmp/interim/ 2>/dev/null; [ -f $OUT/wall.json ] || echo '{"interim": true}' > $OUT/wall.json
python note_fill.py /tmp/interim/tables 2>&1 | grep -v Warning