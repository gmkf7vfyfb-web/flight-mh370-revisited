# End of flight: Bayes factors for the five core 00:19 options on the SAME data (core (b), 10 Oct 2026)

Architecture ruling ~15:45 -0600, item 3. Every option is scored on the same data:
D_00:19 = {R600 BTO, R600 BFO, R1200 BTO, R1200 BFO, log-on time}.
- An option either scores an observation with its nominal likelihood, or treats it as **anomalous**: a declared broad, proper, uniform density
  over that observation's feasible range.
- The options then have defined Bayes factors against each other.

**Inputs.** The per-family 00:19 evidence factors of `results/eof-family-evidence-oct10` (with `+alive`, seed means), which already carry the
normalising constants of the nominal likelihoods. Families are mixed by core's P(family). Code: the cell in this note's lineage; the
per-setting table is in `same-data-bf.json`.

**Labels:**
- core (b), split-half NOT converged; two-tank bookkeeping only;
- **rapid descents above 6,500 ft/min and unloading not reachable by the model** (architecture ~15:45 item 4: this applies to every H1/H2
  number);
- **H1/H2 not yet estimable** (within-parent sampling, smoke 2).

**Anomalous densities** (central value, with sensitivities):

| observation | central width | sensitivities | basis |
|---|---|---|---|
| BFO | 700 Hz | 350, 1,400 Hz | the feasible range at the 7th arc: level flight about +260 Hz to a ~15,000 ft/min dive about −260 Hz (17.6 Hz per 1,000 ft/min) |
| R1200 BTO, scored by no option | 20,000 µs | 2,000, 60,000 µs | a corrupted value (raw 49,660 µs) has no kinematic range |
| log-on time under cause `other` | 3,896 s | 1,800, 7,200 s | uniform from 00:11 to 01:15:56 |

The R1200 BTO cancels between the options; it matters only for Held Out and R600 BTO Only.

| 00:19 option | ln BF against Held Out (central) | range over 27 width settings | per family at central (free / Davey dynamics + radar / descent-climb / routes) |
|---|---|---|---|
| 00:19 Held Out | +0.00 | +0.00 to +0.00 | +0.00 / +0.00 / +0.00 / +0.00 |
| 00:19 R600 BTO Only | +4.20 | +1.90 to +5.30 | +4.21 / +4.11 / +4.27 / +4.31 |
| 00:19 R600 BTO + Raw BFO | +4.08 | +1.09 to +5.88 | +4.00 / +4.00 / +4.47 / +4.26 |
| 00:19 Holland H1 | +0.34 | -4.12 to +3.44 | +0.03 / -0.37 / +1.41 / -0.01 |
| 00:19 Holland H2 | -0.77 | -4.45 to +1.72 | -0.80 / -0.90 / -0.49 / -0.78 |

**Reading.**
1. **The R600 BTO is strongly supported as a real observation:** ln BF +4.2, and at least +1.9 at every width setting. The trajectories
   selected by the data to 00:11 predict it far better than an uninformative value would. **The data favour using it.**
2. **The raw R600 BFO is indeterminate.**
   - Adding it moves ln BF by −0.81 to +0.57 depending on the BFO width: −0.12 at the central width.
   - The posterior-predictive check agrees: the observation lies at the 1-3 % tail (`results/eof-postpred-0019-oct10`).
   - Neither using nor discarding it is favoured by the evidence.
3. **Holland H1 and H2 are indeterminate, and not yet estimable.**
   - Their Bayes factors span −4.5 to +3.4 over reasonable widths.
   - Their nominal parts are parent-limited and rest on a model whose reach excludes the push-over they need.
   - **No conclusion is drawn.**
4. **The results agree across the four core families** to within about 0.5 (estimable options), so this is not a convergence artefact.

## COVERAGE (architecture ruling 15:45 -0600, item 6)

- **(a) Feasible set:**
  - 777-200ER descents from cruise to the surface, from planned descents to uncontrolled dives;
  - bank to the overbank;
  - vertical speeds to about −60,000 ft/min (Boeing App. 1.6E: V_D exceedances, dives to about −58,000 ft/min);
  - load factors at least from about 0.3 to 2.5 g (structural);
  - one-engine flight between the flame-outs;
  - deliberate push-overs within the g limits.
- **(b) The model's reach** (point mass):
  - commanded rates ≤ 6,500 ft/min with an 8-s lag;
  - free flight at a fixed lift coefficient that **cannot unload** below n·cos φ ≈ 1 except through bank (divergent spiral, cap 90°);
  - no autopilot, TAC, RAT or electrical-configuration states;
  - **no one-engine phase after the takeover** (core request 11);
  - no controlled push-over;
  - pitch at contact not modelled (flight-path angle stands in).
- **(c) The proposal's coverage:** per option, the effective parents and impacts are in `results/eof-family-evidence-oct10` and the sweep's
  `summary/`.
  - Estimable: Held Out, R600 BTO Only, R600 BTO + Raw BFO. Summed over 4 seeds per stratum: ESS ≥ 224,000 rows and ≥ 80,000 effective
    parents.
  - **Not estimable:** H1, 34-125 effective rows; H2, 64-106.
- **Gaps, and their status:**
  1. Unloading (reach): the 6-DOF gate. Refit queued under the heavy lock.
  2. Commanded rates above 6,500 ft/min and a controlled push-over (reach): ruling item 4, after the system sequence.
  3. The Boeing system sequence (reach): next in my sequence; partly blocked on core request 11.
  4. The one-engine phase after the takeover (reach): core request 11.
  5. Within-parent sampling of the push-over region (coverage): an exact targeted sampler needs Pete's go, and core request 9.
  6. Pitch at contact (reach): accepted for pass 1 if labelled.

- End of flight
