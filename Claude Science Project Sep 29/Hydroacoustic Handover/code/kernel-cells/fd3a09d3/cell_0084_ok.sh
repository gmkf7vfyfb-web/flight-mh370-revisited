cd hydro; export GIT_CONFIG_GLOBAL=/dev/null
git fetch -q origin hypothesis/hydroacoustics 2>&1 | grep -v "failed to store"; git log --oneline -8 origin/hypothesis/hydroacoustics
git diff --stat fc825c0 origin/hypothesis/hydroacoustics -- "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare" | tail -15
git show origin/hypothesis/hydroacoustics --stat --oneline | head -5
for f in $(git diff --name-only fc825c0 origin/hypothesis/hydroacoustics | grep -i "ram\|air7\|recal" | head -5); do echo "== $f"; git show origin/hypothesis/hydroacoustics:"$f" | sed -n 1,40p; done