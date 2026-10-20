# Davey et al. end-of-flight citation ledger

Retrieved and checked 2026-08-25. The local source is
`paper/paper.pdf`, SHA-256
`37554ca5f0c0ef14fddb825748d9f9dc9059a26563f783a3e4dfafcd0ced91b2`.
The official open-access HTML is used for independently addressable locators.

| Claim supported | Source | Locator | Located passage (short excerpt) | Status |
| --- | --- | --- | --- | --- |
| The main accident-flight filter did not carry a fuel constraint through its particles. Fuel could be applied after the position PDF, and broad fuel consumption informed the Mach range. | [Particle Filter Implementation](https://link.springer.com/chapter/10.1007/978-981-10-0379-0_8) | Section 8.3, assumption 4; HTML lines 189-190; local book p. 60 (PDF p. 73) | “Infinite fuel: the fuel constraints on the aircraft can be applied to the pdf afterwards.” | Verified |
| Davey et al. excluded the transient 18:25 and 00:19 BFOs from the main filter. | [Application to the MH370 Accident](https://link.springer.com/chapter/10.1007/978-981-10-0379-0_10) | Section 10.1, HTML line 75; section 10.3, line 127 | “the BFO values reported for these times cannot be used” | Verified |
| They nevertheless used both mutually inconsistent final BTO observations, with no preference, and let the filter find the best statistical fit. | [Application to the MH370 Accident](https://link.springer.com/chapter/10.1007/978-981-10-0379-0_10) | Section 10.3, HTML lines 128-129 | “we use both measurements and let the filter find paths that are the best statistical fit” | Verified |
| The particle filter ended with an aircraft-state PDF in the air at 00:19; descent was a separate transition kernel convolved with those particles. | [Application to the MH370 Accident](https://link.springer.com/chapter/10.1007/978-981-10-0379-0_10) | Section 10.5 and Eq. 10.1, HTML lines 138-145 | “The output of the particle filter is an estimate of the pdf of the aircraft state at 00:19.” | Verified |
| The published indicative end-of-flight kernel was not a per-particle 777 simulation: it was uniform to 15 NM and had a 30 NM Gaussian drop-off beyond that. | [Application to the MH370 Accident](https://link.springer.com/chapter/10.1007/978-981-10-0379-0_10) | Section 10.5, HTML lines 146-148 | “a uniform disc of radius 15 nm with a Gaussian drop off” | Verified |
| A separate cost-index sensitivity used Boeing lookup tables and an estimated time-varying weight as fuel was expended; the broader constant-Mach result was preferred. | [Application to the MH370 Accident](https://link.springer.com/chapter/10.1007/978-981-10-0379-0_10) | Section 10.7, HTML lines 170-173 | “an estimate of the aircraft weight, which varies over time as fuel is expended” | Verified |

## Audit conclusion

Davey et al. did not implement the proposed end-to-end fuel-state and
post-flameout simulator. Their principal particle filter assumed infinite fuel,
ended at the 00:19 airborne PDF, excluded both final BFOs, and then applied an
ATSB-advised radial descent kernel. The cost-index experiment is relevant
evidence that weight and fuel were considered in a sensitivity, but it is not
evidence that fuel exhaustion was a latent state or likelihood in the main
accident-flight posterior.
