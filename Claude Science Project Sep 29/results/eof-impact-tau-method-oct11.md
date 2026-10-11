# Impact energy-transfer duration (τ90): first-order water-entry model, `impact_tau_method = 1` (end of flight, 11 Oct 2026)

**METHOD NOTE, posted before any column is written** (architecture ruling 20:35 -0600 10 Oct, item 2, delegated by Pete, provisional).
Conventions are those of `results/eof-impact-energy-method.md` (system = airframe plus fragments from first water contact; τ90 =
t95 − t05 of cumulative mechanical energy transfer; nothing after the initial entry event counts). The model uses only the contact
state - speed v, flight-path angle γ, mass m - and declared random parameters. It never reads the family label.

## 1. Two regimes and a blend
Let θ = |γ| at contact.

**Shallow entry (ditching-like), θ ≤ 10°.** The airframe decelerates along the surface. First-order model: constant mean longitudinal
deceleration ā from v to rest, so the transferred fraction is F(t) = 1 − (1 − t/T)², T = v / ā. Then t05 = 0.0253 T, t95 = 0.776 T,
**τ90 = 0.751 v / ā**, peak rate P = m ā v at contact.
- ā is drawn per row, **U[0.75 g, 3.0 g]**, an AVERAGE deceleration. Basis (calm-water dynamic-model ditching tests at NACA Langley
  tank no. 2): maximum longitudinal decelerations for large transports of about 1.7 g (Constellation with Speedpak, NACA RM SL9H05a)
  and about 4 g (Constellation, Fisher & Morris), about 3 g (A-26); a modern civil-aircraft model test peaks at about 1.6 g (Chinese J.
  Aeronautics 2024, S1000936124004291); NACA Report 1347 (Fisher & Hoffman) derives average decelerations from landing speed and
  run length and notes that severe ditchings may exceed 10 g. Average is below maximum, so the range is set below the maxima.
- Declared limit: calm water; a dive-in after a run (the model tests' "dive violently" outcome) is not separated; it falls inside the
  upper part of the ā range, not as a second pulse.

**Steep entry, θ ≥ 30°.** The airframe crushes and fragments progressively at the water surface; the dynamic pressure at the crush
front (ρ_w v² ≈ 10-100 MPa for 100-300 m/s) far exceeds the airframe's crush strength, so the rear of the aircraft keeps nearly its
contact speed until the crush front reaches it. This is the progressive-crushing picture of the Riera aircraft-impact force model
(Riera, Nucl. Eng. Des. 8, 1968), applied to a water target. Energy transfer is then close to linear in time over the crush, so
**τ90 = 0.9 L_eff / v**, t05 = 0.05 L_eff / v, peak rate P ≈ KE v / L_eff.
- L_eff is drawn per row, **U[0.5, 1.0] × 63.7 m** (777-200ER length): the lower half allows wings, engines and tail to separate and
  stop transferring early.
- The deceleration of fragments in the water after the crush front has passed (the cavity phase, a time scale 2m_f / (ρ_w C_D A_f v)
  of about 0.05-0.1 s for a fuselage section) is shorter than L_eff / v and is not added (declared).

**Blend, 10° < θ < 30°:** τ90 = exp((1 − w) ln τ_shallow + w ln τ_steep) with w = (θ − 10°)/20° (log-linear in θ), same for t05, t95 and
the peak rate. Declared and arbitrary within the band; a sensitivity uses the band edges 5°-45°.

## 2. Other columns
- `impact_energy_transferred_j` = contact kinetic energy (both regimes run to rest or to complete crushing; the energy left in intact
  floating pieces is not modelled; declared upper bound).
- `energy_transfer_n_pulses` = 1 (single-pulse model; successive fuselage, engine or wave contacts are not resolved; declared).
- `energy_transfer_peak_rate_w` as above; `impact_tau_method` = 1.
- Rows with contact speed above 212 m/s (G13: no structural limit) carry τ but stay in the flagged set; when the in-flight breakup end
  state exists (ruling 1(A)), τ will be computed per fragment class.

## 3. What this gives (order of magnitude)
- Ditching at 70 m/s: T = 2.4-9.5 s, **τ90 ≈ 1.8-7 s**.
- Steep entry at 200 m/s: **τ90 ≈ 0.14-0.29 s**; at 300 m/s, 0.10-0.19 s.

## 4. Delivery for run C (pass 1)
Run C's columns are NaN (the module binary predates this note). τ will be delivered as a **sidecar per seed**
(`next-run-c/<stratum>/seed-k/tau90_v1.npz`: τ90, t05, t95, peak rate, regime weight w, the two drawn parameters), computed in Python from
the compact columns (speed from the velocity components, `flight_path_angle_deg`, `mass_kg`) with draws seeded by stratum, seed and row,
so it is reproducible. The module's Rust columns follow at the next announced sweep with the same formulas.

## 5. Uncertainty and validation
No full-scale validation exists for a large transport at either extreme. The ranges are wide on purpose. Hydroacoustics shows its result
against its own scenario τ as a sensitivity (ruling item 2). Literature closest to the problem, for a later refinement: Spinosa, Grizzi &
Iafrati (high-speed ditching with cavitation and ventilation, arXiv:2408.06952); Spinosa, Broglia & Iafrati (fuselage water landing,
arXiv:2208.01504).

- End of flight
