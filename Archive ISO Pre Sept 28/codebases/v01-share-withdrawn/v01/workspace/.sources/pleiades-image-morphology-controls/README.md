# Pléiades 777 fuselage morphology sensitivity

This source bundle extends the five-family Pléiades morphology screen with three
Boeing 777-200ER fuselage families. It tests whether the earlier exclusion of
fuselage material changed the descriptive mask ranking. It does not estimate
the probability of breakup, identify any image object, or supply evidence to
the canonical estimator.

## Scientific question

For PHR_4 objects 06, 18, 19, 26 and 27, does adding a complete fuselage shell
or longitudinal shell sections produce a lower strict-size two-view mask loss
than the original aircraft and control families?

These five rating-5 objects were retained after the earlier mask-stability
screen; they were not selected for resemblance to aircraft debris. Size
calibration now retains a perturbation only when its source-coordinate mask
overlaps that view's baseline component by IoU at least 0.25. This retains 15/18
trials for object 06 and all 18/18 trials for every other object. The three
rejected object-06 PCA trials had IoU 0–0.0031 and had switched to unrelated
components. The exact ten source panels, masks, calibration record, size
intervals and original five-family results are pinned under [data](data).

## What the structural evidence permits

The NTSB structures report for Asiana Airlines flight 214 describes six unique
longitudinal intervals in the 777 fuselage: sections 41, 43, 44/45, 46, 47 and
48. Sections 44 and 45 occupy the same body-station interval but divide the
upper and lower structure, which this axisymmetric shell model cannot
distinguish. Body stations were converted using

$$
x_{\mathrm{m}}=(BS-92.5)\,0.0254 .
$$

The resulting longitudinal lengths are 14.2875, 9.6520, 10.1346, 10.1092,
8.0772 and 10.6680 m. They are documented structural or assembly boundaries,
not demonstrated preferred fracture planes.

Accident outcomes argue against a single empirical cut prior. In the Asiana
777 seawall impact, the tail separated at the aft pressure bulkhead at BS 2150
and the upper part of section 48 departed with the vertical fin
(Murphy, 2013; National Transportation Safety Board, 2014). In the British
Airways flight 38 777 ground impact, landing-gear structure punctured the shell
near rows 29/30, but the centre keel, cargo floors and stanchions showed no
damage (Air Accidents Investigation Branch, 2010). In the US Airways flight 1549 A320 water impact, the cabin remained intact while damage
progressed through aft lower skin and bulkhead structure and the tail cone lost
its conical form (National Transportation Safety Board, 2010). These cases are
mechanistic examples, not exchangeable observations of an MH370 impact.

The page-level evidence and file hashes are recorded in the
[citation audit](data/citation-ledger.md).

## Declared candidate families

Each new family contains 3,372 masks, matching the raw budget of every original
family.

| Family | Longitudinal definition | What it means |
| --- | --- | --- |
| Whole 777 Fuselage | Complete 63.6577 m CAD-derived shell | Intact-geometry sensitivity |
| Documented 777 Fuselage Sections | Six NTSB intervals, 562 masks each | Reproducible section-boundary sensitivity |
| Random 777 Fuselage Sections | Two uniformly drawn cuts, redrawn until at least 2 m apart | Flexible stress test, not a fracture prior |

A Boeing CAD side outline supplies a radius profile for an axisymmetric body.
Each mask uses an isotropic orientation: the absolute cosine between fuselage
axis and viewing direction is uniform on [0,1]. One mask in five is fully
visible. The others retain a uniformly sampled 15–100% target fraction after a
linear waterline clip. These are coverage sensitivities, not flooding or
breakup probabilities.

All fields use 0.5 m pixels. Ranking applies the same hard gate as the revised
five-family screen: visible area, oriented length and oriented width must each
fall between the lower and upper limits of the object's audited p10–p90
interval. A candidate that is too small or too large on any one measure is
excluded. For a size-eligible candidate c, the loss is

$$
\ell(c,o)=1-\frac{1}{2}
\left[\max_f\operatorname{IoU}(T_o,f(c))+
      \max_f\operatorname{IoU}(P_o,f(c))\right].
$$

Lower loss means greater binary-mask overlap after principal-axis
normalisation and reflection. It is not a class probability, likelihood ratio,
Bayes factor, fracture probability or identity probability.

## Result

