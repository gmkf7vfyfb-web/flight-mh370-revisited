export HOME=$PWD/h XDG_CONFIG_HOME=$PWD/h/.config
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git"
git clone -q --depth 1 --single-branch -b hypothesis/end-of-flight --filter=blob:none --sparse "$URL" eof 2>&1|tail -2
cd eof; git config --local core.excludesFile ""; git sparse-checkout set --no-cone "/Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke/" "/Claude Science Project Sep 29/engine/data/satcom-observations.csv" 2>&1 | tail -1
git log --oneline -1; ls "Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke/" | wc -l
mkdir -p ../scorer; S="Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke"; cp "$S"/option_table_0019.py "$S"/displacement_hist.py "$S"/compact_impacts.py "$S"/compact-columns.json "Claude Science Project Sep 29/engine/data/satcom-observations.csv" ../scorer/; ls ../scorer; wc -l ../scorer/*.py