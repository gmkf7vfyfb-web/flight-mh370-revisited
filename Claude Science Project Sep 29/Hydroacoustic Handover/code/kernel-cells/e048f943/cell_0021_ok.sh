cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics
sed -n 40,154p prepare/imos_noise.py
echo ----
head -5 data/imos/recordings.csv; cut -d, -f1,3 data/imos/recordings.csv | sort | uniq -c | sort -k2 | head -20
grep -n "def parse_meta\|def clock_err\|def sens\|def gain\|IMOS =\|^IMOS\|def calib" prepare/imos_preregistration.py | head