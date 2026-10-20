# Item 1 — thrust asymmetry: rule-11 before/after on the 00:11 arm (14 Oct 2026)

**Label:** first section 00:11 arm only; second section the full joined V2 estimate with both arms flown with asymmetry. Uncontrolled-arm dynamics not calibrated (item 2).

BEFORE: the joined V2 00:11 arm (binary o13d, symmetric single-engine flight). AFTER: the same recipe, parents, seeds (1–8) and N = 8 with `smoke/asymmetry.toml` (binary o14, sha256 42e66f13…). Statistic per seed: the stage's own ln Σ w L with weights normalised within each run, the impact-latitude median, family shares; mean ± standard error over the 8 seeds of AFTER − BEFORE. The AFTER arm samples compensation off at 0.5 and is also shown re-weighted exactly to 0 and to 1 (`latent:asymmetry_compensation_off`).

| treatment | prior on compensation off | Δ ln Z, nat | Δ impact latitude median, deg | Δ A1 share | Δ A2 share | Δ B share |
|---|---|---|---|---|---|---|
| D0 | 0.5 (sampled) | -0.000 ± 0.001 | -0.003 ± 0.002 | -0.000 | -0.000 | -0.000 |
| D1 | 0.5 (sampled) | +0.001 ± 0.002 | +0.001 ± 0.002 | +0.001 | -0.000 | -0.001 |
| D2 | 0.5 (sampled) | +0.004 ± 0.007 | -0.007 ± 0.004 | +0.003 | +0.001 | -0.006 |
| D3 | 0.5 (sampled) | +0.010 ± 0.035 | +0.006 ± 0.018 | +0.007 | -0.004 | +0.006 |
| D4 | 0.5 (sampled) | -0.026 ± 0.013 | +0.007 ± 0.007 | +0.001 | +0.009 | -0.004 |
| D0 | 0 (always compensated) | +0.002 ± 0.002 | -0.000 ± 0.001 | -0.000 | -0.000 | -0.000 |
| D1 | 0 (always compensated) | -0.001 ± 0.002 | +0.001 ± 0.002 | -0.000 | -0.000 | +0.000 |
| D2 | 0 (always compensated) | +0.002 ± 0.008 | -0.006 ± 0.004 | +0.001 | +0.002 | -0.006 |
| D3 | 0 (always compensated) | +0.007 ± 0.038 | +0.006 ± 0.021 | +0.005 | -0.004 | +0.007 |
| D4 | 0 (always compensated) | -0.025 ± 0.013 | +0.010 ± 0.008 | +0.001 | +0.008 | -0.004 |
| D0 | 1 (never compensated) | -0.002 ± 0.001 | -0.006 ± 0.004 | -0.000 | -0.000 | -0.001 |
| D1 | 1 (never compensated) | +0.002 ± 0.002 | +0.001 ± 0.002 | +0.002 | -0.000 | -0.002 |
| D2 | 1 (never compensated) | +0.007 ± 0.006 | -0.008 ± 0.004 | +0.005 | -0.000 | -0.007 |
| D3 | 1 (never compensated) | +0.013 ± 0.033 | +0.006 ± 0.017 | +0.009 | -0.004 | +0.005 |
| D4 | 1 (never compensated) | -0.027 ± 0.013 | +0.005 ± 0.007 | +0.002 | +0.010 | -0.003 |

**Result.** On the 00:11 arm the asymmetry changes the stage evidence by at most 0.03 nat (D4: −0.026 ± 0.013, the only difference near 2
standard errors), the impact-latitude median by 0.01° or less, and no family share by more than 0.010, under every compensation prior. The
measured reason (smoke, 13–14 Oct): the live engine is mostly at idle in free flight (8–25 kN), where the uncorrected yaw rate is about
0.01°/s, and the held-path trim drag k C_nT² is a fraction of a drag count at cruise q.

**What this does not cover (gaps, named):** (2) roll from dihedral (C_l_β) is not modelled, so the asymmetry cannot start a spiral by itself; (3) C_n_β and
C_Y_β are 747 values (CR-2144), a declared type substitution; the trim-drag and sideslip-drag coefficients are modelling parameters.
Files: `rule11-asym-0011.json` (per seed and aggregate). Code: `smoke/rule11_asym.py`, `full/run_asym_0011.sh`.

## Joined V2 with asymmetry in both arms (22:41 arm run 17:35–21:40Z, Pete's go-ahead)

AFTER: the 22:41 arm (o14 + smoke/asymmetry.toml, otherwise the joined V2 recipe, deliberate onsets only, scored selection) joined with the AFTER 00:11 arm above, by smoke/joined_v2.py --seed k. BEFORE: the joined V2 production (results/eof-joined-v2-oct14). Mean ± standard error over 8 seeds of AFTER − BEFORE; compensation off sampled at 0.5.

| treatment | Δ ln Z, nat | Δ share from onsets before 00:11 | Δ A1 | Δ A2 | Δ B | Δ impact latitude median, deg |
|---|---|---|---|---|---|---|
| D0 | +0.001 ± 0.003 | +0.002 ± 0.003 | -0.001 ± 0.001 | -0.001 ± 0.002 | +0.000 ± 0.003 | +0.008 ± 0.009 |
| D1 | -0.005 ± 0.003 | -0.001 ± 0.002 | +0.000 ± 0.001 | +0.001 ± 0.001 | -0.002 ± 0.002 | -0.000 ± 0.002 |
| D2 | -0.002 ± 0.008 | +0.000 ± 0.001 | +0.003 ± 0.005 | -0.003 ± 0.005 | -0.000 ± 0.001 | -0.003 ± 0.005 |
| D3 | +0.014 ± 0.025 | -0.000 ± 0.000 | +0.009 ± 0.009 | -0.007 ± 0.008 | +0.001 ± 0.004 | +0.011 ± 0.013 |
| D4 | -0.011 ± 0.010 | +0.000 ± 0.000 | -0.002 ± 0.014 | +0.005 ± 0.014 | -0.002 ± 0.001 | +0.007 ± 0.008 |

**Result.** With the 22:41 arm included, every difference is within 2 standard errors of zero: |Δ ln Z| ≤ 0.014 nat, |Δ share| ≤ 0.009, |Δ latitude median| ≤ 0.011°. Thrust asymmetry, as modelled (no dihedral roll), does not move the joined V2 result. The onset-boundary statistic stays 0.00 % in every scored cell. Dihedral roll is therefore not needed for the general result at present; it remains a declared gap for the free-flight case with the lever set (Boeing's short cases), where round 3's turn rule stands in for it.
