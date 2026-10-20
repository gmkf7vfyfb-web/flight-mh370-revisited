# Which arc does 17.50 Hz per 1,000 ft/min belong to?

Core request 8 of `results/core-requests-oct07.md`. `crates/satcom` is core-owned, so the core
estimator session settles it. **Settled: the end-of-flight session is right, and this project's
earlier record was wrong in attribution.**

## The answer

| Arc | BTO | Elevation | Hz per 1,000 ft/min |
|---|---|---|---|
| **00:11** (`m0011`) | 18,040 µs | 39.64–39.67° | **17.800–17.813** |
| **00:19a** (`m0019a`) | 18,400 µs | 38.88–38.92° | **17.515–17.528** |

So 17.50 belongs to the **00:19a** arc. The earlier project record attached it to the 00:11
geometry and quoted an elevation of 38.8°. That elevation is the 00:19a figure. The 00:11 arc sits
about 0.76° higher, at 39.7°, and is correspondingly more sensitive.

## Why the figure is nearly constant along each arc, and why the arcs differ

The BFO's response to a vertical rate is the component of that rate along the line of sight:

    dBFO/dv_vertical = (f_uplink / c) · sin(elevation)

A BTO value fixes the **slant range**, and for a satellite at fixed altitude the range fixes the
elevation angle. So every position satisfying one arc sees the satellite at the same elevation,
and the sensitivity is a property of the *arc*, not of where on it the aircraft is. Across 30°S to
40°S the figure moves by 0.013 Hz — a twentieth of the difference between the two arcs.

The two arcs differ because their BTOs differ by 360 µs. A larger BTO is a longer range, a lower
elevation and a smaller vertical-rate sensitivity. That is the whole of it.

## How it was checked

Computed independently from `data/satellite-ephemeris.csv` using the engine's own constants —
`UPLINK_HZ = 1,646,652,500`, `SPEED_OF_LIGHT_KM_S = 299,792.458`, `PERTH_GES_KM` and
`BTO_FIXED_OFFSET_US` — with the arc longitude found by bisecting `bto_us()` at each latitude, and
elevation taken against the **geodetic** local vertical.

The geodetic vertical matters. Using the geocentric one instead — normalising the position
vector — shifts the elevation by about 0.17° and the answer by 0.05 Hz, which is a fifth of the
difference under dispute. My first attempt made exactly that error and produced 17.86 and 17.57,
which would have muddied rather than settled the question.

With the vertical taken correctly the result reproduces the end-of-flight session's numbers to
four digits in both arcs, from a separate implementation. That agreement is the evidence.

## What follows

A ±20 Hz BFO excursion corresponds to **1,123 ft/min at the 00:11 arc** and **1,141 ft/min at the
00:19a arc**. The substance of the end-of-flight brief's §7 argument is unaffected — the two
figures are within 2% of each other — but the attribution must be right before either reaches the
paper, and the paper should quote the arc alongside the number rather than the number alone.

One caveat to carry: this is the sensitivity of the **geometry**, the partial derivative of
predicted BFO with respect to vertical rate. It is not a statement about how well a vertical rate
can be *estimated* from a BFO, which also depends on the bias state and on the measurement noise.
