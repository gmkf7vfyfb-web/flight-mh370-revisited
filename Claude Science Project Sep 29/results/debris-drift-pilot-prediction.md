# Drift pilot: the prediction, stated before the compute is spent

Ocean drift module, 9 October 2026, ~01:30 UTC. Brief section 5 asks for a prediction before the
pilot runs. This note is committed before any pilot trajectory has been integrated, so that the
result can be read against it rather than rationalised after it.

**The run it refers to** is `engine/hypotheses/debris-drift/pilot.toml` on `hypothesis/debris-drift`
(commit `4993171`):
- 1,709 main-band nodes (99% coverage, 10 NM spacing, 100 NM margin, extent from no-exhaustion-prior
  at 00:19:37, 295.66° prior);
- 3,334 particles per node per motion class;
- the CSIRO-system arm on GLORYS12 + ERA5 (ruling D-b), K = 248 m²/s;
- G1 detection blocks: six segments x three periods, levels ln ν ~ N(ln 0.1 / ln 0.5 / ln 1, 1);
- exponential discovery delay with a 60 d mean;
- beaching read from GLORYS12 land-mask stranding (PROVISIONAL).

## The three numbers, and what I expect

1. **Throughput.** 5-7 x 10⁶ field evaluations per second per thread, as ocean transport measured on
   the same field. With two fields (current, wind) at two RK2 stages, that is about 1.5 x 10⁶
   particle-steps per second per thread, so about 1 h at 12 threads.
2. **Arrival probability per segment**, per particle by the window end, for a main-band source:
   - S3 southern Mozambique and S4 South African south coast: 10⁻³ to 10⁻², the large western
     coasts downstream of the South Equatorial Current and the Agulhas.
   - S1 Réunion and S2 Mauritius-Rodrigues: 10⁻⁴ to 10⁻³, small islands.
   - S5 north-east Madagascar and S6 Pemba: 10⁻⁴ to 10⁻³.

   **At 3,334 particles per class, I expect some nodes to be Monte Carlo unresolved** for the finds
   whose locality and timing are jointly rarest: Pemba, Rodrigues, Antsiraka. The unresolved fraction
   is itself a measurement; it sets the production particle count.
3. **How fast relative likelihood changes with source separation.** I expect the ln-likelihood
   surface, once its Monte Carlo noise is removed (split-half), to change by less than one unit over
   50 NM inside the main band. The correlation length should then exceed the impact posterior's
   own 50% width (0.85° of latitude, about 51 NM).

## The scientific prediction

**Drift reweights the shoulders and the north of the main band, not the mode.** Two lines of
earlier evidence say so:
- the Davey reproduction (+2.75 NM, with the mass shift in the northern tail);
- CSIRO's own reading, that arrival off Africa only after December 2015 favours sources south of
  about 32°S (Part II, p. iii).

Specifically:
- across 35-40°S the drift likelihood varies by less than a factor of e;
- it falls by more than a factor of e north of about 33°S, where arrivals in Africa come too early
  for the observed discovery dates;
- the median of the updated posterior moves by less than 10 NM.

**What would falsify this:**
- a variation of more than one ln unit over 50 NM inside the main body, resolved above split-half
  noise; or
- a likelihood that rises northward through 33°S.

Either outcome would mean the evidence can do more than the prediction allows, and the pilot would
be reported that way.

**What the pilot cannot say.** It is a pilot. It is not split-half stable by construction: one
diffusivity, one product, PROVISIONAL beaching. Its likelihood surface is not to be quoted as
evidence.

— ocean drift
