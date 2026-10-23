cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
git commit -q -m "standing rule on labels (Pete, 22 Oct 2026): no label without approval, posted to ARCHITECTURE, README, every master prompt, engine/AGENTS and every coordination inbox; remaining blocking wording removed; wording unified to 'not retrieved — ask Pete'" 2>&1 | grep -v ignore || true
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git"
for i in 1 2 3 4; do
  git -c credential.helper= pull -q --rebase "$URL" claude-science-sep29 2>&1 | sed "s/${GITHUB_TOKEN}/***/g" | grep -v ignore || true
  git -c credential.helper= push -q "$URL" fix-sep29:claude-science-sep29 2>&1 | sed "s/${GITHUB_TOKEN}/***/g" | grep -v ignore || true
  R=$(git -c credential.helper= ls-remote "$URL" refs/heads/claude-science-sep29 2>/dev/null | cut -f1)
  if [ "$(git rev-parse HEAD)" = "$R" ]; then echo "PUSHED: $(git rev-parse --short HEAD)"; break; fi
  sleep 4
done
git log --oneline -3 | cut -c1-120