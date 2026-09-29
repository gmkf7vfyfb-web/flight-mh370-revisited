# MH370 Rerun — checkpoint 11

Created 2026-09-19 12:44 UTC.

## Outcome

This work unit resolves the source/target distinction that had to precede a physical backward or two-ended bridge. The separate final-radar configuration starts at **18:22:12 UTC**. The historical broad-flight fuel prior is anchored at **18:28:05.9 UTC**, 353.9 seconds later. Its code initializes the fuel mass maps at that anchor and deliberately ignores every segment ending before it.

The 32,524.1–34,524.1 kg historical fuel range therefore cannot be relabelled as fuel at last radar. Fuel at 18:22 is a path-dependent preimage of the 18:28 prior.

## Exact boundary measure

For a proposed radar-to-anchor path, the existing powered-flight law gives an affine gross-mass map

`M_anchor = r M_radar + c`.

With constant zero-fuel weight `Z`, this becomes

`F_anchor = r F_radar + c + (r-1)Z`.

If `F_anchor` is uniform on `[L,U]`, the induced radar-fuel support is

`[(Z+L-c)/r-Z, (Z+U-c)/r-Z]`

with density `r/(U-L)`. There are two valid coordinate choices:

- sample anchor fuel from its historical prior and invert the path map; no extra Jacobian is then needed;
- sample radar fuel directly and use the induced support and density above.

Mixing those choices would either omit or duplicate the Jacobian.

## Exhaustion-time proposal

For a time proposal `T` that makes the forward mass map reach empty gross mass `E`, the required anchor fuel is

`F_anchor(T) = map_T^{-1}(E)-Z`.

Under `dM/dt=-(a+bM)`, its derivative is

`|dF_anchor/dT| = (a(T)+b(T)E)/R(T)`,

where `R(T)` is the retained fraction from the anchor to `T`. A uniform time proposal therefore receives

`p_anchor(F_anchor(T)) × |dF_anchor/dT| / q_T(T)`.

The 00:15–00:17 interval is an explicit conditional hypothesis and 00:15–00:19 is its sensitivity comparison. Neither the proposed time nor a uniformly chosen terminal endpoint is an observation. A bridge must replace—not multiply—the existing fuel-window construction, and it must state whether evidence is unconditional or normalized within the chosen hypothesis.

## Validation

The independent Python implementation passes all eight tests:

- exact affine forward/inverse/composition identities;
- normalized anchor-to-radar change of variables and 2,000-draw round trip;
- analytic time Jacobian against centered finite differences;
- exact recovery of prior event mass for both requested time windows;
- a control showing that omitting the time Jacobian is biased;
- source-contract checks confirming the historical pre-anchor fuel gap.

All 24 unchanged checkpoint-10 proposal/lineage tests also still pass. The illustrative constant-flow values in the validation record are exact-solvable controls only and are not MH370 probabilities.

## Provenance limit

The supplied epochs and the official investigation record support a final-radar time around 18:22:12. The exact source derivation of the configuration's 6.578 N, 96.340 E location and its 2 NM / 2 degree scales remains unauthenticated. They must be treated as proposal/configuration assumptions until primary covariance evidence is found. The final-radar branch also uses a different 4 Hz BFO setting and cannot simply replace the historical 7 Hz branch.

## Next gate

The safe next implementation step is to integrate this boundary mapper into the isolated aircraft source, with anchor fuel retained as the canonical latent coordinate. After restoring Rust 1.98.0, the order is:

1. compile and prove base-versus-K=1 equality;
2. run the retained-parent K=4 physical comparison;
3. add radar-to-anchor propagation to a separate bridge target;
4. validate the 00:15–00:17 and 00:15–00:19 time proposals on synthetic aircraft recovery before any MH370 interpretation.

No full-aircraft bridge was run, no posterior probability or location is claimed, and hydroacoustics remains excluded.

Official context: [Malaysian Boeing performance analysis](https://www.mot.gov.my/my/Laporan%20Siasatan%20Mh370/02-Appendices/Appendices%20Set%201%20-%207%20Appendices%201.1A%20to1.9A/Appendix-1.6E-Aircraft-Performance-Analysis-MH370-%289M-MRO%29.pdf); [ATSB search-area definition](https://www.atsb.gov.au/sites/default/files/investigation-reports/ae-2014-054_mh370_-_definition_of_underwater_search_areas_18aug2014.pdf).
