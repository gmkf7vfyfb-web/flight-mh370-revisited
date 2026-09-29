# Known-flight station-coordinate sensitivity

This directory is a bounded sensitivity audit, not a WSPR detection result.
`known-flight-locator-uncertainty-audit.json` assigns one coherent point per
`(callsign, six-character locator)` in each of 131,072 fixed-seed scrambled
Sobol designs.  It repositions the 59 already-frozen actual-slot candidate
pairs and applies the production 20-degree angle, 25 km clustering and
three-independent-link rules.  It does not regenerate pairs that crossed the
map or 100-NM selection boundary.

Raw qualifying clusters within 25 km of withheld truth occurred in 31 designs
at MH370 16:42 and 22 designs at MH370 16:54; none occurred at the other four
known-flight slots.  These counts describe a deterministic sensitivity design,
not a probability distribution for antenna positions.

`locator-witness-pharlap-all.json` reruns the two local contributing
intersections for all 53 witnesses through the unchanged 295-ray PHaRLAP
screen (318 route jobs).  Before control subtraction, one 16:42 design passes
the declared joint recovery rule: 10.63 km horizontal separation, with a
1.0 km feasible ray height versus withheld aircraft height 0.743 km.  All eight
endpoint-to-intersection errors are at most 25 km.  No witness passes the
surface-endpoint cluster screen.

For sample 23,526, `locator-witness-control-geometry.json` coherently repositions
all 357 retained actual/control pairs for the MH370 16:42 epoch.  The nearest
strict raw control proposal is 198.99 km from the witness centre.  Because a
PHaRLAP screen can only remove supporting links, it cannot create a control
cluster inside the 25 km subtraction radius; the event is therefore residual
within the frozen retained-pair universe.  This still does not rematerialize
pairs excluded by the original cell-centre map/100-NM filter.  A complete test
requires the authors' versioned historical antenna-coordinate database and
full candidate regeneration for all three panels.

Frozen identities:

- Geometry audit SHA-256: `267c40c45d92f0bd05db9ca7ba743e81fc7d7e080d8de932005d2adb93febe40`
- PHaRLAP witness audit SHA-256: `09ca75a9125afe1ef5a0e37a3811b01d588bcb6f05211f86fddaa071b3ae7e34`
- Retained-pair control audit SHA-256: `087ead29670a05851c8c5c3a77c67574b05e3bb6c5e3f707865baec7c7b9714a`
- IRI library SHA-256: `01f18a58b36aa7729a91f0e48e97b68345b69efb004b09525c063f589168f295`
- Ray library SHA-256: `9bcd233651c51878e8907f5401d4d6ab15faec2f8a747b5fa14243eb26b869f3`
