export HOME=$PWD/h XDG_CONFIG_HOME=$PWD/h/.config
cat >> out/README.md <<'EOF'

## Follow-up: queued dedicated run (not yet run when this note was committed)

deskstar job 10b3068e-c457-4bc1-9975-96bc39bc0d8e (`jobs/kadriB.sh`; submitted 18 Oct 01:2xZ) waits for the drift arc-latitude chain
(chain_arclat2.sh, still in its first of eight legs at 02:00Z under a host load of about 160), then holds `~/.mh370-heavy.lock` for:
(1) 26 pilot legs: the six L points at their own T and C impact times (crossing and Haixun at 1e6 particles, strip points at 3e5) and three run J anchors
(37/35/30 S track nodes, 3e5, 00:19:37), both ocean models, with three PROVISIONAL Indonesian segments (base level off, so B/C/off/A/searcher/populated
equal the arclat definitions) and the level alternatives B_ID_low/mid/full, populated_ID_mid, off_ID_mid;
(2) the origin-grid extension (833 points at 0.5 deg, 96-113 E, 35-17 S). Outputs: `out/<leg>-nodes.csv` and `snapE-<model>.bin` in the remote job workdir
/home/pete/.claude-science-scratch/.claude-science/jobs/10b3068e-c457-4bc1-9975-96bc39bc0d8e/. To finish: the point LLRs are ln_l / ln_l_lev_* of the L legs
minus the same columns of the 37 S anchor (same-run comparison), plus the anchor-to-reference offset from §3; the backward test re-runs with
ring_hook.py on snapG + snapE. Until then the numbers above that rest on the run A surfaces (release 00:19:37) stand as the interim result.
EOF
D="repo/Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/drift"; cp out/README.md "$D/README.md"
cd repo; git pull -q --rebase
cat >> "Claude Science Project Sep 29/coordination/architecture.md" <<'EOF'

## 2026-10-18 02:10Z — ocean drift (Kadri-Haixun conditional, drift leg Q7) -> architecture (cc composer, Pete)
Interim results committed at results/kadri-haixun-conditional-2026-10-18/drift/README.md. Prior: run J, four route families, 'D{d} total q=0.333 (C2 silent)'.
Row-level drift LLR, H_K vs the run J reference (D0, two-model mixture, 1-sigma): finds only +0.83 ± 0.35 (T) / +0.81 ± 0.35 (C); with the populated-coast term at the current setting +2.86 ± 0.20 / +2.82 ± 0.20.
The value is stable over D0-D5. It is not specific to the bearing: the 26-33 S plateau is as good. Conditional ESS is 83/19 at D0 and 1-15 at D2-D5 (unconverged composition; gap G-K1 for core/EoF).
Forward drift: at most 6e-4 of the floating debris from the bearing is within 110 km of Haixun at 03:15Z 5 Apr. Backward: the ring origin excludes the bearing (provisional grid).
A heavy job (deskstar 10b3068e) is queued behind the arc-latitude chain for the dedicated L-point release run and the origin-grid extension; the drift thread or a later session should harvest it (README follow-up).
Joined planned descents J0011/J2241 are not included (declared). — Claude Science, drift leg
EOF
git add "Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/drift/README.md" "Claude Science Project Sep 29/coordination/architecture.md"
git diff --cached --name-only | grep -E "\.bin$|fuel-tables.json|\.xlsm$" && echo BAD || echo audit-ok
git -c user.name="Claude Science" -c user.email="noreply@example.com" commit -q -m "Kadri-Haixun drift leg: follow-up note for queued dedicated run; coordination entry"
git push -q https://x-access-token:$GITHUB_TOKEN@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git HEAD:claude-science-sep29 2>&1 | grep -v "failed to store"; git rev-parse --short HEAD; git ls-remote https://x-access-token:$GITHUB_TOKEN@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git refs/heads/claude-science-sep29 | cut -c1-7