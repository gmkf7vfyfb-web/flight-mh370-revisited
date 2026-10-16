# Core request 21: fuel-flow factor on extrapolated steps (kappa_x) — gated and smoked

Job 967bb8ef, branch core-request21 (2e9366b, now cherry-picked onto claude-science-sep29),
bin-2e9366b. Design and prior: engine/config/sensitivity/request21/README.md.

**Gates (factor off):** unit tests 32 + 41 pass, including the three new tests (not serialised when off;
scales only extrapolated steps; draw is last and has the prior). Gate B 10/10 files and gate C 4/4 files
byte-identical to the 15 Oct references (ln Z −87.51501896471403, −100.03202195409557). regress-seed1
−97.51251428262529, equal to the reference.

**Smoke:** Davey posterior with fuel tracked but not constraining (ff-internal chain), 2 seeds x 1.75M.

| kappa_x prior | Dry before 00:10:59 | Dry 00:10:59–00:19:29 | FE 5% | FE median | FE 95% | ln Z |
|---|---|---|---|---|---|---|
| off | 0.918 | 0.044 | 22:51:02 | 23:32:43 | 00:16:16 | −97.0852 |
| N(1.0, 0.046) (production, PROVISIONAL) | 0.918 | 0.041 | 22:50:11 | 23:32:18 | 00:16:47 | −97.0852 |
| N(1.027, 0.043) (sensitivity) | 0.937 | 0.038 | 22:42:42 | 23:27:52 | 00:13:01 | −97.0852 |

ln Z is identical by design: fuel does not constrain this chain, and the extra draw does not change the
propagation random streams (trajectories are identical; only the fuel state differs). In run J fuel
constrains, so kappa_x will act through the fuel likelihood.

STE100 note: the new fuel factor works. When it is off, results do not change at all. When it is on,
only the fuel changes. The shifted version makes the fuel run out about 5 minutes earlier.
