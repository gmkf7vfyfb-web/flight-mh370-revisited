cd hydro; export GIT_CONFIG_GLOBAL=/dev/null
git show origin/hypothesis/hydroacoustics:"Claude Science Project Sep 29/engine/Makefile" 2>/dev/null | grep -n -A12 "^scope" | head -30