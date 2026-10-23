cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
python - <<'EOF'
p='eta_map.py'; s=open(p).read()
s=s.replace('    bmed = {rx: summ["bg_median_level_db"][rx] for rx in R.RECEIVERS}',
            '    bmed = {rx: summ["bg_median_level_db"][rx] + summ["abs_offset_db"][rx] for rx in R.RECEIVERS}   # absolute: dB re 1 uPa, 5-40 Hz, 1 s')
s=s.replace('"eta50": {}, "pd_any_at_anchor": {}', '"bg_median_abs_db_re_uPa": None, "eta50": {}, "pd_any_at_anchor": {}')
s=s.replace('    decades = [1e-8,', '    res["bg_median_abs_db_re_uPa"] = bmed\n    decades = [1e-8,')
open(p,'w').write(s)
EOF
grep -n "bmed = " eta_map.py
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection
OMP_NUM_THREADS=1 python eta_map.py $OUT/inputs $OUT/run $OUT/eta 2>&1 | grep -v Warning | tail -14