cd hydro; export GIT_CONFIG_GLOBAL=/dev/null; B=hypothesis/hydroacoustics; URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
H="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
git fetch -q origin $B 2>&1 | grep -v "failed to store\|ignore"
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "$H/prepare/calibration_events_stage1b.py" "$H/prepare/raster_trace.py" "$H/prepare/digitise_waveform_rasters.py" "$H/prepare/cmst_fig1_imos_overlay.py" "$H/results-data/digitised/waveform-rasters" 2>&1 | grep -v ignore
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); echo $OLD $NEW; [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
git diff --name-only origin/$B $TREE | grep -v "^$H/" && echo "OUT OF SCOPE" ; git diff --name-only origin/$B $TREE | grep -c .
C=$(git -c user.name="Hydroacoustic Module (correction track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics correction track: PRE-REGISTER calibration events stage 1b (KRAKEN + RAM on the af447-H10S and sanjuan-charge-H10N paths; Gaspin & Shuler charge source; criteria.md C1 with C4 level thresholds) before any module TL/RAM value on these paths; plus DIGITISED waveform rasters (Kadri 2024 Figs 5a/7/8, Nielsen 2021 Fig 3, Vergoz 2021 Fig 2, CMST 2014 Figs 1-2; gap G8) and the CMST Fig 1 vs IMOS 3315 overlay check. PREDICTIVE, NOT CALIBRATED; C1, C2")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "failed to store"; echo PUSHED $C; git fetch -q origin $B 2>&1 | grep -v "failed\|ignore"; git log --oneline -1 origin/$B