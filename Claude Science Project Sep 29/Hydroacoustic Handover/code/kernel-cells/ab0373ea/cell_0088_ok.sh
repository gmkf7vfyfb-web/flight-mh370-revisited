set -e
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
TG=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables
for i in $(seq 1 40); do if grep -q '"n_jobs": 336' $OUT/wall.json 2>/dev/null; then break; fi; sleep 15; done
cat $OUT/wall.json | tr '\n' ' '; echo; grep -i "failed\|deadline" $OUT/run5_lowband_offsets.log | head -2
python - <<'EOF'
import pandas as pd, json
OUT="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid"
d=pd.read_csv(f"{OUT}/ram_grid_rows.csv",on_bad_lines="skip"); n0=len(d); d=d.drop_duplicates(["tag","fc_hz"]); d.to_csv(f"{OUT}/ram_grid_rows.csv",index=False)
print("rows",n0,len(d),d.status.value_counts().to_dict(), d.groupby("fc_hz").size().to_dict(), "cpu-h", round(d.wall_s.sum()/3600,1))
json.dump(dict(passes=["23:29-03:35 local: 10/20/40 Hz, 647 jobs (offset 0 complete, +-30 partial)","03:52-03:57: 5/8 Hz offset 0, 170 jobs","03:56-05:13: 10/20/40 Hz remaining +-30 NM, 112 jobs","05:14-~05:30: 5/8 Hz +-30 NM, 336 jobs"], procs=6, bands=[5.0,8.0,10.0,20.0,40.0], n_jobs_total=int(len(d)), failed=int((d.status!="ok").sum()), cpu_hours=round(d.wall_s.sum()/3600,1)), open(f"{OUT}/wall.json","w"), indent=1)
EOF
cd "$P"
PYTHONPATH=. python imos_ram_grid.py build $OUT $TG $TG 2>&1 | grep -v Warning | head -9
cp $TG/imos_tl_ram_arc.csv $TG/imos_ram_minus_kraken_arc.csv $TG/imos_tl_ram_coverage.csv $TG/imos_tl_ram_build.json ../results-data/tl_grid_run_j/; cp $OUT/wall.json ../results-data/tl_grid_run_j/imos_ram_wall.json
python - <<'EOF'
import pandas as pd, numpy as np
a=pd.read_csv("/tmp/interim2/tables/imos_tl_ram_arc.csv",dtype={"logger":str}); b=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_tl_ram_arc.csv",dtype={"logger":str})
a0,b0=a[a.offset_nm==0],b[b.offset_nm==0]; print("offset0 identical to interim2:", np.allclose(a0.tl_db.fillna(-1),b0.tl_db.fillna(-1)))
EOF
PYTHONPATH=. OMP_NUM_THREADS=2 python run_j_levels.py levels --out $OUT/levels-rerun-v2 --repo-out $OUT/levels-rerun-v2/repo_copy --imos-tl-file imos_tl_ram_arc.csv --keys D0/p0.5 --receivers 3315 3376 3274 3275 3250 2>&1 | grep -v Warning | tail -1
for f in detectable eta_50 band_levels_eta1 power_screen coverage; do cp $OUT/levels-rerun-v2/tables/$f.csv ../results-data/imos_ram_grid/levels_rerun_v2_$f.csv; done; cp $OUT/levels-rerun-v2/run.json ../results-data/imos_ram_grid/levels_rerun_v2_run.json
R="$OLDPWD/repo/Claude Science Project Sep 29/results"
PYTHONPATH=. python imos_ram_grid_charts.py $TG $TG /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/tables/detectable.csv $OUT/levels-rerun-v2/tables/detectable.csv "$R/hydroacoustics-imos-ram-grid-old-vs-new.png" --commit "cc943df + addendum" 2>&1 | grep -v Warning | tail -1
cd "$OLDPWD"; sed -i '' 's#OUT / "levels-rerun/tables#OUT / "levels-rerun-v2/tables#g' note_fill.py; python note_fill.py $TG 2>&1 | grep -v Warning > note_tables_v2.txt; (cd $OUT && shasum -a 256 ram_grid_rows.csv plan.csv paths_meta.csv wall.json acceptance_check.csv levels-rerun/tables/*.csv levels-rerun-v2/tables/*.csv > SHA256SUMS); du -sh $OUT; date