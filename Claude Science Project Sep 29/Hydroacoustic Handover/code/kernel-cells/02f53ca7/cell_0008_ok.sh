cd "repo/Claude Science Project Sep 29/results"
cat hydroacoustics-audit/c3-source-models.md
echo "=== git log ew0112 note"; git log --format='%h %ci %s' -- hydroacoustics-air9-ew0112-source-reference.md | head
cd "../../../hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/air9_ew0112"
echo "=== verdicts"; cat verdicts.json; echo; cat verdicts_amendment1.json; echo
echo "=== summary"; cat air9_reference_rescore_summary.csv
echo "=== fig2 scaling"; cat ew0112_fig2_scaling.json
echo "=== ball spectra"; cat ew0112_fig2_ball_spectra_bands_DIGITISED.csv
echo "=== ledger"; cat ew0112_transcription_ledger.csv
echo "=== claims"; cat recovery_package_claims_verified.csv | head -30