cd "hyd/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -n 1,70p kadri_table1_test.py | cut -c1-220
echo ======; grep -n "C_KM_S\|SD_C_KM_S\|BEARING_SD\|BEARING_NU\|PICK\|SD_T" synthetic_composer_test.py | head -20
echo ======; grep -rn "BEARING_MODELS" -A8 searches_run_j/*.py | head -30