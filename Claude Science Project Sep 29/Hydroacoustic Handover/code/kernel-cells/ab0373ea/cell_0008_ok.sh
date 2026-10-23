P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -n 189,217p "$P"/tl_grid_run_j.py; sed -n 1,30p "$P"/tl_grid_run_j.py | grep -n "SRC\|SHALLOW\|ARC_GRID\|IMS\s*=" ; grep -n "^SRC\|^SHALLOW_M\|^ARC_GRID\|^IMS\|^HERE\|^MODULE\|^RD" "$P"/tl_grid_run_j.py "$P"/tl_grid_table.py
grep -n "def build_profiles\|def node_profiles" -A3 "$P"/air9_tl_validation.py | head -20
python -c "import pyram,numba;print(pyram.__version__ if hasattr(pyram,'__version__') else 'pyram', numba.__version__)"
cat "/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/tables/detectable.csv" | python -c "
import pandas as pd,sys; d=pd.read_csv(sys.stdin,dtype={'receiver':str}); d=d[(d.key=='D0/p0.5')&d.receiver.isin(['3315','3376','3274','3275','3250'])&d.eta.isin([0.001,0.00021])]; print(d[['receiver','eta','frac_matched_filter','frac_baseline','snr_q50','blocked_mass']].to_string(index=False))"