cd repo && export XDG_CONFIG_HOME=/tmp/xdg
P="Claude Science Project Sep 29"
git checkout origin/claude-science-sep29 -- "$P/coordination" "$P/threads" 2>&1|tail -2
echo "=== files ==="
wc -c "$P/threads/master-prompts/hydroacoustics.md" "$P/coordination/HYDROACOUSTICS.md"
echo "=== hydro results-data inventory (h08s/kadri/pair) ==="
for d in h08s_shots h08s_template h08s_pulse pair_tests kadri2a kadri_package kadri_fig9_noise stageA; do echo "-- $d"; ls "$P/engine/hypotheses/hydroacoustics/results-data/$d" 2>/dev/null | head -20; done
echo "=== prepare scripts of interest ==="
ls "$P/engine/hypotheses/hydroacoustics/prepare" | head -60