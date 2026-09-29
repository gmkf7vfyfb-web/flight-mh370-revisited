# Waypoint-navigation stratum: sampling boundaries as specified

Pete's specification, 29 September, recorded verbatim in substance before implementation. This is
a **sampling support**, not a hypothesis about what happened: trajectories are generated inside
these bounds and the evidence assigns the weight. Nothing here is a constraint derived from the
satellite data, so it stays independent of BTO and BFO.

## Phase 1 — initial phase

Waypoint candidates **west of MEKAR**.

## Phase 2 — before the 18:40 BFO / C-channel call

A box with:

- **north-west corner**: 10 NM north-west of LAGOG on airway N571
- **south-east corner**: IVRAR

## Phase 3 — after the 18:40 call

A polygon, traversed as given:

1. start at **8°N 94°E**
2. due south along 94°E to **6°N**
3. follow the **FIR boundary** to **6°N 92°E**
4. to **RUNUT**
5. to **YPCC** (Cocos Islands)
6. to **IVRAR**
7. to **NILAM**
8. to **8°N 92°E** (closing)

Within this polygon, trajectories may be sampled through **any waypoint contained in it**.

## Transition out of waypoint navigation

The end of waypoint navigation, and the transition to another mode, is **randomly sampled north
of the polygon's southern boundary**. Every trajectory must have transitioned by the time it
crosses that boundary. The mode it transitions to may be any of the others — constant true or
magnetic heading, constant true or magnetic track, or lateral navigation toward a destination
that is never reached.

Rationale for the southern cutoff: on the high-altitude charts, published waypoints become very
sparse south of roughly 4°S near PIPOV, and those that remain are unlikely on a southbound path,
so continued waypoint navigation past that band is not a meaningful sampling choice. The
transition may also occur earlier at random, but not later.

## Destination catalogue for the post-transition lateral-navigation flavour

Candidates named: Antarctic fields, the geographic and magnetic South Poles, southern Australia,
and — from an earlier discussion to be recovered — a trajectory that appeared to continue toward
**McMurdo**, or the field now coded **NZFX** (Phoenix Airfield; it carried a different NZ code at
the time, same location).

## What must be built alongside it, not after it

Prior work already tested the destination question and did not support it. From
`Archive ISO Pre Sept 28/.../handoff/MH370_waypoint_analysis_README.md`, whose main route was
MEKAR–NILAM–IGOGU–BULVA–ISBIX (**SAMAK is absent and should be included north of IGOGU**):

- Patriot Hills: 48.6% of the main ensemble within 1°, against a catalogue-maximum control
  p = 0.355.
- The earlier IGOGU ensemble's Vostok alignment: 39.3%, adjusted p = 0.474.
- Its own conclusion: "Neither supports an intended destination under this control."
- That ensemble did not converge: ESS 4.801, largest single contribution 40.30%, and two replica
  normalising-constant estimates differing by a factor of about 6.3.
- Its full synthetic-data generation/reconstruction null was **not completed**.

So the catalogue-maximum control is the benchmark this stratum has to beat, and the
generation/reconstruction null is the piece that was missing. A destination prior with enough
freedom will fit almost any arc set; the control and the null are what make a positive result
mean anything.

## Open dependency

Waypoint coordinates. The archive's `waypoint_exact_summary.json` carries a shortlist of names
(IGOGU, ANOKO, NOPEK, BEDAX, BULVA, ISBIX, MUTMI, RUNUT, POSOD, BEBIM) but no coordinate table
was found for MEKAR, LAGOG, IVRAR, NILAM, SAMAK, PIPOV or the FIR boundary vertices. A published
source for the 2014 airway/waypoint set in this region is needed, with the FIR boundary geometry,
before the polygon can be evaluated rather than sketched.
