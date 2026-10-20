# End of flight: the 00:19 start-up offset - what Holland's curve rests on, the 18:25 in-flight test, and proposals (9 Oct 2026)

End of Flight Module, architecture items (iii), (iii-b) and (ii)-widened (~19:50 and ~20:05 UTC, 9 Oct). **PROPOSALS ONLY. Nothing is built.**
Source grades: **A** peer-reviewed or official primary, read here with pages; **B** official, cited but not read
here; **C** online analysis (blog, wiki), included as argument, never as data.

## 1. What Holland's start-up offset is derived from (item iii)

Holland, "MH370 burst frequency offset analysis and implications on descent rate at end of flight",
arXiv:1702.02432v3 (**A**; journal version in IEEE Trans. Aerosp. Electron. Syst., 2018, DOI still to be confirmed in the ledger).
- **The seven calibration log-ons** (Sec. V-A, pp. 5-6; Table II, p. 7). Preceding power outages, as given in
  Table II: log-on 1: 381-442 min; log-on 2: 295-354 min; log-on 3: 35-95 min; log-on 4: 43-103 min; log-on 5: 35-92 min; log-on 6: 228-288 min;
  log-on 7 (the 18:25 in-flight log-on): 20-78 min, "probably ... approximately 63 minutes" (p. 6).
- **How the bounds were set.** The bounds are about 60 min wide because of the ground station's log-on-interrogation timer (p. 6).
  Footnote 10 (p. 6) adds that they assume the whole outage was a power outage.
- **Ground against flight.** Log-ons 1-6 were on the ground, and most used closed-loop Doppler compensation. Holland halves their
  decay for that reason (pp. 6-7). Log-on 7 is the only in-flight one, and Holland discards its first point
  (the R600 log-on request, 142 Hz) as untrustworthy because of a non-zero BER and low C/N0 (p. 5; Table II "first point untrustworthy").
- **The derived bounds** (Sec. V-B, p. 7): the R600 log-on is 17-136 Hz above steady state, the R1200 acknowledge 17-130 Hz above it,
  and the acknowledge is 0-6 Hz below the log-on.
- **What H1 assumes for the outage.** Holland's own Hypothesis 1 is an SDU outage of **"about one minute"** before 00:19:29 (Sec. VI and VI-A, p. 8).
  Footnote 13 (p. 8) concedes that "the extent of BFO decay due to OCXO warm-up would be less", and calls this
  "essentially covered within Hypothesis 2".

**Finding.** Pete's point is borne out by the primary text. The offset bounds come from outages of about 20 minutes to 7 hours
(the shortest bound in Table II is 20 min), six of them on the ground, and are applied to an outage of about 1-2 minutes. Holland
acknowledges the mismatch but does not model it: he leaves the shorter-outage case to H2's zero offset.

**Is a short-interruption variant supportable?** Partly, from general OCXO behaviour:
- Warm-up is a thermal process with a time constant of minutes. A typical OCXO needs a few minutes to some tens of
  minutes to settle from cold, and its frequency moves by ppm during warm-up (manufacturer application notes, **B/C**).
  After a short interruption the oven is still near its set point, so warm-up completes quickly (patent literature, **C**).
- I found nothing published on the 9M-MRO SDU's OCXO for outages of about 1-2 minutes. The SATCOM sub-group study Holland cites as [8]
  is internal and unpublished. The ATSB's Aug 2017 search-and-debris update (AE-2014-054) describes manufacturer tests on SDU warm-up drift
  (**B**). Its server stalled twice here, so that page is **NOT READ**, and it is the first thing to read.

**Proposal V-short (a declared alternative, not built).** The start-up offset scales with the oven's temperature deficit at power-on:
offset = f x Holland's bounds, with f = 1 - exp(-T_off / tau_oven). T_off is the outage implied by each descent (flame-out of the
generator-driving engine to log-on, minus the SDU boot time), and tau_oven is uncertain, a few to about 15 minutes. With T_off of about 1-2 min and
tau_oven of 5-15 min, f is about 0.1-0.3, giving offsets of about 2-40 Hz, between H1 and H2. This makes H1-versus-H2 a continuum
indexed by an oven parameter, instead of a dichotomy. It needs the ATSB 2017 manufacturer data to pin tau_oven; without that, tau_oven is
an analyst prior and must be labelled one.

