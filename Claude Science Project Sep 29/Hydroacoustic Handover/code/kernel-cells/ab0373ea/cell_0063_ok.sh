set -e
P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
TG=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables
ls $OUT/work 2>/dev/null | wc -l; rm -rf $OUT/work
python - <<'EOF'
import pandas as pd, json
OUT="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid"
d=pd.read_csv(f"{OUT}/ram_grid_rows.csv",on_bad_lines="skip"); n0=len(d); d=d.drop_duplicates(["tag","fc_hz"]); d.to_csv(f"{OUT}/ram_grid_rows.csv",index=False); print("rows",n0,len(d),d.status.value_counts().to_dict())
json.dump(dict(wall_s_total_run_segments="23:29-00:08 duplicate pair (83 jobs kept), 00:13-03:35 single run", procs=6, bands=[10.0,20.0,40.0], n_jobs_planned=759, n_done=int(len(d)), deadline_hard="2026-10-22T03:50", stopped="soft deadline 03:35 local (SIGINT)", timing=False, cpu_hours=round(d.wall_s.sum()/3600,1)), open(f"{OUT}/wall.json","w"), indent=1)
EOF
cd "$P"
PYTHONPATH=. python imos_ram_grid.py build $OUT $TG $TG 2>&1 | grep -v Warning | head -25
cp $TG/imos_tl_ram_arc.csv $TG/imos_ram_minus_kraken_arc.csv $TG/imos_tl_ram_coverage.csv $TG/imos_tl_ram_build.json ../results-data/tl_grid_run_j/
cp $OUT/acceptance_check.csv ../results-data/tl_grid_run_j/imos_ram_acceptance_check.csv; cp $OUT/wall.json ../results-data/tl_grid_run_j/imos_ram_wall.json
# offset-0 rows identical to the interim table?
python - <<'EOF'
import pandas as pd, numpy as np
a=pd.read_csv("/tmp/interim/tables/imos_tl_ram_arc.csv",dtype={"logger":str}); b=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_tl_ram_arc.csv",dtype={"logger":str})
a0,b0=a[a.offset_nm==0],b[b.offset_nm==0]; print("offset0 identical:", np.allclose(a0.tl_db.fillna(-1),b0.tl_db.fillna(-1)) and (a0.status.values==b0.status.values).all())
EOF
PYTHONPATH=. OMP_NUM_THREADS=2 python run_j_levels.py levels --out $OUT/levels-rerun --repo-out $OUT/levels-rerun/repo_copy --imos-tl-file imos_tl_ram_arc.csv --keys D0/p0.5 --receivers 3315 3376 3274 3275 3250 2>&1 | grep -v Warning | tail -1
mkdir -p ../results-data/imos_ram_grid; for f in detectable eta_50 band_levels_eta1 power_screen coverage; do cp $OUT/levels-rerun/tables/$f.csv ../results-data/imos_ram_grid/levels_rerun_$f.csv; done
cp $OUT/levels-rerun-sens-lowband-old/tables/detectable.csv ../results-data/imos_ram_grid/levels_rerun_sens_lowband_old_detectable.csv; cp $OUT/levels-rerun/run.json ../results-data/imos_ram_grid/levels_rerun_run.json
R="$OLDPWD/repo/Claude Science Project Sep 29/results"
PYTHONPATH=. python imos_ram_grid_charts.py $TG $TG /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/tables/detectable.csv $OUT/levels-rerun/tables/detectable.csv "$R/hydroacoustics-imos-ram-grid-old-vs-new.png" --commit 4920cc2 2>&1 | grep -v Warning | tail -1
cd "$OLDPWD"; python note_fill.py $TG 2>&1 | grep -v Warning > note_tables.txt; wc -l note_tables.txt; (cd $OUT && shasum -a 256 ram_grid_rows.csv plan.csv paths_meta.csv wall.json acceptance_check.csv levels-rerun/tables/*.csv > SHA256SUMS); du -sh $OUT; df -k /System/Volumes/Data | tail -1 | awk '{print $4/1048576 " GiB free"}'