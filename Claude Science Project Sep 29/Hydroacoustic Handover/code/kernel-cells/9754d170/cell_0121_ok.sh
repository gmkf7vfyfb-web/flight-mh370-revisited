cd audit/repo && git pull -q --rebase origin claude-science-sep29 2>&1 | grep -v ignore | tail -2; C="Claude Science Project Sep 29/coordination"; cat >> "$C/HYDROACOUSTICS.md" <<'EOF'

## 2026-10-11 ~00:30 UTC — architecture audit → hydroacoustics: independent audit of bugs and model fidelity (Pete's request)

Report: `results/hydroacoustics-audit-architecture.md`. Pre-registration: `results/hydroacoustics-audit/criteria.md`
(`940f1a3`), C3 source models (`7157b77`, two citation amendments). Read-only on your code (@3412bc6).
- **Verdict.** The engine is sound as code (KRAKEN reproduced to 0.15 dB on independently built paths; markers to 0.0 dB;
  F-35A η_cal to 0.02 dB). It is **NOT CALIBRATED** for a likelihood under criteria C6:
  - **air9 absolute TL fails slope at both stations:** +10.4 ± 0.9 dB/oct (H01W) and +7.4 ± 0.7 dB/oct (H08S); levels
    −1.4 / −2.4 dB pass. The station difference is PARTIAL (slope +2.4 dB/oct).
  - **Array directivity explains about two thirds of the tilt**, but this depends on the geometry, so air9 cannot
    calibrate near-surface point-source coupling.
  - **SUS 2003 station differences PASS** (3 shots, but only over 31.5–63 Hz).
  - **Below 12.5 Hz, H01W is unconstrained.** At H08S, air9 at 6.3–10 Hz shows the model 9–12 dB too lossy.
- **Pléiades.** abs(ln R_hyd) ≤ 0.30 under every TL variant, so "within noise" is robust. The power is not: E[ln R | H] in
  scenario A runs from 0.015 to 0.37.
- **Fixes, in priority order:**
  1. Relabel air9 and add slope and shape criteria.
  2. Replace flat C_site with a level + slope error and an allowance below the data span.
  3. Get more near-surface calibration events: the Kadri aircraft list, the spheres, and Gaspin & Shuler 1971 by hand.
  4. Use App. B noise in lhyd (+5.4 dB at H01W); IMS P_D is borrowed.
  5. Check island and ridge blockage with N×2D/3D (A11→H08S crosses Cocos (Keeling) but was observed).
  6. Make coupling depend on impact kinematics (coverage gap G-H1).
- Corrected charts: `results/hydroacoustics-audit/hydroacoustics-audit-noise-vs-impact-{H01W,H08S}.png`.

- Architecture (audit)
EOF
cat >> "$C/architecture.md" <<'EOF'

## 2026-10-11 ~00:30 UTC — architecture: hydroacoustics audit complete (record)

`results/hydroacoustics-audit-architecture.md`. **Hydro TL/source chain: NOT CALIBRATED** for a likelihood:
- **air9:** slope FAIL at both stations (+10.4 / +7.4 dB/oct).
- **Path:** station differences PARTIAL (airgun) and PASS (SUS, 31.5–63 Hz only).
- **Below 12.5 Hz:** nothing checks H01W.
- **Hydro module status unchanged:** predictive or sensitivity use only, and lnL = 0 stays.

The Pléiades hydro "within noise" survives every TL variant (abs(ln R_hyd) ≤ 0.30), so it stands, labelled
conditional on the calibration error model. Its power check carries that label too.

**Coverage gaps recorded (Pete's rule, 10 Oct):**
- **G-H1 (reach, OPEN):** coupling η has no angle, speed or breakup dependence; one near-vertical F-35A event.
- **G-H2 (feasible/reach, OPEN; referred to end of flight):** impact speeds ≥ 340 m/s (supersonic at sea level) appear
  in end-of-flight samples (maximum 378 m/s) and in the hydro chart scenario (a).
- **G-H3 (charts, CLOSED):** the 150–270 m/s descents are now shown.
- **G-H4 (calibration span, OPEN):** below 12.5 Hz at H01W the model is unconstrained.

Declared deviations: power checks at N_SYN = 1,000; ln R_hyd on the 5,000-row packages (shifts only, provisional);
absolute SUS source levels not scored (DTIC blocks automated access).

- Architecture
EOF
git add -A "Claude Science Project Sep 29/results/hydroacoustics-audit" "Claude Science Project Sep 29/results/hydroacoustics-audit-architecture.md" "$C/HYDROACOUSTICS.md" "$C/architecture.md"; git ls-files -s "Claude Science Project Sep 29/results/hydroacoustics-audit" | grep -E '\.bin$|fuel-tables' ; git commit -q -m "hydroacoustics audit: report, corrected noise-vs-impact charts, calibration checks, SUS test, TL sensitivity of the Pleiades hydro test; coordination posts" && git push -q https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git HEAD:claude-science-sep29 2>&1 | grep -v -e 'failed to store' -e ignore | tail -2; git log --oneline -1; git status -sb | head -2