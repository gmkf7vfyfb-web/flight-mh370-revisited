export XDG_CONFIG_HOME=$PWD/.xdg; mkdir -p $XDG_CONFIG_HOME
git clone -q --depth 50 --no-single-branch https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git repo 2>&1 | tail -3
cd repo; git branch -a | grep -E "sep29|pleiades|hydro|end-of-flight"; git checkout -q claude-science-sep29; git log --oneline -3
ls; ls results | grep -iE "hydro|pleiad" ; ls results/pleiades | head -50