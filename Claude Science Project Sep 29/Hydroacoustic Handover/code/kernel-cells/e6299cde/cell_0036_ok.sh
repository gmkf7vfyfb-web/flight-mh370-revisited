cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
for p in a d; do head -2 data/kadri_fig9_digitised/kadri-2024-figure9-panel-$p-*.csv; done
grep -n "^FS\|^KD\|^DAY0\|^H01\|LAG" prepare/weak_signal/run_h08s.py | head; sed -n 82,140p prepare/weak_signal/run_h08s.py