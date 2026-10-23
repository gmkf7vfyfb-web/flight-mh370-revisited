export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null; URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd hydro && python - <<'EOF'
p="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j/prereg.py"; s=open(p).read()
s=s.replace('''   CHUNK_ROWS 1 M -> 500 k (memory; no value change).
"""''','''   CHUNK_ROWS 1 M -> 500 k (memory; no value change).
A2 (22 Oct, after the run): another process held the disk below the 20 GiB floor for part of the run, so 14 seeds were written with the
   marginalised IMOS column only (section 8 rule). B11_TOPUP=1 re-runs such a seed writing all five columns; 4 were topped up (waypoints
   21-24), 10 free-stratum seeds (0.13 % of the mixture mass) remain short (gap G11-2). Values unchanged (deterministic re-run).
A3 (22 Oct, after the run): reduce.py does not write the merged subsample to the exchange (1.1 GB duplicate of the per-seed files).
   Deviation from the task text, declared before the run: alpha 0.05 primary (report level), screen level 0.3 as a sensitivity.
"""''')
open(p,"w").write(s); print("ok")
EOF
B=hypothesis/hydroacoustics; git -c credential.helper= fetch -q origin $B 2>/dev/null; export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j/prereg.py"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (composition)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics block 11: prereg amendments A2 (disk-floor short write + top-up mode) and A3 (merged subsample not written) recorded in prereg.py; no value changes")
git -c credential.helper= push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "failed to store\|config/git"; echo "commit $C"