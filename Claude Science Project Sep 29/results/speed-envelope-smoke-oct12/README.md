# Speed-envelope smoke (core, 12 Oct 2026, 00:20-00:50Z, 2 threads)

Free flight, run D free stack without look-ahead (`run.json` config_paths), 4 seeds x 420k particles. **Unconverged at this scale**: split-half far below the 4-seed floor 0.896 in both arms.

- **A:** current model. Cruise Mach 0.73-0.84 (Davey Table 8.2), no cruise CAS clip; early phase 0.45-0.87 within 210-330 KCAS to 18:40.
- **B:** Pete's ruling. Early phase unchanged; cruise 0.70-0.87 within 210-330 KCAS (`config/sensitivity/early-families/speed-envelope-throughout.toml`, engine 3c4ceeb3).

| | A | B |
|---|---|---|
| log Z (log mean exp over seeds) | -135.17 (seed sd 1.12) | -136.10 (seed sd 0.26) |
| split-half, mean (range), 6 partitions | 0.627 (0.574-0.683) | 0.590 (0.528-0.658) |
| worst epoch, worst ESS fraction | m0011, 0.0017 | m0011, 0.0030 |
| distinct parents at m0011 (fraction, median over seeds/modes) | 0.76 | 0.78 |
| 00:19 median (2.5-97.5 %) | -37.41 (-37.93 to -29.66) | -37.02 (-38.18 to -32.82) |
| CPU seconds | 2108 | 1514 |

00:19 values: core, Davey both-BTO no-BFO 00:19 treatment.

**Prediction check** (PREDICTION.txt, filed 00:03Z; posted to CORE_STAGES during arm A):
1. log Z cost 0.5-2.5 nats: **met** (0.93), though A's seed spread (sd 1.1) means the difference is not resolved.
2. 00:19 median within 0.1 deg: **missed** (0.40 deg), within the noise of this scale.
3. Worst-epoch ESS no worse than half of A's: **met** (B 1.8x A).
4. Split-half within 0.03 of A: **narrowly missed** (0.037 lower).
5. Distinct parents at m0011 at least 0.5x A: **met** (0.78 vs 0.76).

**Reading.** The wider cruise range with the CAS clip shows none of the earlier failure mode, where the fuel cut discarded most of the weight. The bottleneck stays at 00:11 and is no worse. Its effect on the 00:19 position cannot be measured at this scale; that needs run I's full scale.

The final-epoch Mach in final.npy is post-exhaustion single-engine drift-down speed, not cruise Mach, so it is not reported here.
