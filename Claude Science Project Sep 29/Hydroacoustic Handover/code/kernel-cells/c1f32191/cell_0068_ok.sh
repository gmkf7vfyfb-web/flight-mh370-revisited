cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
d=open("driver.py").read()
d=d.replace('''Rows {rows:,}; not_computed (NaN) {nc}; per-seed checks''','''Rows {rows:,}; not_computed (NaN) {nc}; the marginalised IMOS column (proposed default) is present for every seed; per-seed checks''')
d=d.replace('''Seeds with fewer than five columns (disk floor): {len(short)} {short}
''','''Seeds with fewer than five columns (another process held the disk below the 20 GiB floor during the run; the marginalised IMOS
column was written, the other four were not): {len(short)} {short}
TOP-UP RECIPE (when >= 22 GiB free): B11_TOPUP=1 python worker.py <stratum> <seed> <this dir>  then  python driver.py  (finaliser only).
''')
open("driver.py","w").write(d)
EOF
OMP_NUM_THREADS=1 python driver.py 4 2>&1 | grep -v Warn | tail -3; O=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated; ls $O | head; cat $O/READY; tail -2 $O/driver.log
du -sh $O; df -k /System/Volumes/Data | tail -1