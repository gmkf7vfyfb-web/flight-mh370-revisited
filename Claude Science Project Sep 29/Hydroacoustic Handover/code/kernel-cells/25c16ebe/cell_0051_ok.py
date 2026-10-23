# --- K. Pitfalls additions ---
ed("""- Do not import Holland's descent-rate bounds as a constraint. They are conditional on the transient
  assumption this project declines to treat as established, and importing them would kill the
  deliberate-descent branch by assumption rather than by evidence.
""",
"""- Do not import Holland's descent-rate bounds as a constraint. They are conditional on the transient
  assumption this project declines to treat as established, and importing them would kill the
  deliberate-descent branch by assumption rather than by evidence.
- **Holland's bounds are published by hypothesis, and the separation is routinely lost in
  quotation.** At 00:19:29 they are 3,900–14,800 ft/min under the satellite-data-unit-restart
  hypothesis against 2,900–6,800 ft/min under the no-warm-up hypothesis, with an 8 s mean downward
  acceleration of 0.68 g. §7's declared-alternative structure is already the right vehicle; compare
  against the **matching** hypothesis, never the merged range, and say which in every figure.
- **None of the ten Boeing cases is in a steep descent as the 7th arc is crossed.** So Boeing's own
  simulations of uncontrolled flight after dual fuel exhaustion and the descent rate derived from
  the 00:19 offsets **do not agree with each other**, a contradiction inside the official material
  rather than between it and this project. Report it as a result of the study; do not reconcile it,
  and do not let the steep arm inherit the authority of the Boeing simulations it does not
  reproduce. This is the most important framing fact available for the paper.
- **Beware the asymmetry a fit failure creates.** The steep, high-energy region of the envelope has
  been found, widened and well sampled because the 00:19 data kept pressing on it. The shallow,
  long-glide and sustained-low-altitude regions have had no comparable pressure applied, so their
  coverage reflects what nobody was forced to fix. A comparison between "a steep dive fits 00:19"
  and "a shallow approach does not" is not a comparison between two equally explored hypotheses
  until §2 rule 12 has been run and its answers closed.
""", "K pitfalls")

# header note
ed("""# End of flight — mission and master prompt

Supersedes `ISO Sept 28 Status/threads/master-prompts/end-of-flight.txt`, which remains correct on
physics and calibration and is stale on build status and evidence handling.""",
"""# End of flight — mission and master prompt

**Version 5, 13 October 2026.** Revises version 4 of 7 October against the audit of run I and
run-i-dive (`results/eof-audit-2026-10-13.md`, `results/eof-audit-pushover-addendum.md`) and the
independent literature pass (`results/eof-published-benchmarks.md`). Twelve changes, listed in §0.
Version 4 was six days stale by the time the first full sweeps were reviewed and told a reader the
model did not exist; §3 is now updated per sweep rather than per revision.

Supersedes `ISO Sept 28 Status/threads/master-prompts/end-of-flight.txt`, which remains correct on
physics and calibration and is stale on build status and evidence handling.""", "header")
print(EDITS)
