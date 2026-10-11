# Physics item 2, Boeing's system sequence on the point mass: smoke results (end of flight, 11 Oct 2026)

**SMOKE (N = 1 child x 4 descents, one seed). NOT EVIDENCE.** Core run C `next-c-free` seed 1, m0011 hand-off, run C module recipe + trim at loss + bounded push-over (items 3 and 4), constraint `unpowered`. Binary `/tmp/mh370-eof-item2` (sha256 f3b5c321...). With the sequence off it equals the item-4 run in every existing column (byte-identical; one new latent). Labels: G13 (no structural limit); H1/H2 not estimable; PROVISIONAL.

## What item 2 is, on the point mass (`full/boeing-sequence.toml`)
- **Primary configuration (Boeing SIR App. 1.6E p. 8):** right tank dry first, TAC and autopilot hold the aircraft on the left engine (flown by the core to the takeover: s7 one-engine dynamics, s8 hold-then-taper; needs the two-tank takeover, core request 11); at the left engine's flame-out the autopilot disconnects: free flight with the trim at the state at loss (item 3), residual left rudder P(left) = 0.8, RAT drag (glide configuration), APU start and its log-on lag to the 00:19:29 R600.
- **Alternative configuration:** autopilot lost at the FIRST flame-out, the left engine running at a held lever setting U[0.5, 1.0] of full thrust until its tank is dry, then as above. New cells `flame-out-associated / one-thrusting / *`, appended after the existing 24 families (every existing index unchanged; only with the switch on). Prior probability: U[0, 1] hyper-parameter, proposal 0.5, exact re-weighting with `latent:ap_loss_config` (0 no draw, 1 primary, 2 alternative).
- Eligible: flame-out-associated onsets with both tanks live at the hand-off (24 % of the prior here). A parent with one tank already dry at 00:11 was flown by the core with the autopilot held, so it takes the primary configuration (declared conditional).

## Results

| run | push-over tail P(vertical-speed change <= -10,450 ft/min) | P(contact > 212 m/s) | ln Z R600 BTO Only | ln Z Raw BFO | ln Z H1 (eff. par.) | ln Z H2 (eff. par.) | Held Out median lat |
|---|---|---|---|---|---|---|---|
| items 3+4 (item-2 binary, sequence off) | 0.125 % | 13.2 % | -5.674 | -12.699 | -29.12 (7.6) | -23.94 (2.4) | -37.54 |
| + two-tank takeover | 0.127 % | 13.0 % | -5.673 | -12.772 | -30.36 (3.8) | -23.88 (4.7) | -37.56 |
| + Boeing sequence (two-tank + autopilot-loss configuration) | 0.142 % | 13.9 % | -5.705 | -12.694 | -30.36 (3.8) | -23.16 (5.2) | -37.51 |

Alternative configuration (autopilot lost at the first flame-out), sequence on: posterior share and ln Z as a function of its prior probability p

| option | posterior share | eff. parents | ln Z at p = 0 | p = 0.5 (marginal) | p = 1 |
|---|---|---|---|---|---|
| Held Out | 0.116 | 11805.4 | -0.04 | -0.05 | -0.06 |
| R600 BTO Only | 0.117 | 8369.2 | -5.67 | -5.70 | -5.74 |
| R600 BTO + Raw BFO | 0.132 | 848.6 | -12.78 | -12.69 | -12.61 |
| Holland H1 | 0.000 | 1.0 | -30.35 | -30.36 | -30.36 |
| Holland H2 | 0.510 | 1.9 | -23.88 | -23.16 | -22.75 |

Primary against alternative (prior, sequence on):

| cell | prior share | contact > 212 m/s | max descent > 15,000 ft/min | second flame-out after the autopilot loss, median | impact time, median (min after 00:00) | median latitude |
|---|---|---|---|---|---|---|
| primary, no intervention | 0.031 | 0.50 | 0.50 | -0.1 min | 40.6 | -36.98 |
| alternative, no intervention | 0.030 | 0.50 | 0.50 | 3.2 min | 33.9 | -36.36 |
| primary, all controls | 0.121 | 0.21 | 0.32 | -0.1 min | 45.6 | -37.69 |
| alternative, all controls | 0.122 | 0.28 | 0.31 | 4.5 min | 39.4 | -37.06 |

## Reading (smoke)
1. **The two-tank takeover alone** changes little (R600 options ≤ 0.07 nat; latitude ≤ 0.02°).
2. **The alternative configuration** moves its descents earlier (median impact 00:33.9 against 00:40.6 for no intervention) and about
   0.6° north; the second engine runs on for a median 3.2 min after the autopilot loss.
3. **The 00:19 data hardly select between the configurations:** R600 BTO Only −0.07 nat from p = 0 to 1, Raw BFO +0.17, Held Out −0.02.
   H2 puts about half its (2-parent) weight on the alternative; not estimable.
4. With items 2-4 the push-over tail is 0.142 % (run C recipe 0.106 %), and every H1/H2 row is a push-over row (items 3 + 4).

## COVERAGE
(a) Feasible set: either autopilot-loss configuration; any lever setting of the running engine; residual roll either way. (b) Reach
(this change): both configurations; the running engine's lever U[0.5, 1.0] (declared, no source: between cruise and maximum
continuous); TAC is not modelled as a separate yaw state on the point mass (its effect is the residual-bank draw; declared); the
alternative is unreachable for parents with a tank already dry at 00:11 (conditional on the core's autopilot-held flight; declared).
(c) Proposal: configuration p0 = 0.5, exact re-weighting; H1/H2 coincidence still the open sampling gap. Bounds/sources: Boeing SIR
App. 1.6E p. 8; tank flow ratio 1.021 (fuel session); INOP flow correction 0.5 (fuel session).

- End of flight