## 2. The 18:25 in-flight test (item iii-b)

**The data**, Ashton et al., "The Search for MH370", J. Navigation 68 (2015) 1-22, Table 1, p. 3 (**A**):

| UTC | message | channel | BFO (Hz) |
|---|---|---|---|
| 18:25:27 | log-on request | R600 | 142 |
| 18:25:34 | log-on acknowledge | R1200 | 273 |
| 18:27:04 | user data (two) | R1200 | 176, 175 |
| 18:27:08 | acknowledge | R1200 | 172 |
| 18:28:06 | access request | R1200 | 144 |
| 18:28:15 | acknowledge | R1200 | 143 |
| 00:19:29 | log-on request | R600 | 182 |
| 00:19:37 | log-on acknowledge | R1200 | -2 |

**The published readings conflict:**
- **Ashton et al., Sec. 5.3, pp. 15-16 (A).** From other flights, the log-on request "did provide a consistent and
  accurate BFO measurement". They use the R600 at 18:25:27 and at 00:19:29, and discount 18:25:34-18:28:15 and 00:19:37.
  In their Table 9 (p. 20) they predict 256 Hz in level flight at 00:19:29 against 182 measured, and ascribe the -74 Hz to vertical
  motion (p. 21).
- **Holland (A).** He discards the 18:25:27 R600 point (BER, C/N0), and finds the R1200 sequence then follows the ground log-ons'
  simple decay (p. 5).
- **Davey et al., *Bayesian Methods in the Search for MH370* (DSTG 2015 draft; Springer 2016), pp. 7 and 83, Table 10.1 (A).** Every
  18:25 and 00:19 log-on BFO, on both channels, is treated as an unusable transient. The 18:25:27 R600 message is not listed at all.
- **Online (C).** On the Radiant Physics blog (Iannello, Feb-Mar 2017), the offset-manoeuvre explanation of the 18:25 BTO/BFO
  explains every value except the 273 Hz peak. Commenters argue that low C/N0 is unlikely to explain the 18:25:27 BFO, and
  that warm-up timing could depend on the oven temperature at power restoration. The MH370 wiki lists the non-zero BER as the reason for doubt.

**What a start-up-transient model predicts at 18:25.** The Ashton values settle to about 143 Hz by 18:28. The R600 at 142 Hz is
therefore already at the settled value. The R1200 acknowledge 7 s later is +130 Hz, and decays to +30 Hz by 18:27 and to about 0 by 18:28.
- A model with **one** transient shared by both channels, as in Holland's H1 (acknowledge 0-6 Hz below the log-on), reproduces 18:25 only
  if the 142 Hz R600 point is an error.
- The same model with the R600 point kept is contradicted by about 130 Hz.
- So Holland's [0, 6] Hz relation is a **ground** result that the only in-flight restart contradicts unless one datum is thrown away.

**Hypothesis S, "the R600 log-on request carries no start-up transient; the R1200 acknowledge does".** Proposed as a declared
alternative. Two mechanisms could produce it:
- **(S1) a rising limb.** The R600 burst is sent before the transient develops; the transient peaks within seconds and then decays.
  This needs a sub-10-second rise, which is hard to square with oven thermal time constants of minutes.
- **(S2) channel- or mode-specific behaviour.** The log-on request is sent before a frequency or compensation state that the
  acknowledge then uses: a synthesiser or AFC update, or the change of Doppler-compensation mode Holland discusses (p. 6). No primary
  source documents such a mechanism; the online discussion (C) raises it.

**What S predicts at 00:19.** The R600 at 00:19:29 (182 Hz) is then a clean BFO: with Holland's 1.7 Hz per 100 ft/min (p. 8) and
Ashton's 256 Hz level prediction, that is about 4,350 ft/min of descent. The R1200 at 00:19:37 carries a positive transient of
0 to about 131 x f Hz. Crude kinematics on one track:

| reading | descent 00:19:29 | descent 00:19:37 | mean vertical acceleration |
|---|---|---|---|
| no transient (H2) | 4,350 ft/min | 15,200 ft/min | 0.70 g |
| S, 18:25 amplitude (+131 Hz) | 4,350 | 22,900 | 1.20 g |
| S, half amplitude | 4,350 | 19,000 | 0.95 g |
| Holland H1, mid-range offsets | 8,850 | 19,500 | 0.69 g |

