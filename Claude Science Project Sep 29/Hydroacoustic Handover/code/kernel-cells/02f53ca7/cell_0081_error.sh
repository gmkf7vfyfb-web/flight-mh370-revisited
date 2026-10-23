cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
OUT=../results-data/tl_recal_block9; DIG=../results-data/digitised/blackman-2004
python tl_recal_block9.py air7_v2 $OUT $DIG 2>&1 | cut -c1-230
echo "======= AIR1"; python tl_recal_block9.py air1 $OUT $DIG ../results-data/airgun_sites_confirm ../results-data/air9_ew0112