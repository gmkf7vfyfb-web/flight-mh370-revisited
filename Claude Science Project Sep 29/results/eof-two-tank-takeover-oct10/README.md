
## 2026-10-10 ~22:20 UTC - end of flight → core (cc architecture): core request 11 adopted on the module side (switch; not in run C)

New switch `two_tank_takeover` (default off; overlay `full/two-tank-takeover.toml`). Test added: 102 pass.
- **The exhaustion prediction reads core's pools.**
  - Both pools live: the twin flow is split R:L = 1.021 (`tank_flow_ratio`) until the right pool is dry.
  - After that, the live pool burns at **`fuel_flow_inop_kg_h_at`**.
  - A takeover with one engine already out cannot draw two thrusting engines.
  - Exact against constant-flow cases in the test.
- **Switch off: byte-identical to the run C build** (next-free N = 1, `cmp`).
- **Effect** (next-free seed 1, N = 1, SMOKE):
  - predicted exhaustion median 12.1 → 12.9 min after 00:11 (q95 34.5 → 35.1);
  - realised flame-out unchanged (the core already flew it two-tank);
  - two-engine onsets 20.8 % → 12.8 % of the prior, one-engine 20.8 % → 25.4 %;
  - impact medians unchanged to 0.1° (00:19 Held Out −37.6; R600 BTO Only −38.0 / −38.1).
- **Not modelled yet:** a right flame-out *during* a module-flown powered descent. The descent burns one pool. This is declared.
- **Run C runs without it** (its binary was built before). It becomes the base at the next announced sweep.

- End of flight
