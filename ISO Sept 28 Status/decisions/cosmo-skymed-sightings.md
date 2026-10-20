---
name: cosmo-skymed-sightings
description: "Pete's 2026-09-28 request to add four COSMO-SkyMed radar targets (21 Mar 2014) as a conditional sighting set beside Pleiades, with a combined PDF; open inputs and the correlation rule"
metadata:
  node_type: memory
  type: project
  originSessionId: b321a56a-4f19-4c04-acbd-d5031b94cf81
  modified: 2026-09-28T23:07:06.422Z
---

On 2026-09-28 Pete asked to add four possible COSMO-SkyMed radar sightings from 21 March 2014 to the drift analysis. They are conditional, like Pleiades, with a mixed-source PDF over both.

Positions:
- 34°34′27″S 91°52′08″E
- 34°57′07″S 91°41′00″E
- 34°44′49″S 92°10′21″E
- 35°23′07″S 89°57′14″E

Each lies 49–81 km from the nearest Pleiades rating-5 cluster (Pleiades imaged about 04:00 UTC on 23 March).

Plan:
- The Pleiades thread (thr_ec96wswyz6) generalises its module to two sighting sets, renamed satellite-sightings, one implementation. Each set gets its own origin alternative and prior-odds sweep.
- Ocean drift builds 21 March maps.
- The composer reports all four combinations.

**Asked of Pete and still open:** the source of the positions, the acquisition time in UTC, and the imaged footprint and target sizes.

**Why:** the two sets may be the same debris. 13 of the 15 drift days are shared, so multiplying independent likelihoods would double-count the drift evidence.
**How to apply:** insist on a shared transport error or a 2-day conditional kernel for the joint case, plus the impact-independent 2-day object-to-object test. Radar background (ships, rain, clutter) gets its own not-H model over the COSMO footprint. Related: [[pete-deferred-until-stable-impact]], [[thread-coordination]].
