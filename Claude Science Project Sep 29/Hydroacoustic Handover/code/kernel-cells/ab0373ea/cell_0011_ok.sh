P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
cd "$P" && python - <<'EOF'
import re,pathlib
p=pathlib.Path("tl_grid_table.py"); s=p.read_text()
s=s.replace('def load_table(table_dir, bands, src_depths, offset_nm=None, ridge_policy="keep"):',
 'def load_table(table_dir, bands, src_depths, offset_nm=None, ridge_policy="keep", imos_file="imos_tl_ramcorr_arc.csv"):')
s=s.replace('IMOS tables are RAM-corrected as the old file. offset_nm selects the arc line (nearest available offset)."""',
 'IMOS tables are RAM-corrected as the old file. offset_nm selects the arc line (nearest available offset).\n    imos_file (amendment, imos_ram_grid 23 Oct 2026): the IMOS table file name; `imos_tl_ram_arc.csv` = RAM along the grid (G-TL1)."""')
s=s.replace('imo = pd.read_csv(td / "imos_tl_ramcorr_arc.csv", dtype={"logger": str})','imo = pd.read_csv(td / imos_file, dtype={"logger": str})')
p.write_text(s)
p=pathlib.Path("run_j_levels.py"); s=p.read_text()
s=s.replace('''def tl_tables():
    import pandas as pd, tl_grid_table as TT
    xs, tabs = TT.load_table(RD / "tl_grid_run_j", BANDS, [Z_REF])''','''IMOS_TL_FILE = "imos_tl_ramcorr_arc.csv"   # amendment 2 (imos_ram_grid.py, 23 Oct 2026): --imos-tl-file swaps the IMOS table


def tl_tables():
    import pandas as pd, tl_grid_table as TT
    xs, tabs = TT.load_table(RD / "tl_grid_run_j", BANDS, [Z_REF], imos_file=IMOS_TL_FILE)''')
s=s.replace('''    ap.add_argument("--seeds", nargs="*"); ap.add_argument("--repo-out", default=str(RD / "levels_run_j"))
    a = ap.parse_args()''','''    ap.add_argument("--seeds", nargs="*"); ap.add_argument("--repo-out", default=str(RD / "levels_run_j"))
    ap.add_argument("--imos-tl-file", default=IMOS_TL_FILE, help="amendment 2: IMOS TL table file in results-data/tl_grid_run_j")
    ap.add_argument("--keys", nargs="*", help="amendment 2: restrict the levels run to these keys (e.g. D0/p0.5)")
    ap.add_argument("--receivers", nargs="*", help="amendment 2: restrict to these receivers (best-receiver table then covers them only)")
    a = ap.parse_args()
    global IMOS_TL_FILE, KEYS, RECEIVERS
    IMOS_TL_FILE = a.imos_tl_file
    if a.keys: KEYS = [k for k in KEYS if k in a.keys]
    if a.receivers: RECEIVERS = [r for r in RECEIVERS if r in a.receivers]''')
p.write_text(s)
EOF
python -c "import ast,sys;[ast.parse(open(f).read()) for f in ['run_j_levels.py','tl_grid_table.py','imos_ram_grid.py']];print('ok')"
grep -n "IMOS_TL_FILE\|global" run_j_levels.py | head
# amendment line in the docstring
python - <<'EOF'
import pathlib
p=pathlib.Path("run_j_levels.py"); s=p.read_text()
s=s.replace('''Usage (from prepare/, PYTHONPATH=.):''','''AMENDMENT 2 (23 Oct 2026, imos_ram_grid.py, G-TL1 closure; committed before the rerun): `--imos-tl-file` names the IMOS TL
  table inside results-data/tl_grid_run_j (default unchanged: imos_tl_ramcorr_arc.csv; the G-TL1 rerun uses
  imos_tl_ram_arc.csv), `--keys` and `--receivers` restrict the run (the G-TL1 rerun: D0/p0.5, the five IMOS loggers; its
  best-receiver table covers those five only and is not a replacement of the full one). No other rule changed.

Usage (from prepare/, PYTHONPATH=.):''',1)
p.write_text(s)
EOF
python -c "import ast;ast.parse(open('run_j_levels.py').read());print('ok2')"