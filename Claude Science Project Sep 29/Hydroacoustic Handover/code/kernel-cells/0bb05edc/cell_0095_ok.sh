cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
P='Claude Science Project Sep 29'; E="$P/engine/hypotheses/hydroacoustics"
python3 -m py_compile "$E/prepare/digitise_brown_2026.py" "$E/prepare/tl_recal_block9.py" && echo "py_compile ok"; find . -name "__pycache__" -path "*hydroacoustics*" -exec rm -rf {} + 2>/dev/null; git status --short | grep -v "^M " | head -3
python3 -c "import json;json.load(open('$E/results-data/digitised/brown-2026/METHOD.json'));print('json ok')"
git commit -q -m "hydroacoustics: remove stale 'closed access / not held' labels from module code, data notes and the (unsent) Kadri request list; San Juan 2019 paper is Dall'Osto's (Pete's ruling 22 Oct 2026)" 2>&1 | grep -v "ignore" || true
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git"
for i in 1 2 3; do
  git -c credential.helper= pull -q --rebase "$URL" hypothesis/hydroacoustics 2>&1 | sed "s/${GITHUB_TOKEN}/***/g" | grep -v ignore || true
  git -c credential.helper= push -q "$URL" fix-hydro:hypothesis/hydroacoustics 2>&1 | sed "s/${GITHUB_TOKEN}/***/g" | grep -v ignore || true
  R=$(git -c credential.helper= ls-remote "$URL" refs/heads/hypothesis/hydroacoustics 2>/dev/null | cut -f1)
  if [ "$(git rev-parse HEAD)" = "$R" ]; then echo "PUSHED: $(git rev-parse --short HEAD)"; break; fi
  sleep 3
done
git log --oneline -3 | cut -c1-120