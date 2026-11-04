# Amendment 3 to the reverse-sensing methods specification: primary-secondary pair test (P2)

Date: 4 Nov 2026. Source: Pete Large's proposal, 4 Nov 2026. Fixed BEFORE the association phase runs. It adds one association test (P2). It changes no screening detector.

## Physical basis (first principles; checked numbers to be added by the association track)
- A sealed or trapped air volume that survives the impact sinks until outside water pressure collapses it. Thin aluminium structure built for about 0.6 bar inside-to-outside differential is expected to collapse at tens to a few hundred metres. Sink speed 1-5 m/s (settling module range).
- Main lag window: primary + 5 s to + 10 min. Extension window: + 10 min to + 75 min (collapse at depth or contact with the seabed, 3,500-4,500 m on the arc).
- Primary and secondary share the source position (sinking drift is small) and so the same path. The travel-time uncertainty cancels. The lag between them is a source property. At two or more stations the lag must agree to within the pick uncertainty (about 1-2 s, to be set from the data form: raw IMOS or envelope).
- Implosion signal: a sharp broadband pulse (rise in milliseconds) and a few bubble oscillations, which give spectral ripple or lines at the bubble frequency. Scale: an air pocket of 2 m radius at 300 m collapses in about 0.03 s.
- Energy available is about water pressure times volume (about 1 MJ for 1 m^3 at 100 m; about 30 MJ for 10 m^3 at 300 m; about 300 MJ for 100 m^3 at 300 m). A large part goes into sound. A source hundreds of metres deep has no near-surface cancellation and is nearer the channel axis, so it couples into the channel better than a surface source.
- Condition: a high-energy dive breaks the structure into small pieces, so few or small secondaries are expected under the dive hypothesis tested first. Large secondaries are more likely after a low-energy ditching.

## Test P2
1. For each candidate primary (any detector, any station), search the main lag window, then the extension window, at the same station for secondary transients from the screening detectors and S10 at the spec's candidate threshold.
2. Single-station statistic: number of secondaries (and their implosion-like class score from the classifier: impulsive, broadband, bubble ripple allowed) against the off-window background rate of transients at that station (scan statistic, Poisson with the measured rate; time-slide check).
3. Multi-station statistic: for primaries associated across stations, the lag pattern (secondary minus primary) must agree across stations within the pick uncertainty. Null: time slides of the secondary lists, independently per station.
4. Use: P2 adds weight to a candidate's rank. A missing secondary never lowers a candidate's rank, because under the dive hypothesis the secondary is expected to be weak.
5. Calibration reference: the project's 27 glass-sphere implosion outcomes (time shape and spectral form only).
