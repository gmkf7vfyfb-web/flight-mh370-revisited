
sub('coordination/PLEIADES.md',"The [Taylor1921] equation location is still open: the paper and LaCasce (2008) are closed access, so this is a library request for Pete.",
    "The [Taylor1921] equation location is still open: there is no copy of the paper or of LaCasce (2008) in the project store yet, so this is a library request for Pete.")
sub('results/hydroacoustics-audit-architecture.md',"(PAGEOPH 2022, doi 10.1007/s00024-022-03090-0; closed access, not read)","(PAGEOPH 2022, doi 10.1007/s00024-022-03090-0; no copy in the project store, not read)")
r=subprocess.run("""cd "%s" && export GIT_CONFIG_GLOBAL=/dev/null && git add --sparse -A . 2>/dev/null; git commit -q -m "sources: last two stale 'closed access' labels (Taylor 1921 / LaCasce 2008 in PLEIADES.md; Prario 2023 in audit-architecture)" 2>&1 | grep -v ignore
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git"
for i in 1 2 3; do
  git -c credential.helper= pull -q --rebase "$URL" claude-science-sep29 2>&1 | sed "s/${GITHUB_TOKEN}/***/g" | grep -v ignore
  git -c credential.helper= push -q "$URL" fix-sep29:claude-science-sep29 2>&1 | sed "s/${GITHUB_TOKEN}/***/g" | grep -v ignore
  R=$(git -c credential.helper= ls-remote "$URL" refs/heads/claude-science-sep29 2>/dev/null | cut -f1)
  if [ "$(git rev-parse HEAD)" = "$R" ]; then echo "PUSHED: $(git rev-parse --short HEAD)"; break; fi
  sleep 3
done""" % ROOT, shell=True, capture_output=True, text=True, env=dict(os.environ))
print(r.stdout[-400:], r.stderr[-300:])
