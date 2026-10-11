# Waypoint family: gap against Pete's specification, and a proposed reset (11 Oct 2026, core)

Status: **proposal only. No run until Pete approves.** Revised 11 Oct evening with Pete's additions 8-11. Source of the specification:
`results/waypoint-stratum-spec.md` (Pete, 29 Sep), Pete's notes on 29–30 Sep (archive messages 390, 752, 788 and 827),
and Pete's rulings of 11 Oct (chat).

## What Pete specified

1. **Sampling support, not a hypothesis list.** Phase 1: fixes west of MEKAR. Phase 2 (before the 18:40 call): a box from
   10 NM NW of LAGOG on N571 to IVRAR. Phase 3: the polygon 8N 94E – 6N 94E – FIR boundary – 6N 92E – RUNUT – YPCC – IVRAR –
   NILAM (as later corrected, with SAMAK inside and a corridor either side of the 094°25′E boundary). "Random trajectories
   through **any** waypoint contained within the polygon can be sampled." Pete noted his own table was a smaller subset than
   the region needs.
2. Trajectories **north of N571**, on a more NNW heading after the last radar return, sampled as well as N571 itself.
3. Flight **toward SAMAK with a turn south well before reaching it**.
4. **Transition** out of waypoint navigation at a **random** point north of the polygon's southern boundary (about 4°S),
   mandatory by it, to any other mode, including LNAV to a destination never reached.
5. (11 Oct) **Family prior:** free flight and waypoint flight at **equal weight**. The question is which the evidence
   favours, if either.
6. (11 Oct) **Speed:** sample up to the aircraft's limit, **Mach 0.87, throughout**.
7. (11 Oct) **Turn model:** sample **both fly-by and fly-over**, not one, unless there is a separate reason to reject one.

## What was built (runs of 9–11 Oct)

