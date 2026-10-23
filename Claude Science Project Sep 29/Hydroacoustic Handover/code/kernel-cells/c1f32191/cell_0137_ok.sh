cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && S=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/stats-ramgrid-v2 && O=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated-v2 && mkdir -p $S/reduce && B11_STATS_ONLY=1 OMP_NUM_THREADS=1 python reduce.py $S $S/reduce 2>&1 | grep -v Warn | tail -1
python - <<'EOF'
import numpy as np
O="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated-v2"; S="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/stats-ramgrid-v2"
mx=0
for sd in ["run-j-free/seed-3","run-j-waypoints/seed-1","run-j-repro-radar/seed-2","run-j-descent-climb/seed-7"]:
    a=np.load(f"{O}/{sd}/acc.npz"); b=np.load(f"{S}/{sd}/acc.npz")
    for k in ["wL_a0.05","wPnd_a0.05","wLmarg_a0.05","half_wL_a0.05","wL_ims_a0.05","sum_w"]:
        mx=max(mx, float(np.max(np.abs(a[k]-b[k])/np.maximum(np.abs(b[k]),1e-300))))
print("max rel diff v2 product vs stats-v2 accumulators:", f"{mx:.2e}")
EOF
python addendum_tables.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/reduce $S/reduce > $S/reduce/addendum_tables.md 2>/dev/null
RES="../../../../../../../repo/Claude Science Project Sep 29/results"; python addendum_text.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/reduce $S/reduce $S/reduce/addendum_tables.md "$RES/hydroacoustics-composition-run-j.md" "module commits 8093d97 (A4 code), 50870c8 (v2 product + data), this commit; work e79bba2 (first addendum, numbers withdrawn), 037d154 (v2 addendum), this commit" 2>&1 | grep -v Warn
grep -o "Amplitude-weighted (A4c[^.]*\. " "$RES/hydroacoustics-composition-run-j.md" | head -1; grep -o "amplitude-weighted +[0-9.]* / +[0-9.]*°" "$RES/hydroacoustics-composition-run-j.md" | head -1
H="../../../results-data/composition_run_j"; cp $S/reduce/*.csv $S/reduce/*.json "$H/v2/" && cp $S/reduce/addendum_tables.md "$H/v2/addendum_tables.txt" && ls "$H/v2" | wc -l; date -u +%H:%MZ