| Family | Objects with a size-eligible candidate | Mean lowest loss* | Objects at lowest loss |
| --- | ---: | ---: | ---: |
| Flooding-model wing | 1/5 | 0.3286 | 0 |
| Random-pose wing | 5/5 | 0.3232 | 1 |
| Other shortlisted 777 parts | 4/5 | 0.3704 | 0 |
| Matched random geometry | 5/5 | 0.3267 | 2 |
| Generic ocean-object controls | 4/5 | 0.3532 | 1 |
| Whole 777 Fuselage | 4/5 | 0.3472 | 0 |
| Documented 777 Fuselage Sections | 5/5 | 0.3318 | 1 |
| Random 777 Fuselage Sections | 4/5 | 0.3388 | 0 |

\*Mean over eligible objects only; family means are not directly comparable.

The corrected extended object-level minima are: a fishing-net-or-rope ocean
control for object 06, matched random geometry for objects 18 and 19, a
random-pose wing for object 26, and documented section 47 for object 27. For
object 06 the ocean-control loss is 0.2769, compared with 0.2776 for matched
random geometry and 0.2887 for the random-pose wing. The section-47 loss for
object 27 is 0.3058, versus 0.3145 for matched random geometry. Under the fully
visible restriction its fuselage loss rises to 0.3556, so the random control is
again lower.

The whole shell supplies an eligible mask for four objects but is never the
lowest-loss family. Its four minima require absolute axis/view cosines of
0.885–0.988 and achieved visible fractions of 0.305–0.672: nearly end-on
projection, substantial occlusion, or both. Object 18 has no eligible whole
shell. Only six fully visible whole-shell masks are size eligible across all
five objects, and none improves the extended object-level minimum.

Adding fuselage candidates changes the descriptive minimum for object 27.
Independently, correcting the component correspondence removes the invalid
undersized object-06 nacelle result. The scientific conclusion is unchanged:
Boeing 777 shapes remain admissible, yet the masks do not consistently
distinguish them from generic alternatives. No morphology result should update
the integrated estimate without a calibrated object-detection and identity
model.

## Published-PCA category panel

The paper-facing panel places each published PCA crop beside five grouped
simulated PCA-colour proxies: (1) the lower strict PCA loss across flooding and
random-pose wings, (2) other 777 parts, (3) matched random geometry, (4)
ocean-object controls, and (5) the lower strict PCA loss across whole,
documented and random fuselage families. Every original 3,372-mask family is
independently re-ranked after the unchanged two-sided size gate using

$$
\ell_{\mathrm{PCA}}(c,o)=1-\max_f\operatorname{IoU}(P_o,f(c)).
$$

Every tile retains the 24 m × 24 m field and 5 m ruler. Colours and aligned
orientations are display proxies. This PCA-only panel is a view-specific
diagnostic and does not replace the primary two-view morphology screen.

The published references are sampled from continuous source coordinates, so
each displayed crop spans exactly 24 m rather than an integer-rounded
approximation. Their annotated area, length and width are reconstructed
directly from the published PCA segmentation before display resampling. Each
reconstructed area agrees with the reported GA area within 0.002 m².

For object 06, all five displayed category minima are now inside the corrected
two-sided intervals: area 14.83–31.68 m², length 6.38–9.24 m and width
4.54–6.32 m. Their displayed areas are 23.00–31.00 m² around the 25.00 m²
reference. The earlier 10.25–16.25 m² displays are superseded; their admission
resulted from three failed PCA perturbations contaminating the old lower
limits.

Object 18 has no size-eligible other-777-part or ocean-control mask. Those two
red cells show the recorded closest-size cases only and are not strict category
minima. In the PHR_4 18 row, the wing and ocean-control panels (columns 2 and 5
when the published source is included) are shown after a 180° in-plane display
rotation. This loss-admissible transformation changes neither the score,
dimensions nor eligibility. Gold borders, without an overprinted badge,
identify the lowest eligible displayed category.

The PCA-only category minima are an ocean-object control for object 06 (loss
0.2763), a complete left wing for object 18 (0.2730), matched random geometry
for object 19 (0.2917), documented fuselage section 46 for object 26 (0.3790)
and documented section 47 for object 27 (0.2326). The object-26 section-46
margin over the wing is only 0.0018 and is therefore a descriptive numerical
near-tie, not calibrated evidence of class separation.

The full-component sketches remain separate from the PCA panel and continue to
represent the primary two-view object-level minima: the object-26 right wing
without its flaperon and object-27 documented section 47. Each top–bottom
sketch pair shares a physical scale. Section 47 is BS 1832–2150, 8.0772 m long,
immediately forward of the BS 2150 aft pressure bulkhead. It is a documented
section interval, not a claimed weak point.

