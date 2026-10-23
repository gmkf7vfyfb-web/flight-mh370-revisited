cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
P='Claude Science Project Sep 29'
git checkout -q -- "$P/results/hydroacoustics-bibliography.csv" "$P/results/hydroacoustics-literature-review.md" "$P/results/hydroacoustics-prior-work-critique.md" "$P/threads/master-prompts/hydroacoustics.md" 2>&1 | grep -v ignore || true
git add --sparse -A . 2>&1 | grep -v ignore || true
git status --short | cut -c1-170
git diff --cached --name-only | grep -v "engine/hypotheses/hydroacoustics/" || echo "all staged paths are inside the module folder"
git diff --cached -U0 | grep '^[+-]' | grep -v '^+++\|^---' | cut -c1-210