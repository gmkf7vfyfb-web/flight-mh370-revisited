# Run-J item 6 check: BFO sd 7 / 4.3177 / 4 Hz on the pure reproduction (15 October 2026)

Pete's GO, 15 Oct. deskstar job ac952234, binary `bin-dbeb59e`, under the deskstar heavy lock.
- **Runs.** `davey2016-inmarsat.toml` + `config/sensitivity/bfo-sd-check/repro-bfo{7,432,4}.toml`. This is Davey's
  dynamics, priors and observations, with Inmarsat's satellite states and the 289.7° track. No fuel, speed
  envelope, radar or families.
- **Scale.** 4 seeds × 7M (Davey's per-seed count). 4.3177 Hz is Davey et al. (2016) Table 5.1, the larger
  in-flight value.
- **Files.** The full `summary.json` of each run is in this folder.

| BFO sd | shoulder 34.5–36.5 S | ln Z (4 seeds; seed sd) | magnetic heading + track | median 00:19 lat | 95% interval | overlap with Fig. 10.3 | split-half (floor 0.896 at 4 seeds) |
|---|---|---|---|---|---|---|---|
| 7 Hz | **0.078** | −97.128 (0.038) | 0.048 | −37.95 | −39.44 to −34.88 | 0.750 | 0.936 |
| 4.3177 Hz | **0.150** | **−96.570** (0.066) | 0.083 | −37.67 | −38.93 to −34.15 | 0.762 | 0.911 |
| 4 Hz | **0.179** | −96.797 (0.072) | 0.099 | −37.56 | −38.83 to −33.67 | 0.784 | 0.929 |

Davey's Fig. 10.3 shoulder (digitised) is 0.2406.

## Reading
1. **Our reproduction at Davey's own 7 Hz gives a shoulder of 0.078, about a third of Davey's 0.2406.** The
   deficit is in the reproduction itself, not in the production stack. A narrower sd raises the shoulder
   (0.078 → 0.150 → 0.179), but even at 4 Hz it stays well below 0.24.
2. **"Our 4 Hz shoulder matches Davey's 7 Hz shoulder" is a property of the production stack.**
   - The production-stack 4 Hz figure (0.2931) is 0.11 above the reproduction at 4 Hz (0.179).
   - The production stack at 7 Hz (0.1739) is 0.10 above the reproduction at 7 Hz (0.078).
   - So the fuel and early-flight stack adds about 0.1 to the shoulder at either sd, and the closeness to
     0.2406 is a coincidence of two effects.
   - The stated cause, a bias-drift term, is not active (see the run-J proposal).
3. **The data favour about 4.3 Hz over 7 Hz.**
   - ln Z at 4.3177 Hz is +0.56 nat against 7 Hz, and +0.23 nat against 4 Hz. The standard error of each
     4-seed mean is 0.02–0.04.
   - Treated as a Bayes factor on the measurement sd, this supports item 6's choice of 4.32 Hz on the
     evidence, not only on Table 5.1.
4. **The mechanism is as stated in the answers note.** A narrower sd moves weight into the magnetic modes
   (0.048 → 0.099), and those modes sit on the northern shoulder.

## Predictions (CORE_STAGES, before the run)
- **Shoulder at 7 Hz 0.10–0.20: MISSED (0.078, lower).**
- **+0.05 to +0.15 at 4 and 4.32 Hz: MET** (+0.100, +0.072).
- **Magnetic share rises: MET.**
- **The closeness is a property of our reproduction rather than the production stack: WRONG.** The
  reproduction is far below Davey at both sd values, and the production stack is what lifts the shoulder.

## What this leaves open
Why our reproduction's shoulder at 7 Hz (0.078) is a third of Davey's. `bfo-4hz.toml` records that the deficit
is already present in the BTO-only case. That points to the BTO side or to the prior and dynamics, and the next
diagnostic is the BTO-only case of the reproduction against Fig. 10.3's BTO-only curve. This is NOT ASSESSED here.