| Item | Specification | As built | Consequence |
|---|---|---|---|
| Fix universe | every published fix in the regions | 15 fixes fetched **by name** (Pete's 4 AIP rows plus names core listed); in the 92.5–98.5E / 3–9.5N box the table holds only 9 named fixes. Pete's chart shows many more (AGEGA, EMRAN, IDKUT, RUPTI, LEKIR, SANOB, IGEBO, POVUS, ANSAX, MINAT, MAPSO, DUKUN, …) | the family is a subset chosen before seeing data, but not the region Pete specified |
| Route generation | random paths through any contained fix | a **fixed list of 48** (6 first legs × 8 continuations) composed by core | the hypothesis set is core's enumeration, not a random draw over the region |
| Runs G and H | — | restricted to the **6 routes above 0.1 % in the pilot** | **data-informed selection**: the 6-route family ln Z (−129.55 fly-over, −122.19 fly-by) is biased upward against free flight by the selection. Only the full 48-route family, or the reset family, gives an honest family-level comparison |
| Early break-off | turn south at any point before a fix | only the fly-by anticipation, plus 4 discrete pseudo-fixes in the hybrid arm | partial |
| Transition | random, north of about 4°S, to any mode | at the **end fix** (ISBIX/BULVA/…), to the particle's own free mode | the post-route path is tied to the end fix |
| Phase 2 box | waypoint choices before 18:40 | not sampled as choices; only VAMPI–MEKAR–NILAM | missing |
| Turn model | both | fly-over (to 11 Oct pm), then fly-by + leg tracking | one at a time |
| Mach | to 0.87 throughout | early phase (to 18:40) 0.45–0.87 within the 210–330 KCAS envelope; **cruise 0.73–0.84** (Davey Table 8.2) | cruise cap below the aircraft limit |

**Correction (Mach).** Core's posts of 20:10Z and 20:59Z said route 43's initial-Mach posterior sat against the 0.84 cap.
That is wrong. `initial_mach` is the early-phase draw, whose range was already 0.45–0.87 under the 330 KCAS envelope.
The Mach-cap arm raised only the cruise cap (after 18:40). Route 43 does not approach that cap (00:19 Mach 0.69). Its
−0.12 nat result is real but tested a cap that was not binding. Whether the 330 KCAS envelope (VMO) binds on route 43 at
its sampled altitudes is not yet checked.

## Pete's additions (11 Oct, evening)

8. **Fix epoch.** Use fixes valid in March 2014, not the current cycle.
9. **Break-off on any leg.** The aircraft may fly toward one fix and turn toward **another** fix before reaching it
   (for example to follow the FIR boundary or to pass other traffic). It may also reach a fix by flying over it
   or by turning before it.
10. **State trace for the traffic diagnostic.** Record position, time, heading, speed and altitude every 60 s from
    18:25 to 18:39 for every candidate trajectory. Do not wait for the traffic CSV files.
11. **Mach 0.70-0.87 throughout**, with the 210-330 KCAS envelope throughout. Wide Mach with fuel previously hurt
    convergence (the require-power cut discarded about 69 % of weight and split-half failed). The endurance-aware
    fuel proposal now exists, so smoke-test that combination first.

## Proposed reset (design for approval)

1. **Fix universe: done as a table, not yet used.** See `results/waypoints-2014-epoch-oct11/`. Sources: AIP Malaysia
   ENR 3.3 AMDT 2/2010; the engine's earlier pre-2014 AIP rows; and Robin A. Peel navigation data cycle 2013.10
   (X-Plane / FlightGear default data), which covers the Indian, Indonesian and Australian FIRs five months before
   the flight. Tiers: A, pre-2014 AIP (9); B, in 2013.10 data (17); C, current-cycle en-route only (5, including
   EMRAN); D, current-cycle terminal fixes (13); S, stale (DOVUM). **Proposed sampling set: A + B, 26 fixes**,
   against 9 before. C as a sensitivity arm.
2. **Route generator in the engine** (one draw per particle; no enumerated list):
   - from the 18:22 radar position, a random number of legs (geometric, mean set by Pete). Each leg goes to a fix
     drawn uniformly from the sampling-set fixes in the current phase region that lie ahead (course change up to
     150 deg). Directs north of N571 are as available as airway legs;
   - **break-off on any leg** (addition 9): with a declared probability, at a uniform fraction of the leg, the aircraft
     abandons that fix and turns toward a new fix drawn the same way. The abandoned fix is not revisited;
   - **turn model** per particle, at each sequenced fix: fly-by or fly-over (fly-over with leg recapture), prior 1/2 each;
   - **transition** at a uniform time between the last sequenced fix and the crossing of the southern boundary
     (4.5 S), to one of the five modes, including LNAV to a catalogue destination.
3. **Family prior:** free 1/2, waypoint 1/2. The waypoint family's evidence is the filter's marginal over the
   generator. Route shares, turn points, turn model and transition are reported afterwards from recorded latents.
   No data-informed pruning before the family comparison.
4. **Mach and speed envelope** (addition 11): Mach 0.70-0.87 and 210-330 KCAS, both families, all phases. Needs a
   code change, because the CAS envelope is now applied only to 18:40. **Smoke test first**, at the scale of the
   earlier wide-Mach test: endurance fuel proposal with require-power to 00:11. Pass criteria: weight discarded by
   the require-power cut well below the earlier 69 %; split-half on the 00:19 median within the 8-seed floor; and
   no new bottleneck epoch (the earlier test moved it to 18:25 at 2.35 % ESS).
5. **Sampling efficiency:** the discrete space is large. Use the tempered sampler with route latents carried
   through resampling. Check per-family split-half against the 8-seed floor before quoting.
6. **State trace: done** (addition 10). Engine option `[output.trace]` (from_utc, to_utc, interval_s; at most 32
   points) writes `trace.npy` with latitude, longitude, altitude (ft), ground track, ground speed (kt), Mach and
   true heading, for the same posterior draws as routes.npy. Commit fe4a17b3. Off by default; gates B and C
   byte-identical; unit test added. Every route run from now on carries 18:25-18:39 at 60 s.
7. **Diagnostics to keep:** per-route shares, turn-start geometry, 00:11/00:19 latitude per route group, and the
   N571 traffic diagnostic (IGO053, UAE343) from the trace, once the traffic tracks are available.

What carries over from 11 Oct as engine capability (all off by default, gates byte-identical): `fly_by`, `track_legs`,
route-only `bank_angle_deg` and `fly_by_max_turn_deg`. What does **not** carry over as a result: the 6-route family
evidence of runs G and H, and any family-level Bayes factor drawn from them.
