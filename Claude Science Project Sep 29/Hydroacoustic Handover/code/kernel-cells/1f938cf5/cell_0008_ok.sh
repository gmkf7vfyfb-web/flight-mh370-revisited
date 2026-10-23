export HOME=$PWD/home XDG_CONFIG_HOME=$PWD/home/.config
git clone -q --depth 1 --single-branch -b hypothesis/settling --filter=blob:none --sparse https://x-access-token:$GITHUB_TOKEN@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git settl 2>&1 | grep -v "failed to store"
cd settl; git sparse-checkout set --no-cone "/Claude Science Project Sep 29/engine/hypotheses/settling/" ; git log --oneline -1
cd "Claude Science Project Sep 29/engine/hypotheses/settling/"; find . -type f | grep -v "\.png$" | head -80; du -sh .