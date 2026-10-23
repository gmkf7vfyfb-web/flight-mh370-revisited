cd hyd; P='Claude Science Project Sep 29/engine/hypotheses/hydroacoustics'
git sparse-checkout add "/$P/prepare/*.py" "/$P/prepare/searches_run_j/*" "/$P/prepare/weak_signal/*" "/$P/src/*" 2>&1 | grep -v config/git
grep -rn -E "rec_times|, ?16\)|int\([^)]*16\)|GPS|clock.?drift|leap" "$P/prepare" "$P/src" 2>/dev/null | grep -v "^Binary" | head -30