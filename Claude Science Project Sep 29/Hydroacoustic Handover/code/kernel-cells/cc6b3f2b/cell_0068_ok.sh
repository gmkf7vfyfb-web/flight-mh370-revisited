set -e
R="repo/Claude Science Project Sep 29"
cp hydroacoustics-weak-signal-methods.md "$R/results/"
cp out/figs/hydroacoustics-weak-signal-*.png out/figs/hydroacoustics-weak-signal-*.pdf "$R/results/"
cat >> "$R/coordination/architecture.md" <<'EOF'

## 2026-10-22 ~03:00Z — hydroacoustics (weak-signal track, unattended) -> architecture (cc end of flight, composer, Pete): block 8 weak-signal method trials DONE (method trial only; no detection claimed)

Work order 2026-10-21 block 8, brief Refresh v2 §7. Pre-registration 78c7e88 (module branch, before any statistic on data);
code + tables c2b4548 (`prepare/weak_signal/`, `results-data/weak_signal/`); note `results/hydroacoustics-weak-signal-methods.md`
with three charts; full products `/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-weak-signal/` (17 MB, SHA256SUMS).
Everything PREDICTIVE, NOT CALIBRATED; C1, C2; digitised data labelled; both Kadri times carried (text 00:52:03, caption 00:54:30).
- (a) Synthetic impact pulses (one-pole source x KRAKEN coherent broadband channel, 1,800-3,000 km) in 14 days of real IMOS
  background: dispersion-aware matched filters reach P_D = 0.5 at SNR ~7 dB (alpha 0.01 per 60 s window) at 3376, against
  13-16 dB STA/LTA and 27-28 dB band energy; at alpha 0.001 only the matched filters reach 0.5 (envelope 16-19 dB). This is the
  model-matched best case (pulses share the template model). Spectral kurtosis = STA/LTA; cepstral, synchrosqueezing,
  Bayesian change-point, stochastic resonance failed (kept as negative results). Two-station z stacking (idealised) is weak.
  Amendment 1 disclosed: SNR grid extended to 30 dB after the first run.
- (b) Digitised Kadri Fig. 9 panels: only the envelope matched filter reaches p = 0.05 inside an author's box (text time
  00:52:03, label mark); caption time best p = 0.11 (screen); poster panel (a) boxes p >= 0.08. All boxes carried as
  screen-level rows. H08S kurtosis rows are null-mismatch artefacts (airgun shots), not candidates.
- (c) H08S airgun suppression on panels d, e: shot-template subtraction -5.8/-4.7 dB residual energy, -7.6/-5.3 dB with cadence
  gating; chance coincidence rate cut 3-5x; an injected arrival 4 dB below the median shot peak still recovered (0.88/0.50).
  36 surviving z >= 3 peaks listed, 9 in the Kadri lag windows, none a claim (no residual null, gap G-W3).
- Recommendation: add the envelope matched filter (M1b) as the primary screen statistic beside STA/LTA in block 5/7, templates
  from the module's bathymetry-following paths at receiver depth; close gap G-W1 (a non-model-matched ground-truth test, needs
  block 1 digitised waveforms) before any MH370 statistic uses it.
- Gaps: G-W1 no real-arrival test; G-W2 panel null emulated from one IMOS site; G-W3 no H08S residual null; G-W4 secondary
  nulls at stride 4; G-W5 SR rate 0.92/s not 1/s; G-W6 two-station test idealised.
No core request. No ruling needed. done: block 8 / next: block 1 waveforms -> G-W1 / blocker: none for this block.
-- Hydroacoustic Module (weak-signal track, unattended), 22 Oct 2026
EOF
cd repo; export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"; B=claude-science-sep29
git fetch -q origin $B 2>&1 | grep -v "failed to store\|config/git" || true
# rebase our architecture.md append on the fetched head: take origin's file and append our entry
git show origin/$B:"Claude Science Project Sep 29/coordination/architecture.md" > /tmp/arch_head.md
python3 - <<'EOF'
head=open('/tmp/arch_head.md').read(); mine=open('Claude Science Project Sep 29/coordination/architecture.md').read()
i=mine.find('\n## 2026-10-22 ~03:00Z — hydroacoustics (weak-signal track'); entry=mine[i:]
open('Claude Science Project Sep 29/coordination/architecture.md','w').write(head.rstrip('\n')+'\n'+entry)
EOF
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/results/hydroacoustics-weak-signal-methods.md" "Claude Science Project Sep 29/results/hydroacoustics-weak-signal-pd-vs-snr.png" "Claude Science Project Sep 29/results/hydroacoustics-weak-signal-pd-vs-snr.pdf" "Claude Science Project Sep 29/results/hydroacoustics-weak-signal-kadri-panels.png" "Claude Science Project Sep 29/results/hydroacoustics-weak-signal-kadri-panels.pdf" "Claude Science Project Sep 29/results/hydroacoustics-weak-signal-h08s-suppression.png" "Claude Science Project Sep 29/results/hydroacoustics-weak-signal-h08s-suppression.pdf" "Claude Science Project Sep 29/coordination/architecture.md"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (weak-signal track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 8: weak-signal method trials note + three charts (matched filters on the dispersed arrival shape ~7 dB SNR_50 vs 13-16 dB STA/LTA at 3376, model-matched upper bound; Kadri panels: envelope MF p=0.05 at text time 00:52:03 only; H08S shot suppression -5 to -8 dB); coordination entry. PREDICTIVE, NOT CALIBRATED; C1, C2; digitised.")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "failed to store\|config/git" || true
git fetch -q origin $B 2>&1 | grep -v "failed to store\|config/git" || true; echo "work commit $C"; git log --oneline -1 origin/$B