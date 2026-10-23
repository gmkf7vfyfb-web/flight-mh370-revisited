set -e
export GIT_CONFIG_GLOBAL=/dev/null
cd fix-metz
git fetch -q origin 2>&1 | grep -v "failed to store" || true
P='Claude Science Project Sep 29'
git sparse-checkout set \
 "/$P/coordination/architecture.md" "/$P/coordination/HYDROACOUSTICS.md" "/$P/coordination/PAPER.md" \
 "/$P/results/hydroacoustics-bibliography.csv" "/$P/results/hydroacoustics-references.md" "/$P/results/hydroacoustics-digitised-sources.md" \
 "/$P/results/hydroacoustics-blackman-validation.md" "/$P/results/hydroacoustics-kadri-package-v2.md" "/$P/results/hydroacoustics-overnight-2026-10-22-summary.md" \
 "/$P/results/hydroacoustics-literature-review.md" "/$P/results/hydroacoustics-prior-work-critique.md" "/$P/results/debris-drift-find-episodes.md" \
 "/$P/results/evidence-sweep-2026-10-17/research-radar-infrasound-ohasisbio.md" \
 "/$P/results/satellite-coverage-2014-03/coincidence/literature/satellite-literature-register.csv" \
 "/$P/paper/JON-MODEL-PAPERS.md" "/$P/threads/master-prompts/hydroacoustics.md"
git checkout -q -B fix-sep29 origin/claude-science-sep29
git log -1 --format='%h %ad %s' --date=iso | cut -c1-120
git status --short | head -3
ls "$P/results" | head -20