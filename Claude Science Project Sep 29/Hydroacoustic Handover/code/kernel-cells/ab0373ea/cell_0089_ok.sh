P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid; TG=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables
cd "$P" && python - <<'EOF'
import pathlib
p=pathlib.Path("imos_ram_grid_charts.py"); s=p.read_text()
s=s.replace('offset 0 nodes, 10/20/40 Hz, log-f interpolation clamped (5–8 Hz take the 10 Hz Δ), 10 m source','offset 0 nodes, 5/8/10/20/40 Hz (addendum of 22 Oct: 5 and 8 Hz added; 31.5 Hz interpolated in log f), 10 m source')
s=s.replace('for fc in BANDS:\n            for tab, ls, lab','for fc in BANDS:\n            for tab, ls, lab')
p.write_text(s)
EOF
R="$OLDPWD/repo/Claude Science Project Sep 29/results"
PYTHONPATH=. python imos_ram_grid_charts.py $TG $TG /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/tables/detectable.csv $OUT/levels-rerun-v2/tables/detectable.csv "$R/hydroacoustics-imos-ram-grid-old-vs-new.png" --commit "cc943df + addendum" 2>&1 | grep -v Warning | tail -1
cd "$OLDPWD"; sed -n 1,12p note_tables_v2.txt; grep -A8 "LEVELS old" note_tables_v2.txt; grep -A7 "power screen" note_tables_v2.txt | head -8; grep "rows ok" note_tables_v2.txt; grep -A6 "rows covered per logger" note_tables_v2.txt
python - <<'EOF'
import pandas as pd
d=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_ram_minus_kraken_arc.csv",dtype={"logger":str}); d0=d[(d.offset_nm==0)&(d.fc_hz<=8)]
print(d0.groupby(["logger","fc_hz"]).ram_minus_kraken_db.describe(percentiles=[.1,.5,.9])[["count","10%","50%","90%"]].round(1).to_string())
OUT="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid"
b1=pd.read_csv(f"{OUT}/levels-rerun/tables/band_levels_eta1.csv",dtype={"receiver":str}); b2=pd.read_csv(f"{OUT}/levels-rerun-v2/tables/band_levels_eta1.csv",dtype={"receiver":str})
bb=b1.merge(b2,on=["receiver","fc_hz","chain"],suffixes=("_v1","_v2")); bb["d"]=bb.q50_v2-bb.q50_v1; print(bb[bb.fc_hz<=8].pivot(index="receiver",columns="fc_hz",values="d").round(1))
EOF