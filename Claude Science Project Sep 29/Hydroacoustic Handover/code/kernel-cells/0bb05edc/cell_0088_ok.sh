cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
git commit -q -m "sources: remove blocking 'closed access / not held' labels (Pete's ruling 22 Oct 2026); add source-access ledger; Metz 2023, Royer 2016, ATSB 2016 are held; Kadri 2019 vs Dall'Osto 2019 misattribution corrected" 2>&1 | grep -v "ignore\|failed to store" || true
git log -1 --format='%h %s' | cut -c1-120
for i in 1 2 3; do
  git pull -q --rebase origin claude-science-sep29 2>&1 | grep -v "ignore\|failed to store" || true
  if git push -q origin fix-sep29:claude-science-sep29 2>&1 | grep -v "ignore\|failed to store"; then :; fi
  if [ "$(git rev-parse HEAD)" = "$(git ls-remote origin refs/heads/claude-science-sep29 | cut -f1)" ]; then echo "PUSHED: $(git rev-parse --short HEAD)"; break; fi
  sleep 3
done
git ls-remote origin refs/heads/claude-science-sep29 | cut -c1-12
git log --oneline -3 | cut -c1-110