So **182 Hz is consistent with S**, which then reduces to H2 at 00:19:29. S with the full 18:25 amplitude needs a downward acceleration of
about 1.2 g at 00:19:37, i.e. negative load factor: a push-over, not a spiral. That is possible but extreme, and the
Boeing-checked simulator is the right judge of it. S with f of about 0.1-0.3 (Proposal V-short) is close to H2.
The 18:25 test therefore argues against H1 as Holland specifies it, and for H2 or S. It cannot separate H2 from S at 00:19:29,
because they agree on the R600.

**Proposal.** Declare S (R600 no offset; R1200 offset U[0, 131 f] Hz) as an option beside H1 and H2, scored by core's existing BFO-model
machinery. It is a `terminal.bfo_models` entry (core config) plus nothing in this module. I will write the parameter block for core
once Pete agrees, and grade every value as above.

## 3. Is sampling limiting (item ii, widened)?

The survivor diagnosis (`results/eof-two-burst-oct09/`) found the surviving descents interior to the prior. It did not show that the
fast transitions are sampled densely enough. Two tests are proposed; the first is cheap and runs on the existing code:
1. **Within-parent saturation.** Re-run only the top 200 parents of each two-burst arm with 1,024 children each, instead of 32 descents. If ln Z
   rises materially, the within-parent descent sampling (the fast transitions after fuel exhaustion and the second flame-out) is
   limiting. If it stays put, the limit is the hand-off. About 200k descents per arm per seed, minutes not hours. It needs a filtered
   hand-off snapshot, written inside the module's run directory.
2. **Coverage of the transition.** On the 6-DOF ensemble, map which (vertical rate at 00:19:29, vertical rate at 00:19:37) pairs are
   kinematically reachable from each 00:11 state across the first and second flame-out (asymmetric thrust, autopilot
   disconnect at the second flame-out, RAT, stick-fixed free dynamics). Then check that the fast model's proposal covers that
   reachable set with a declared defensive floor.

**How the fast model will cover the transitions.** It is fitted to a 6-DOF ensemble that samples:
- the time between the first and second flame-out;
- the autopilot state at each flame-out (Boeing: glides keep the autopilot through the first and lose it at the second;
  dives lose control at the first);
- the trim and residual bank at the loss of control.

Each descent is then a draw of those inputs pushed through the fitted reduced dynamics. These are the same mechanisms the Boeing runs show,
so sudden changes in descent rate are produced by the physics rather than imposed as profile shapes. The proposal over the inputs keeps a
defensive mixture with the prior, as in the stopgap, but with core request 9 in place so the weights are unbiased.

## 4. What `inflated` adds (Pete's question)

`inflated` replaces Holland's start-up model with an independent, zero-mean error on each burst, sd 34 Hz, the spread of his
17-136 Hz range divided by sqrt(12) (`config/integrated.toml`). It keeps the size of Holland's uncertainty but drops three of his
assumptions:
- that the offset is positive;
- that it is shared by the two bursts, i.e. the acknowledge sits 0-6 Hz below the log-on;
- that its range is fixed by the ground log-ons.

It therefore asks whether the two 00:19 bursts are informative if one says only that they are noisy. On reference-289 they are.
`inflated` has the highest evidence of the three BFO models on every burst set (`results/eof-two-burst-oct09/`): both bursts, `other`,
ln Z -23.17 against -23.93 (no-offset) and -24.27 (startup-offset). It still requires a steep descent, because 182 and -2 Hz sit
-74 and -258 Hz from level flight against a 34 Hz sd. It is the project's own sensitivity, and comes after Pete's four priorities.

## Reading list, in order

1. ATSB AE-2014-054, *MH370 - Search and debris examination update*, Aug 2017, section "7th arc BFO analysis / Oscillator warm-up
   drift": the manufacturer's warm-up tests (**B, not yet read**).
2. Holland 2018, journal version: confirm that the pages match v3.
3. Malaysian SIR (2018), the SATCOM appendix, for any statement on the 18:25:27 R600 BFO.
