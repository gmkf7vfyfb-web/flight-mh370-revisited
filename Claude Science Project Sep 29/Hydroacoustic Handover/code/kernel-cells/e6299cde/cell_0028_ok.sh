cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
ls results-data/imos2b; head -3 results-data/imos2b/*.csv 2>/dev/null | head -20
grep -n "def subsec" -A8 prepare/imos_detectors.py | head -14
grep -n "true_start\|clock_err\|parse_meta\|gain" prepare/imos_detectors.py | head -20
grep -n -i "gain\|dB re\|uPa\|calibration" prepare/imos_noise.py | head -20
head -3 results-data/imos1d/noise_bands.csv; grep -n "3376" results-data/imos1d/calibration_gain.csv