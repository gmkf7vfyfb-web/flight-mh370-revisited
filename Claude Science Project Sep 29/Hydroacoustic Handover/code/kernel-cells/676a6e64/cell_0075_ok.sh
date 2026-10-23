cd hydro; export GIT_CONFIG_GLOBAL=/dev/null
git fetch -q origin hypothesis/hydroacoustics claude-science-sep29 2>&1 | grep -v 'config/git' || true
BASE=$(git merge-base origin/hypothesis/hydroacoustics origin/claude-science-sep29 2>/dev/null || echo 77b4b49)
echo "base=$BASE head=$(git rev-parse --short origin/hypothesis/hydroacoustics)"
echo "=== module-branch commits tonight"; git log --format='%h %s' 77b4b49..origin/hypothesis/hydroacoustics | wc -l
echo "=== changed paths since 77b4b49 outside hypotheses/hydroacoustics (relative to engine/)"
git diff --name-only 77b4b49 origin/hypothesis/hydroacoustics | sed 's#^Claude Science Project Sep 29/##' | awk '!/^engine\/hypotheses\/hydroacoustics\//' | sed 's#/[^/]*$##' | sort | uniq -c | sort -rn | head
echo "=== engine/ changes outside the module"; git diff --name-only 77b4b49 origin/hypothesis/hydroacoustics | grep '^Claude Science Project Sep 29/engine/' | grep -v 'engine/hypotheses/hydroacoustics/' | head
echo "=== .md inside engine/?"; git diff --name-only 77b4b49 origin/hypothesis/hydroacoustics | grep '/engine/.*\.md$' | head