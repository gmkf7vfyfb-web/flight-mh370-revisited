s = open('hydroacoustics-overnight-2026-10-22-summary.md').read()
old_c = s[s.index('10. **Composition**'):s.index('11. **Kadri package v2**')]
new_c = """10. **Composition** (`results/hydroacoustics-composition-run-j.md`, addenda A4/A5 = corrected table). IMOS-gated likelihood
    L = (1 − P_D) + P_D × m/β per impact row, η marginalised over log-uniform [1e-6, 1e-2], written for all 313.6 M rows on the
    corrected IMOS table as `run-j-gated-v2/` (READY 12:34Z; `run-j-gated/` is the old-table version, kept and marked SUPERSEDED).
    Final headline (D0′ p 0.5): the IMOS non-detections are weakly informative — ln Z −0.034, median latitude +0.05°, mass north of
    33 S 0.058 → 0.063, KL 0.008 nats; 95 % upper limit on η from the non-detection 5.6e-3 against 6.3e-3 for the prior alone;
    P(no detection | η) = 0.56 / 0.79 / 0.89 at η = 1e-2 / 1e-3 / anchor; classical 95 % exclusion is not reached below η = 1e-2
    anywhere. Bayes factors: Kadri 306.18° row −0.04 (both times); Royer B −0.18; Royer D1/D2 and poster boxes 1–3 no information;
    Holland-type p = 1 vs p = 0 within ±0.03 under D0′. New defect G11-1: the pre-registered match term is amplitude-blind (it drove
    +1.4° shifts under D3/D4 p = 1 on the old table; +0.15° on the corrected table; amplitude-weighted +0.10°; non-detection only
    −0.02°). A first statistics re-run that straddled the table rewrite was withdrawn and redone (A5, disclosed). **Ruling requested
    from architecture: may `hydro-lnL-imos-margeta` in run-j-gated-v2 enter the composer as the module's default (G11-1 label), IMS
    proxy as sensitivity? The composer default is unchanged (0.0) until then.**
"""
s = s.replace(old_c, new_c)
s = s.replace("Its predictions.csv carries the old IMOS table and needs a reload before sending.", "Its predictions.csv carries the old IMOS table and needs a reload before sending.")
s = s.replace("composition 3a566a0/e79bba2;", "composition 3a566a0/e79bba2/037d154/faa8828;")
s = s.replace("- Composition: per-row exchange columns on the old IMOS table until run-j-gated-v2 completes; charts not re-rendered on the\n  corrected table; amplitude-aware match is a down-weighting sensitivity, not a calibrated likelihood ratio.",
              "- Composition: α = 0.05 primary (screen level 0.3 as a sensitivity); amplitude-aware match is a down-weighting sensitivity, not a\n  calibrated likelihood ratio; supplement rows enter the statistics with a τ stand-in and no column; the first A4 statistics run\n  (mixed table versions) is withdrawn and replaced (A5).")
s = s.replace("Exchange outputs ~9 GB", "exchange outputs ~9 GB")
open('hydroacoustics-overnight-2026-10-22-summary.md','w').write(s)
print(len(s), 'run-j-gated-v2' in s)