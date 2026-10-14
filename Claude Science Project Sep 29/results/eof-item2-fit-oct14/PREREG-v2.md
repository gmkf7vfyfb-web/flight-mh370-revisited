# Item 2, round 2 — reach extension: design fixed BEFORE fitting (14 Oct 2026, ~10:40Z)

Pete's decision (14 Oct, after the round-1 leave-one-out failure): **extend the point-mass reach**, refit with the SAME approved
tolerances, repeat leave-one-out. This file fixes the additions, the parameter budget and the bounds before any round-2 fit is run.
Nothing below may change after the first round-2 fit is seen; any later change is a round 3 and is declared as such.

## Unchanged
Targets, tolerances (σ = tolerance/2), features and their measurement code, the gate rule (every case passes every applicable target out
of sample, plus P(right dive class) ≥ 0.5 and P(right direction) ≥ 0.5), initial conditions from the traces, the 4 Sobol draws of the
unfitted aerodynamic bands, the bank grid, the declared choices of round 1 (end reference 1,500 ft, mass 174 t, 3σ missing-feature
score, zero for a wrong class or direction), no per-case nuisance.

## Additions (each answers one measured round-1 gap)
1. **Lift–speed exponent n** (glide phugoid period). In free flight the lift coefficient is c_L,trim (V_loss / V)^n, so lift goes as
   V^(2−n); the phugoid frequency becomes √(2−n)·g/V (n = 0: Lanchester, the round-1 model). Stands in for the flight-control law's
   speed holding, which the point mass lacks. Bounds [0, 1.5].
2. **Path-rate damping k** (glide phugoid damping). Lift is set so that L = L0 − k·m·V·γ̇, i.e. L = (L0 + k W cos γ)/(1 + k cos φ):
   k > 0 adds damping, k < 0 removes it (n and k are applied per integration step, 2 s, as the production command is). Bounds [−0.5, 2].
3. **State-dependent dive trigger** (dive class). The free phase diverges with probability 1 / (1 + exp(−(EAS_loss − e0)/s)), EAS at the
   loss of control, instead of the state-independent `spiral_divergent_weight`. e0 bounds [150, 260] kt, s bounds [2, 40] kt.
4. **Divergent-spiral bank cap** (dive chord), fitted. Bounds [30, 90] deg.

## Parameter budget: 11 shared against 62 case-targets
spiral_doubling_s [3, 600], trim_cl_offset [−0.30, 0.10], windmilling_per_engine [0, 0.0015], rat_increment [0.0001, 0.0006],
residual_bank_deg upper bound [2, 60], residual_bank_left_probability [0.02, 0.98], n, k, e0, s, cap. (spiral_divergent_weight is
replaced by e0, s.)

## Production consequence
The additions go into the production model behind configuration (off by default, bit-identical without it). Only a fit that passes the
gate changes run.toml; a fit that fails is reported with its residual table as round 1 was.
— End of Flight Module