The object-18 attitude figure instead depicts the exact PCA-only wing minimum,
`random_pose__03122`: a complete left wing at roll +25.51°, pitch +53.02° and
heave −2.133 m. The complete first-order 3D shell is coloured separately above
and below the level sea surface, and the sea-surface intersection is traced on
the wing. The image-mask model retained geometry to 0.5 m below that surface.
This unconstrained random pose is a geometry sensitivity, not a
hydrostatic-equilibrium prediction.

## Object-18 flooding-attitude sensitivity

A separate post-hoc sensitivity tested whether a quasi-static flooded complete
left wing could reproduce the exact waterline-relative attitude of
`random_pose__03122`. Its target reference heights were +3.649 m at the root,
−11.859 m at the tip, +1.049 m at the leading edge and −4.875 m at the trailing
edge. The preserved first-order model uses a rigid 1 m plan grid, five vertical
buoyancy layers, three assumed mass/thickness draws (6.33, 6.54 and 13.0 t),
and engine-present or engine-absent cases. Its 3 × 3 span/chord cells vary
equivalent retained-air fraction; they are not physical 777 compartments.

The audit recreated 168 states from the four original progressive flooding
schedules, exhaustively enumerated all 512 binary retained/flooded patterns for
all six mass/engine configurations (3,072 states), then performed 24
deterministic coordinate refinements from the four closest binary states in
each configuration. An equilibrium was described as target-like when both the
root-to-tip and leading-to-trailing vertical offsets had the target sign and
were individually within 25% of the selected random pose, with root above and
tip below sea level. This is a descriptive flag, not a measurement tolerance.
Every equilibrium was also rendered in the 12 preserved sensor-surrogate views
and subjected to the corrected two-sided object-18 area, length and width gate.

None of the 168 original-schedule states was target-like. One binary state met
the two slope bounds, but its root was below sea level and it had no
strict-size render. Ten of the 24 locally refined states met both the attitude
definition and strict size gate. Within the tested model they occurred only
with the engine absent, all six midspan and tip cells fully flooded, and
retained buoyancy confined to the coarse inboard row. Root-middle retention
was 17.97–51.56%; root-trailing retention was 0–1.56%; root-leading retention
ranged from 0–100% and was therefore not a necessary condition. Equivalent
modeled retained-air volume ranged from 12.69 to 71.87 m³.

The closest equilibrium used the 6.54 t draw and retained 87.5%, 25.0% and
1.56% in the root leading/middle/trailing cells. Its root-to-tip and
leading-to-trailing drops were 14.001 and 6.264 m, its four-height RMSE was
0.796 m, and its strict PCA loss was 0.3421. The target random pose had loss
0.2730. A different target-like equilibrium gave the lowest refined PCA loss,
0.3183, with 12.69 m³ modeled retained air and height RMSE 1.505 m. Because
retention was fitted after inspecting this target and the search budget differs
from the equal-family screen, neither refined result is added to the
object-level family ranking.

Primary records both support and constrain the mechanism. The 777 has integral
wing-box tanks bounded by spars and tank-end ribs, and engine fuse pins can
permit engine separation while protecting the tank in a prescribed overload
sequence (National Transportation Safety Board, 2014b). However, the tanks are
normally vented to atmosphere through roof channels, outboard surge tanks and
lower-wing scoops (Air Accidents Investigation Branch, 2010; Ministry of
Transport Malaysia, 2018). Boeing lists one main tank at 35.2 m³
(Boeing Commercial Airplanes, 2024); the closest attitude state's 49.3 m³
equivalent volume cannot be interpreted as air retained solely in that tank.
No located source establishes the required isolated inboard pocket, complete
wing survival, or assumed wing mass.

The defensible paper statement is therefore: *within the tested first-order
complete-wing geometry, a target-like attitude was reproduced only under
strongly asymmetric equivalent buoyancy—engine absent, all modeled midspan and
tip regions flooded, and residual buoyancy confined inboard. Documented tank
construction makes residual buoyancy mechanically conceivable, but normal
venting and the lack of a documented sealed inboard bay leave that retention
pattern unsupported.*


## Reproduce

