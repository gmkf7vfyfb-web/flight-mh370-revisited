# 18:25:27 R600 burst held out: posterior predictive check (15 October 2026)

**Pete's ruling (15 Oct evening, supersedes 12 Oct).** Run J uses the two settled R1200 BFOs (18:28:05 at 144 Hz
and 18:28:14 at 143 Hz, as in run I). It HOLDS OUT the 18:25:27 R600 burst, BFO and BTO, and checks the burst
against the output.
- **Pete's prediction, recorded before this check:** it will fit very well with the selected trajectories.
- **Pete's note on the signal.** The low C/N0 and BER 5 are likely a collision on the network. That affects
  power; it may or may not affect the BFO.
  - The log fits that reading: received power was normal to high (−52.3 dBm) while C/N0 was low.
- So run J adds NO new epoch. Its observation set equals run I's, with the BFO sd at 4.32 Hz.

**Method.** The log predictive density of a held-out datum y given all other data D is
ln p(y | D) = ln Z(D ∪ y) − ln Z(D). This holds whatever the datum's position in the filter. The 12 Oct smoke
(job f529c67a, 4 seeds × 420k, BFO sd 7 Hz, run-I-era stack; `results/run-i-oct12/r600-1825-smoke.csv`) ran:
- arm A: no R600;
- arm C: + R600 BFO;
- arm B: + R600 BFO and BTO.

So ln p(BFO | D) = Z_C − Z_A, and ln p(BTO | D, BFO) = Z_B − Z_C. The best attainable value (zero residual, no
trajectory spread) is −½ ln(2π σ²), with σ² = 7² + 5.4 Hz² (the marginalised bias variance) for the BFO and
62² µs² for the BTO.

| family | ln p(R600 BFO given the rest) | best attainable | shortfall | equivalent residual | ln p(R600 BTO given the rest) | best | shortfall | equivalent residual |
|---|---|---|---|---|---|---|---|---|
| free | −3.70 (s.e. 0.40) | −2.92 | 0.78 nat | ≤ 1.25 σ | −5.37 (0.47) | −5.05 | 0.32 nat | ≤ 0.80 σ |
| waypoints | −2.98 (0.52) | −2.92 | 0.06 nat | ≤ 0.35 σ | −5.67 (0.61) | −5.05 | 0.62 nat | ≤ 1.12 σ |

The "equivalent residual" is √(2 × shortfall), an upper bound, because part of the shortfall is trajectory
spread, not residual.

## Reading
- **The held-out R600 BFO fits the posterior of the other data well**: within 0.06 nat of a perfect fit for
  waypoints and 0.78 nat for free flight. The held-out R600 BTO fits within 0.3–0.6 nat. **Pete's prediction holds**
  at smoke scale.
- So the weak signal (C/N0 30.28 dB-Hz, BER 5) shows no sign of a corrupted frequency or timing measurement.
- The burst still moves the free-flight 00:19 median by 1.4° north when INCLUDED with its BTO (arm B −35.62
  against arm A −37.02). That is information, not misfit: the data agree, and the burst narrows where free flight
  can be.
- **For run J.** Repeat this check at production scale on the final configuration (4.32 Hz), as a cheap
  companion: the repro family with and without the burst, 16 seeds each. It can also be run on any other family
  if wanted. Report ln p and the shortfall per family.
