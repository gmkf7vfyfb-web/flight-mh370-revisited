cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git"
P='Claude Science Project Sep 29'
git -c credential.helper= fetch -q "$URL" '+refs/heads/claude-science-sep29:refs/remotes/origin/claude-science-sep29' 2>&1 | sed "s/${GITHUB_TOKEN}/***/g" | grep -v ignore || true
git sparse-checkout add "/$P/results/**/*.md" "/$P/coordination/*.md" "/$P/threads/**/*.md" "/$P/paper/*.md" "/$P/results/composer-pass0/*.py" "/$P/results/composer-pass1-run-c/*.py" "/$P/results/composer-pass2-run-i/*.py" "/$P/results/composer-views-v3-run-j/*.py" "/$P/results/composer-views-v3-run-j/v3.2/*.py" 2>&1 | grep -v ignore || true
git checkout -q -B fix-sep29 origin/claude-science-sep29 2>&1 | grep -v ignore || true
git log -1 --format='%h %s' | cut -c1-90
find "$P" -name "*.md" | wc -l