The checked environment used Python 3.14.7 and the pinned packages in
[requirements.txt](code/requirements.txt). The result JSON pins simulation-code
hashes and software versions; Git metadata is absent from this exported
workspace. Two deterministic single-process regenerations took 51.6–73.5 s and
reached 190,604–190,852 KiB (186.1–186.4 MiB) maximum resident memory on the
audit host; figure rendering is separate.
The expanded object-18 flooding run took 296.85 s and reached 97,980 KiB
(95.7 MiB) maximum resident memory; its local refinements used 3,398
hydrostatic objective evaluations.

~~~bash
python3 -m venv /tmp/pleiades-fuselage-venv
/tmp/pleiades-fuselage-venv/bin/pip install -r code/requirements.txt
/tmp/pleiades-fuselage-venv/bin/python code/run_screen.py
/tmp/pleiades-fuselage-venv/bin/python code/run_wing_flooding_sensitivity.py
/tmp/pleiades-fuselage-venv/bin/python code/render_report.py
/tmp/pleiades-fuselage-venv/bin/python code/test_morphology.py
~~~

The bundled inputs are sufficient for the screen. The
[size-interval calibration](data/size-interval-calibration.json) records every
retained and rejected perturbation. *prepare_inputs.py* is only needed to
independently re-extract the inputs from the preserved pre-refactor source
corpus; it accepts that corpus root as its sole argument.
*prepare_panel_display_masks.py* recreates the original two-view-selected
display masks by default. With `--pca-only-results`, it consumes a complete
five-family rerun ranked by PCA IoU under the corrected intervals, aligns the
selected masks for display and writes
[pca-only-selected-display-masks.json](data/pca-only-selected-display-masks.json).
That pinned file records the complete rerun hash, corrected-target hash, source
hashes and wing-state provenance. Display alignment never enters loss scoring.

Artifacts:

- [common-scale mask panel](outputs/fuselage-common-scale-mask-panel.pdf)
  ([SVG](outputs/fuselage-common-scale-mask-panel.svg);
  [PNG](outputs/fuselage-common-scale-mask-panel.png))
- [extended family loss comparison](outputs/extended-family-loss-comparison.pdf)
  ([SVG](outputs/extended-family-loss-comparison.svg);
  [PNG](outputs/extended-family-loss-comparison.png))
- [published PCA and five PCA-only grouped category minima](outputs/published-pca-category-minima-panel.pdf)
  ([SVG](outputs/published-pca-category-minima-panel.svg);
  [PNG](outputs/published-pca-category-minima-panel.png))
- [PHR_4 18 complete-wing attitude and waterline](outputs/phr4-18-pca-wing-attitude-waterline.pdf)
  ([SVG](outputs/phr4-18-pca-wing-attitude-waterline.svg);
  [PNG](outputs/phr4-18-pca-wing-attitude-waterline.png))
- [PHR_4 18 complete-wing flooding sensitivity](outputs/phr4-18-wing-flooding-sensitivity.pdf)
  ([SVG](outputs/phr4-18-wing-flooding-sensitivity.svg);
  [PNG](outputs/phr4-18-wing-flooding-sensitivity.png))
- [separate full-component and matched-pose sketches](outputs/selected-777-full-and-matched-sketches.pdf)
  ([SVG](outputs/selected-777-full-and-matched-sketches.svg);
  [PNG](outputs/selected-777-full-and-matched-sketches.png))
- [complete JSON result](outputs/fuselage-screen-results.json)
- [object-by-family CSV](outputs/fuselage-screen-summary.csv)
- [all generated candidate parameters](outputs/fuselage-candidate-inventory.csv)
- [flooding sensitivity JSON](outputs/phr4-18-wing-flooding-retention-sensitivity.json)
- [all flooding states CSV](outputs/phr4-18-wing-flooding-retention-states.csv)
- [citation audit](data/citation-ledger.md)
- [JON-format BibTeX](paper-references.bib)

## Integration status

Not integrated: the separately oversampled Asiana aft-section family was
removed because it duplicated documented section 48 and its additional
nuisance draws distorted a best-of-search comparison. The Asiana accident is
retained only as structural context.

Not integrated: the fuselage screen is a source-only morphology sensitivity.
A physical breakup model would require impact attitude and velocity,
hydroelastic loading, structural failure and joint properties, flooding,
fragment survival and observation-selection processes that are not available
here.

Not integrated: the refined object-18 flooding states are post-hoc conditional
sensitivities with unequal search effort and target-fitted retained-buoyancy
fractions. They do not replace the equal-budget flooding family, define a
physical tank-flooding probability, or update object identity. Integration
would require documented tank/bay geometry, credible vent and fracture
boundary conditions, validated wing mass distribution, and time-dependent
flooding in waves.
