cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare
cat tl_grid_evidence.py > /tmp/x1.txt
ls exploratory/pleiades_test/ | head -30
wc -l exploratory/pleiades_test/lhyd.py
grep -n "TAU_GRID\|RHO_C\|TRIAD_GAIN\|T_EFF\|BANDS\|def _se\|def _snr0\|def _pd\|def nuisance\|class \|Sb\[\|def _spec\|C_MEAN\|C_SD\|PICK_S\|SRC =" exploratory/pleiades_test/lhyd.py | head -60