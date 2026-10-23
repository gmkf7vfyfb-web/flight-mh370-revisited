cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
sed -n 140,400p prepare/weak_signal/methods.py | grep -n "^def \|^METHODS\|^    \"M" | head -20
grep -n "def window_max" -A8 prepare/weak_signal/methods.py | head -24
head -3 results-data/windows_run_j/request_windows.csv; grep -c . results-data/windows_run_j/request_windows.csv
grep "3315\|3275" results-data/windows_run_j/request_windows.csv | head -8
python -c "
import sys; sys.path.insert(0,'prepare'); import imos_preregistration as P; m=P.parse_meta(); print({k:(v['sens_db'],v['cal_file'],v.get('lat'),v.get('lon')) for k,v in m.items()})"