cd repo; export GIT_CONFIG_GLOBAL=/dev/null
P="Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke"
mkdir -p ../eof; for f in option_table_0019.py compact_impacts.py family_shares.py combine_strata_0019.py supplement_summary.py; do git show "origin/claude-science-sep29:$P/$f" > ../eof/$f; done
wc -l ../eof/*.py
sed -n 1,90p ../eof/option_table_0019.py