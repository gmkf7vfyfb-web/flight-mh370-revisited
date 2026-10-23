cd hyd; P='Claude Science Project Sep 29/engine/hypotheses/hydroacoustics'
git ls-tree -r --name-only HEAD | grep "$P/results-data/digitised/royer" | head -60
git ls-tree -r --name-only HEAD | grep -E "$P/(results-data/(searches_run_j|calibration_events|windows_run_j|pair_tests|kadri2a|kadri_northern)|prepare/ranked)" | grep -v -E "\.png$|\.pdf$" | head -80