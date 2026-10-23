cd "$PWD" && export XDG_CONFIG_HOME=/tmp/xdg && git clone --filter=blob:none --sparse --single-branch -b claude-science-sep29 "https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git" repo 2>&1 | tail -5
cd repo && git sparse-checkout set "Claude Science Project Sep 29" 2>&1 | tail -3
echo "--- top ---"; ls
echo "--- proj ---"; ls "Claude Science Project Sep 29"
echo "--- HEAD ---"; git log --oneline -1
echo "--- branches ---"; git ls-remote origin "refs/heads/hypothesis/hydroacoustics"