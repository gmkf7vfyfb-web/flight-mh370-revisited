cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
OUT=../results-data/tl_recal_block9; EW=../results-data/air9_ew0112
RES="$PWD/../../../../../../repo/Claude Science Project Sep 29/results/hydroacoustics-audit/data/air9_residuals.csv"
python tl_recal_block9.py route1 "$RES" $EW $OUT 2>&1 | tail -80
echo ======== AIR8; python tl_recal_block9.py air8 $OUT $EW