export HOME=$PWD/home XDG_CONFIG_HOME=$PWD/home/.config; W=$PWD; cd repo
P='Claude Science Project Sep 29'; mkdir -p $W/lib
for f in compact-columns.json compact_impacts.py displacement_hist.py option_table_0019.py; do git show "FETCH_HEAD:$P/engine/hypotheses/end-of-flight/smoke/$f" > $W/lib/$f; done
git sparse-checkout add "/$P/results/composer-pass1-run-c/seabed_loglik.py" "/$P/engine/data/satcom-observations.csv" 2>&1 | tail -1
cp "$P/results/composer-pass1-run-c/seabed_loglik.py" "$P/engine/data/satcom-observations.csv" "$P/results/composer-views-run-j/views_common.py" $W/lib/
ls -la $W/lib; ls /Users/pete/Downloads/mh370-exchange/end-of-flight/; ls /Users/pete/Downloads/mh370-exchange/composer/run-j-views/work | head
grep -n "def seed_terms" -A60 $W/lib/option_table_0019.py | head -90