---
name: eof-no-unpiloted-assumption
description: "Pete's correction — never treat unpiloted end-of-flight simulations or Holland's BFO reading as anchors for what happened"
metadata:
  node_type: memory
  type: feedback
  originSessionId: b321a56a-4f19-4c04-acbd-d5031b94cf81
  modified: 2026-09-25T23:33:37.573Z
---

Don't call Boeing's end-of-flight simulator runs or ATSB's "within 15 NM of the arc" result "behavioural anchors". Both assume no human control after flame-out, which Pete considers an unsupported, essentially non-falsifiable conditional hypothesis. ATSB's result also rests on Holland's BFO analysis, which assumes:
- a 60–90 s power cycle produced the same start-up transient as a long cold start;
- that transient is what explains the 00:19 BFO values.

**Why:** Pete corrected this on 2026-09-25. A core aim of the research is realistic uncertainty in flight time after fuel exhaustion, distance and impact energy, without relying on unprovable assumptions.

**How to apply:**
- Use the Boeing runs only as physics calibration data for our own open model, not as a scenario prior.
- End-of-flight scenario priors cover piloted and unpiloted cases without preference.
- The 00:19 BFO measurement model carries alternatives (no offset, offset model, inflated error).
- Results are reported per assumption. See [[thread-coordination]].
