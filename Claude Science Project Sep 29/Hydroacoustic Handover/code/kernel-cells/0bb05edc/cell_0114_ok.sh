cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
P='Claude Science Project Sep 29'
head -n 12 "$P/ARCHITECTURE.md" | cut -c1-170; echo ......; head -n 8 "$P/threads/master-prompts/composer.md" | cut -c1-120
git add --sparse -A . 2>&1 | grep -v ignore || true
echo; git diff --cached --stat | tail -n 45 | cut -c1-130
echo; echo "== lines removed that were not mine/expected? count of '-' lines per file (top 8)"; git diff --cached --numstat | sort -k2 -n -r | head -8 | cut -c1-140