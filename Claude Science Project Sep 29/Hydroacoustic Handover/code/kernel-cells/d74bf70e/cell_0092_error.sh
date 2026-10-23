cd repo
git add "Claude Science Project Sep 29/results/hydroacoustics-literature-review.md" "Claude Science Project Sep 29/results/hydroacoustics-prior-work-critique.md" "Claude Science Project Sep 29/results/hydroacoustics-bibliography.csv" "Claude Science Project Sep 29/results/hydroacoustics-ground-truth-cases.csv"
git commit -q -m "results: hydroacoustics literature review and critique of prior work on this case (81-entry bibliography, 37 ground-truth cases)"
for i in 1 2 3; do git pull -q --rebase origin claude-science-sep29 && git push -q origin HEAD:claude-science-sep29 && break; sleep 3; done
git log --oneline -1
echo "== scope: files on module branch relative to merge-base with working branch"
git diff --name-only $(git merge-base origin/claude-science-sep29 origin/hypothesis/hydroacoustics) origin/hypothesis/hydroacoustics | sed 's|^|  |'
git diff --name-only $(git merge-base origin/claude-science-sep29 origin/hypothesis/hydroacoustics) origin/hypothesis/hydroacoustics | grep -v '^Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/' | wc -l
git log --oneline origin/hypothesis/hydroacoustics -6