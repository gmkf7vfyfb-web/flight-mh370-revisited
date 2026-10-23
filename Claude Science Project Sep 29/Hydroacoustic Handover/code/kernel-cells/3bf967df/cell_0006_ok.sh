export HOME=$PWD/h XDG_CONFIG_HOME=$PWD/h/.config; mkdir -p $XDG_CONFIG_HOME/git; touch $XDG_CONFIG_HOME/git/ignore
rm -rf repo
git clone -q --depth 1 --single-branch -b claude-science-sep29 --filter=blob:none --sparse "https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git" repo 2>&1 | tail -2
cd repo && git config --local core.excludesFile "" && git log -1 --format='%h %cd %s' 
git ls-tree -r --name-only HEAD | grep -iE 'kadri|haixun|evidence-sweep|hydroacoustics-kadri' | head -60