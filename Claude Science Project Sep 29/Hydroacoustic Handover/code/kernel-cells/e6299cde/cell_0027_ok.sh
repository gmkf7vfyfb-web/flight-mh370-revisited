cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
python - <<'EOF'
import ast
src=open('prepare/imos_noise.py').read(); t=ast.parse(src)
for n in t.body:
    if isinstance(n,ast.FunctionDef) and n.name in ('read_volts','decimate','gain_db'):
        print(ast.get_source_segment(src,n)[:900]); print('---')
EOF
grep -n "^FS_D\|^FS\b\|^FS =" prepare/imos_noise.py prepare/imos_preregistration.py | head
head -3 results-data/imos1d/calibration_gain.csv; ls results-data/imos1d
awk -F, 'NR>1{print $1,$9}' data/imos/recordings.csv | sort | uniq -c
sed -n 19,80p prepare/weak_signal/run_h08s.py
grep -n "def parse_meta\|def clock_err\|def header" -A12 prepare/imos_preregistration.py | head -60