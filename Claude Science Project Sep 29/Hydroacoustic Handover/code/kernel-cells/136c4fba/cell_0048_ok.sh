cd repo && export XDG_CONFIG_HOME=/tmp/xdg
P="Claude Science Project Sep 29"
python3 -m py_compile "$P/engine/hypotheses/hydroacoustics/prepare/kadri_h01w_time_discriminant.py" && echo compiles
git add "$P/engine/hypotheses/hydroacoustics/prepare/kadri_h01w_time_discriminant.py" "$P/engine/hypotheses/hydroacoustics/prepare/kadri_northern_conditional.py"
git -c user.name="hydroacoustics" -c user.email="hydroacoustics@local" commit -q -m "Hydroacoustics run J Task 1 amendment A1: PRE-REGISTRATION of the Cape Leeuwin two-time discriminant (Pete, 13 Oct), committed before any statistic; cycles() unpack fix and calibration path fix in the Task 1 script"
git log --oneline -1
cd "$P/engine/hypotheses/hydroacoustics"
KD="../../../../Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data"
time python3 prepare/kadri_h01w_time_discriminant.py "$KD" results-data/kadri_northern 2>&1 | grep -viE "userwarning|_set_context|runtimewarning|return \(x -|obs = float|nanmax|nanmin" | tail -60