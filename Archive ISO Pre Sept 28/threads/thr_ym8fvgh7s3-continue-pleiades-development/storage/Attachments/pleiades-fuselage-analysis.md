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

These five objects were retained because their true-colour and PCA masks were
stable across the earlier segmentation perturbations. They were not selected
for resemblance to aircraft debris. The exact ten source panels, derived masks,
size intervals and original five-family results are pinned under [data](data).

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
fall within the object's audited p10–p90 interval. For a size-eligible
candidate c, the loss is

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
| Flooding-model wing | 1/5 | 0.3036 | 0 |
| Random-pose wing | 5/5 | 0.3206 | 1 |
| Other shortlisted 777 parts | 4/5 | 0.3624 | 1 |
| Matched random geometry | 5/5 | 0.3244 | 2 |
| Generic ocean-object controls | 4/5 | 0.3523 | 0 |
| Whole 777 Fuselage | 4/5 | 0.3472 | 0 |
| Documented 777 Fuselage Sections | 5/5 | 0.3308 | 1 |
| Random 777 Fuselage Sections | 4/5 | 0.3353 | 0 |

\*Mean over eligible objects only; family means are not directly comparable.

The extended object-level minima are: nacelle-side for object 06, matched
random geometry for objects 18 and 19, random-pose wing for object 26, and
documented section 47 for object 27. The section-47 loss for object 27 is
0.3058, versus 0.3145 for matched random geometry. Under the fully visible
restriction its fuselage loss rises to 0.3556, so the random control is again
lower.

The whole shell supplies an eligible mask for four objects but is never the
lowest-loss family. Its four minima require absolute axis/view cosines of
0.885–0.988 and achieved visible fractions of 0.305–0.672: nearly end-on
projection, substantial occlusion, or both. Object 18 has no eligible whole
shell. Only six fully visible whole-shell masks are size eligible across all
five objects, and none improves the extended object-level minimum.

Adding fuselage candidates therefore changes one descriptive label but not the
scientific conclusion. Boeing 777 shapes remain admissible, yet the masks do
not consistently distinguish them from generic alternatives. No morphology
result should update the integrated estimate without a calibrated
object-detection and identity model.

## Published-PCA category panel

The paper-facing panel places each published PCA crop beside five grouped
simulated PCA-colour proxies: (1) the lower strict loss across flooding and
random-pose wings, (2) other 777 parts, (3) matched random geometry, (4)
ocean-object controls, and (5) the lower strict loss across whole, documented
and random fuselage families. Every tile retains the 24 m × 24 m field and 5 m
ruler. The colours are display proxies; all losses remain the two-view binary
mask calculation above.

The published references are sampled from continuous source coordinates, so
each displayed crop spans exactly 24 m rather than an integer-rounded
approximation. Their annotated area, length and width are reconstructed
directly from the published PCA segmentation before display resampling. Each
reconstructed area agrees with the reported GA area within 0.002 m².

The apparent first-row size difference is real rather than a display-scale
error. Object 06 has a 25.00 m² reference, while its five displayed category
minima range from 10.25 to 16.25 m². They remain eligible because the audited
object-06 area interval is unusually broad (3.15–31.10 m²); once area, length
and width pass their hard intervals, the morphology loss compares
principal-axis-normalized shape. The candidates were therefore not enlarged
to resemble the reference.

Object 18 has no size-eligible other-777-part or ocean-control mask. Those two
red cells show the recorded closest-size cases only and are not strict
category minima. Gold borders, without an overprinted badge, identify the
lowest eligible displayed category. Full-component sketches have been removed
from the PCA panel and supplied as a separate figure for the three
aircraft-category object-level minima: the object-06 nacelle, the object-26
right wing without its flaperon, and object-27 documented section 47. Each
top–bottom sketch pair shares a physical scale. Section 47 is BS 1832–2150,
8.0772 m long, immediately forward of the BS 2150 aft pressure bulkhead. It is
a documented section interval, not a claimed weak point.

## Reproduce

The checked environment used Python 3.14.7 and the pinned packages in
[requirements.txt](code/requirements.txt). The result JSON pins simulation-code
hashes and software versions; Git metadata is absent from this exported
workspace. Two deterministic single-process regenerations took 51.6–73.5 s and
reached 190,604–190,852 KiB (186.1–186.4 MiB) maximum resident memory on the
audit host; figure rendering is separate.

~~~bash
python3 -m venv /tmp/pleiades-fuselage-venv
/tmp/pleiades-fuselage-venv/bin/pip install -r code/requirements.txt
/tmp/pleiades-fuselage-venv/bin/python code/run_screen.py
/tmp/pleiades-fuselage-venv/bin/python code/render_report.py
/tmp/pleiades-fuselage-venv/bin/python -m unittest code/test_morphology.py
~~~

The bundled inputs are sufficient for the screen. *prepare_inputs.py* is only
needed to independently re-extract them from the preserved pre-refactor source
corpus; it accepts that corpus root as its sole argument.
*prepare_panel_display_masks.py* similarly recreates the four legacy-family
PCA display-mask columns from the preserved five-family analysis directory.
These extracted masks are display inputs only and never enter loss scoring.

Artifacts:

- [common-scale mask panel](outputs/fuselage-common-scale-mask-panel.pdf)
  ([SVG](outputs/fuselage-common-scale-mask-panel.svg);
  [PNG](outputs/fuselage-common-scale-mask-panel.png))
- [extended family loss comparison](outputs/extended-family-loss-comparison.pdf)
  ([SVG](outputs/extended-family-loss-comparison.svg);
  [PNG](outputs/extended-family-loss-comparison.png))
- [published PCA and five grouped category minima](outputs/published-pca-category-minima-panel.pdf)
  ([SVG](outputs/published-pca-category-minima-panel.svg);
  [PNG](outputs/published-pca-category-minima-panel.png))
- [separate full-component and matched-pose sketches](outputs/selected-777-full-and-matched-sketches.pdf)
  ([SVG](outputs/selected-777-full-and-matched-sketches.svg);
  [PNG](outputs/selected-777-full-and-matched-sketches.png))
- [complete JSON result](outputs/fuselage-screen-results.json)
- [object-by-family CSV](outputs/fuselage-screen-summary.csv)
- [all generated candidate parameters](outputs/fuselage-candidate-inventory.csv)
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
