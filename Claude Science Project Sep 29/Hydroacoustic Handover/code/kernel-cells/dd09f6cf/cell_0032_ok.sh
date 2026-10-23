export HOME=$PWD/home XDG_CONFIG_HOME=$PWD/home/.config; cd repo
P='Claude Science Project Sep 29'
git ls-tree --name-only HEAD -- "$P/engine/hypotheses/end-of-flight/smoke/" | head; 
git fetch --depth 1 origin hypothesis/end-of-flight 2>&1 | tail -1
git ls-tree -r --name-only FETCH_HEAD -- "$P/engine/hypotheses/end-of-flight/smoke/" | grep -E 'option_table_0019|displacement_hist|compact' ; git log -1 --format='%h %ci' FETCH_HEAD
ls ~/Downloads/mh370-exchange/composer/run-j-views/work 2>/dev/null | head; ls ~/Downloads/mh370-exchange/end-of-flight/ | head -30