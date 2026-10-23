export HOME=$PWD/home XDG_CONFIG_HOME=$PWD/home/.config; mkdir -p $HOME
git clone --depth 1 --single-branch -b claude-science-sep29 --filter=blob:none --sparse https://x-access-token:$GITHUB_TOKEN@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git repo 2>&1 | tail -2
cd repo; git log --oneline -1
git ls-tree -r --name-only HEAD | grep -v '^ISO Sept 28' | grep -iE 'seabed-search|searched|surface-search|search_and_rescue|SEARCHED_AREAS|amsa|coverage' | head -80