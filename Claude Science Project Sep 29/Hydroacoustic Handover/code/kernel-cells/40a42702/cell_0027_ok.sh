cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
grep -n "^def " kraken_tl.py | head -30; grep -n "def write_env" -A6 kraken_tl.py | head -12; grep -n "def write_flp" -A4 kraken_tl.py | head -8
grep -n "sens_db\|cal_file" imos_preregistration.py | head -8
uptime; df -k /System/Volumes/Data | tail -1 | awk '{print $4/1048576 " GiB free"}'
ls ../results-data/weak_signal/templates/