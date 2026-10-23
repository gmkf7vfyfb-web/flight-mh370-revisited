cd hydro; export GIT_CONFIG_GLOBAL=/dev/null
F="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/tl_recal_block9.py"
git show origin/hypothesis/hydroacoustics:"$F" > /tmp/tl_recal_block9.py
grep -n -i "ram\|pyram\|wall\|minutes\|seconds\|dr\b\|dz\b\|def " /tmp/tl_recal_block9.py | head -60