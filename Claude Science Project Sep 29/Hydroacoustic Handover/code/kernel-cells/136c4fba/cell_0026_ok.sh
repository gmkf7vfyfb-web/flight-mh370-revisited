cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -n '/^def template/,/^def main/p' h08s_shot_outliers.py
echo "=== consts ==="; sed -n 70,96p h08s_shot_outliers.py
echo "=== kadri_table1_test DAY0/secs ==="; grep -n "DAY0\|^def secs" kadri_table1_test.py | head
echo "=== imos_preregistration: IMOS, clock_err ==="; grep -n "^IMOS\|^def clock_err\|^FS_D" imos_preregistration.py imos_noise.py | head