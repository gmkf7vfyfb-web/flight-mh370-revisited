# --- J. Calibration gate ---
ed("""Calibrate against the 10 Boeing
engineering-simulator runs (1 Hz X/Y/altitude only; targets phugoid period, bank growth, time to
15,000 fpm, distance) and against Boeing's published range and endurance.
""",
"""Calibrate against the 10 Boeing
engineering-simulator runs (1 Hz X/Y/altitude only; targets phugoid period, bank growth, time to
15,000 fpm, distance) and against Boeing's published range and endurance.

**The uncontrolled-arm calibration gate.** The runs declare "6-DOF gate not passed" as a label and
proceed, which is the module inventing a gate the contract never defined. Define it here.

- **Passed** when the fast model reproduces the ten traces on all four targets with a per-case
  residual table published, the dive cases (3, 4, 5, 6, 10) included explicitly — they are tests of
  *uncontrolled dives* and are the only aircraft-specific validation data the uncontrolled arm has.
- **While unpassed**, the module may report impact *distributions* with the provisional labels
  attached, and may not report any impact *energy*, *attitude*, *flight-path angle* or
  *energy-transfer duration* as a physical prediction — only as a model output conditional on an
  uncalibrated descent. That restriction is heavier than it sounds and is the reason it is here: an
  independent literature pass on 13 October found **no retrievable source publishes an impact speed,
  flight-path angle, impact energy or energy-transfer duration for this accident**, per-case impact
  conditions having been withheld from the Boeing dataset. The trace fit is therefore not one
  validation among several; it is the only one available.
- **Current state.** Unpassed. The 6-DOF fit on the 747 aerodynamic base did not converge: joint
  misfit fell 4 per cent and the shared-physics stage made no progress at its evaluation cap. Where
  the 747-based reference cannot be made to converge, say so and fall back to per-case fitting of
  the fast model rather than leaving the arm labelled interim indefinitely. Transonic drag rise is
  required, because the steep arm routinely exceeds the crest Mach number.
""", "J calibration gate")

# --- B. Three-arm acceptance condition in deliverables ---
ed("""2. V1a, V1b and V2 as config-gated arms, with the hand-off epoch and the descent-onset support
   both set by config and empty onset support a legal setting.""",
"""2. V1a, V1b and V2 as config-gated arms, with the hand-off epoch and the descent-onset support
   both set by config and empty onset support a legal setting. **This is an acceptance condition,
   not an instruction.** No result may be reported as the headline comparison unless all three arms
   ran on the **same binary, the same core run and the same evidence columns**. The previous version
   described V1a as "nearly free, because the hand-off is built anyway", and the consequence was
   that every full sweep since has been V1a alone: a V1a-only sweep is reportable as "the impact
   distribution under this configuration" and licenses **no** statement about the descent hypothesis
   or about the checkpoint, which §1 already says and which should have been a rule.""", "B three-arm acceptance")

# --- G. Test 6: uniform-prior recovery ---
ed("""Ballistic energy conservation. Level-flight equilibrium. BFO vertical-speed sensitivity against a
finite difference. One synthetic-recovery test: generate the data from a known descent and check
coverage. Plus hand-computed fixtures.
""",
"""Ballistic energy conservation. Level-flight equilibrium. BFO vertical-speed sensitivity against a
finite difference. One synthetic-recovery test: generate the data from a known descent and check
coverage. Plus hand-computed fixtures.

**Test 6, added 13 October — prior recovery under the correction.** For every aimed or targeted
proposal component, show that **the sampling weight alone recovers the uniform prior on the aimed
latent over its full configured support**, and report the statistic in every run note that uses an
aim. This is the test that settles whether a targeted proposal shaped the answer, and the previous
version did not ask for it even though the module had built the machinery and passed it.

Report two things: the maximum absolute deviation between the weighted cumulative distribution and
the uniform one, and the corrected share inside the aim window beside the share a uniform prior
would give. Measured on run-i-dive, as the worked example of a pass: push-over rate deviation
0.0030 with aim-window share 0.6615 against 0.6567 uniform; push-over load floor 0.0041 with
0.1650 against 0.1667; stored mean importance correction 1.000178 ± 0.000693. Beside it, report the
*posterior* share under the informative 00:19 options — 0.9438 and 0.3995 respectively — because the
pair is the evidence of selection: a demonstrably uniform prior, and the data moving it.
""", "G test 6")
print(EDITS)
