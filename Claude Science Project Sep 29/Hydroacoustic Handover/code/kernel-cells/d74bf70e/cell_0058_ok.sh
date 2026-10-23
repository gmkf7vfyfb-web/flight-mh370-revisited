cd repo
git checkout -q hypothesis/hydroacoustics
git add "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/synthetic_composer_test.py"
git diff --cached --name-only | grep -v '^Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/' ; echo scope-ok
git commit -q -m "Hydroacoustics: synthetic composer test on the parametric 7th-arc PDF, verdict thresholds pre-registered in the header" && git push -q origin hypothesis/hydroacoustics && git log --oneline -1