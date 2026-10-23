export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null; cd hydro && git -c credential.helper= fetch -q origin hypothesis/hydroacoustics 2>/dev/null; git log --oneline -4 origin/hypothesis/hydroacoustics | cut -c1-120
git show origin/hypothesis/hydroacoustics:"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/tl_grid_table.py" > "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/tl_grid_table.py"
grep -n "def load_table" -A 6 "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/tl_grid_table.py" | head -12
ls "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/tl_grid_run_j/" | grep ram; git show origin/hypothesis/hydroacoustics --stat | head -5 | cut -c1-120
python - <<'EOF'
import pandas as pd
c=pd.read_csv("hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/searches_run_j/imos/imos_candidates.csv",dtype={"receiver":str})
m=c[(c.detector=="M1b")&(c.p<=0.05)&(c.receiver.isin(["3376","3315","3274","3275"]))]; print(m[["receiver","time_utc","p","excess_5_40_pa2s","eta_needed","tl_note"]].to_string())
EOF
uptime