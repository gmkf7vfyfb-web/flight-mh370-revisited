ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/graphics-2026-10-22 2>&1
H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
python -c "
import numpy as np
for lg in ['3376','3274','3250']:
  d=np.load('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/null/null_%s.npz'%lg); print(lg,{k:d[k].shape for k in d})
"
grep -n "PANEL_T0\|PANEL_FS\|PANEL_BAND\|^TAUS\|ENV_FS\|^FS \|^FS=\|WINDOW_S\|WARMUP\|def p_value\|LEVELS\|SCREEN_P" "$H/prepare/searches_run_j/preregistration.py" "$H/prepare/searches_run_j/common_rows.py" | head -20
grep -n "def header\|def parse_meta\|def clock_err" -A6 "$H/prepare/imos_preregistration.py" | head -50; grep -n "def read_volts\|def decimate" -A8 "$H/prepare/imos_noise.py" | head -30