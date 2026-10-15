# End-of-flight work order, 15 October 2026 (b)

From coordination, after Pete's message of 15 Oct. Family codes: A1 = cruise to FE then uncontrolled descent; A2 = cruise to FE then controlled/arrested descent; B = planned descent with ditching approach begun before FE. Analysis behind items 1–3: `results/answers-2026-10-15-pm.md`.

1. **Ruling recorded (Decision 4).** The headline uses dive probability p = 0.5. The sweep over p is a declared sensitivity.
2. **D0 redefined.** "00:19 values held out, transmission imposed": every treatment requires the aircraft to be airborne at 00:19:37. Today, 32.8% of D0 weight impacts before 00:19, which is physically impossible. Recompute the D0 shares and the loudness shares on this set. Loudness is reported only on the feasible set (loudest-decile share D0 0.100 … D4 0.317).
3. **Bank limit.** Replace the fixed cap with a bank limit sampled per trajectory. Its prior comes from the maximum bank in each Boeing trace, widened to cover the leave-one-out spread (57.3–62.4°), with a tail to 90°. Keep the fixed 90° cap and the fitted 52.5° cap as declared sensitivities. Report the >45° and 10–45° shares and ln Z under each. Design note and smoke first; post the predictions.
4. **Onset prior for B.** Add a uniform-onset (22:41–00:11) sensitivity beside the fuel-tied prior. Coordination reweighting of run I gives: D0 B share 0.108→0.225 (0.119–0.464 over seeds); D2/D4 unchanged, because the pre-00:11 share is ≤0.002. Confirm by a direct run at run-J scale, and report B with both priors.
5. Do not re-run the 22:41 asymmetry arm (immaterial, ≤0.031 nat).
