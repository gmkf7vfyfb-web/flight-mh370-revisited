P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
cd "$P" && python - <<'EOF'
import pathlib
p=pathlib.Path("run_j_levels.py"); s=p.read_text()
s=s.replace('''    a = ap.parse_args()
    global IMOS_TL_FILE, KEYS, RECEIVERS
    IMOS_TL_FILE''','''    a = ap.parse_args()
    IMOS_TL_FILE''')
s=s.replace('''def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["draw", "supplement", "noise", "levels", "check"])''','''def main():
    global IMOS_TL_FILE, KEYS, RECEIVERS
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["draw", "supplement", "noise", "levels", "check"])''')
p.write_text(s)
EOF
python -m py_compile run_j_levels.py tl_grid_table.py imos_ram_grid.py && echo compiled
# quick inspection of the plan
python - <<'EOF'
import sys; sys.argv=["x"]
import imos_ram_grid as G
P,rx=G.plan(1.0,[-30,0,30],"/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables")
print(P.run.sum(), P.groupby(["priority"]).run.sum().to_dict()); print(P[P.run].groupby("logger").size().to_dict()); print(rx)
EOF
uptime