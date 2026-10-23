cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
echo "== results-data"; ls results-data | tr '\n' ' '; echo; ls results-data/windows_run_j
echo "== windows.csv head"; head -3 results-data/windows_run_j/windows.csv; wc -l results-data/windows_run_j/windows.csv
echo "== coverage.csv head"; head -2 results-data/windows_run_j/coverage.csv
echo "== data"; ls data; ls data/imos | head; head -3 data/imos/recordings.csv; wc -l data/imos/recordings.csv
echo "== weak_signal common/methods signatures"
grep -n "^def \|^class " prepare/weak_signal/common.py prepare/weak_signal/methods.py prepare/weak_signal/template.py prepare/weak_signal/bank.py prepare/weak_signal/run_kadri.py prepare/weak_signal/run_h08s.py
echo "== exchange"; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-weak-signal/ | head -30
echo "== imos inputs"; ls /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/ | head; du -sh /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/* 2>/dev/null | head
echo "== royer"; ls "../../../results/evidence-sweep-2026-10-17/"; ls "../../../results/" | grep -i "radar\|infra"