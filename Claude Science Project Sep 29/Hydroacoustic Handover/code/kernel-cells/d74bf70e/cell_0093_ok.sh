cd repo
git ls-remote origin hypothesis/hydroacoustics; git rev-parse hypothesis/hydroacoustics
MB=$(git merge-base origin/claude-science-sep29 hypothesis/hydroacoustics)
git diff --name-only $MB hypothesis/hydroacoustics
echo "outside module dir: $(git diff --name-only $MB hypothesis/hydroacoustics | grep -v '^Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/' | wc -l)"
git log --oneline hypothesis/hydroacoustics -5