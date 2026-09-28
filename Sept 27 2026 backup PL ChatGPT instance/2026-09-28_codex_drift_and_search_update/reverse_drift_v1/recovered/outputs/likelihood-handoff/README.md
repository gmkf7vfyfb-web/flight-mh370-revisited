# Conditional likelihood-surface handoff

This source-only interchange contract prepares the Pléiades forward-transport result for an explicitly conditional downstream sensitivity run. It does not enter the product runner, identify any image object, or supply an unconditional crash-location posterior.

The machine schema is pleiades-conditional-source-surface/1.0.0. Generated files are under outputs/likelihood-handoff:

- grid.csv is the single 5,289-node curvilinear grid shared by every surface.
- surfaces.csv is the long-format value table joined to the grid by cell_id.
- manifest.json carries scientific semantics, normalized hashes, support and interpolation rules, conditional-use blockers, model-family policy, and provenance.
- likelihood-surface-schema-v1.json defines the CSV row fields and types.
- comparison.html embeds the exact source-generated four-panel vector comparison for ordinary browser viewing.
- comparison.svg is the publication-quality vector comparison and comparison.png is its 4,000 x 1,680 pixel raster counterpart; both are exact packaged copies of the source-generated artifacts.

## Value contract

The three transport components expose a relative conditional endpoint-compatibility likelihood proxy. They expose neither a calibrated posterior density nor a calibrated evidence likelihood. The equal-prior three-family surface is an uncalibrated sensitivity shape, not a fourth evidence item and not a calibrated model posterior.

| Surface | Primary handoff meaning | Posterior density? | Calibrated evidence likelihood? |
| --- | --- | ---: | ---: |
| bran2016 | Relative conditional likelihood proxy | No | No |
| oscar_v2_final | Relative conditional likelihood proxy | No | No |
| glorys12_waverys | Relative conditional likelihood proxy | No | No |
| equal_transport_family_model_average | Uncalibrated equal-prior sensitivity shape | No | No |

At source node $i$, the component score $\ell_i$ is the ensemble expectation of an unnormalised 10 km Gaussian endpoint kernel. It is averaged over the twelve equally weighted Geoscience Australia rating-5 locations, the three equally weighted windage responses, and three fixed stochastic seeds. The composition field is

\[
r_i=\frac{\ell_i}{\max_j \ell_j},
\qquad
\log r_i\leq 0.
\]

The display-only compatibility density and node quadrature mass are

\[
q_i=\frac{\ell_i}{\sum_j \ell_j A_j},
\qquad
m_i=q_i A_i,
\qquad
\sum_i m_i=1,
\]

where $A_i$ is the two-dimensional trapezoidal quadrature area. Edge nodes have half weight and corner nodes quarter weight.

Normalizing $q_i$ is equivalent to applying a constant area-density prior $\pi_0=1/A_S$ on the declared support, where $A_S=439027.71200001123\ {\rm km}^2$ and $\pi_0=2.2777605437352764\times10^{-6}\ {\rm km}^{-2}$. This is a display/normalization prior, not a flight-path prior.

The relative_likelihood and log_relative_likelihood fields already have this constant prior removed up to an irrelevant global factor. If reconstruction from normalized_density_per_km2 is unavoidable, divide $q_i$ by $\pi_0$ before composition. Because $\pi_0$ is constant, the relative shape is unchanged. Do not use normalized_probability_mass as a likelihood: doing so would insert the varying boundary quadrature weights.

For a downstream prior mass $P_i$ on the same cells, form posterior mass proportional to $P_i r_i$. For a prior density $\pi_i$, form mass proportional to $\pi_i r_i A_i$. Add log-relative values to other conditional log-likelihoods only where their conditional independence has been justified.

## Verified source-location assumption

The source premise in Griffin and Oke (2017) was conditional on at least some Pléiades objects being aircraft pieces; the exact located passage and page are recorded in the [citation ledger](data/citation-ledger.md), with the preserved report at [CSIRO Part III](paper/csiro-ocean-drift-part-iii.pdf). Geoscience Australia explicitly could not determine whether the objects were aircraft debris; that passage is also located in the ledger and the preserved [Geoscience Australia report](paper/geoscience-australia-pleiades-imagery.pdf).

The computational hypothesis handed downstream is narrower and fully explicit:

- A source is evaluated at 2014-03-08 00:19 UTC on the declared seventh-arc strip.
- The image observation time is 2014-03-23 04:00 UTC.
- Exactly one latent associated identity is uniformly weighted across all twelve rating-5 locations.
- The twelve location kernels are averaged analytically; no identity is sampled per particle, mask, or source node.
- A uniform one-to-many subset construction is mathematically equivalent only when selected location likelihoods are arithmetically averaged. It is not a joint/product multi-debris likelihood.

Thus the source assumption is verified against both the implementation and the cited premise, but it remains a hypothetical evidence condition rather than an object-identity result.

## Support and interpolation

The native and preferred contract is discrete. Join exact cell_id values and use quadrature_area_km2. The logical grid spans 0–640 NM along the seventh arc at 5 NM spacing and -100 to +100 NM cross-arc at 5 NM spacing, positive eastward.

If transfer to another grid is unavoidable, linearly interpolate relative_likelihood in logical $(along_nm,cross_nm)$ coordinates after mapping the target point to the same arc-coordinate system. Do not interpolate probability mass or extrapolate. Anything beyond the outer logical rectangles is unsupported, not zero. The outer boundary is a chosen truncation boundary, not physical evidence against locations outside it.

Exact zero values can arise from IEEE-754 underflow in very small Gaussian scores. A blank log_relative_likelihood encodes $\log(0)=-\infty$ computationally but must not be read as physical impossibility. Any finite likelihood floor is a separate, explicitly reported sensitivity.

## Family selection and blockers

BRAN2016, OSCAR v2 Final, and GLORYS12 plus WAVERYS are alternative transport responses to the same conditional image-location information. They must never be multiplied as independent evidence. A downstream conditional run may choose one named component. The equal-prior mixture is retained only as a separately reported sensitivity: it is excluded from the core likelihood, must not appear alongside any component, and must not be used to average families in core composition. Its one-third weights are declared sensitivity weights, not empirically estimated family probabilities.

Treating any component as a calibrated conditional likelihood remains blocked because:

- no calibrated MH370-object identity prior, false-positive process, or image-detection/selection likelihood exists;
- the endpoint kernel, identity weights, windage weights, and unresolved diffusion are modelling choices rather than calibrated observation-error distributions for these detections;
- likelihood outside the finite seventh-arc strip was not computed;
- particle/seed variation remains material and numeric zeros include underflow;
- GLORYS12/WAVERYS changes both the Eulerian current product and the explicit Stokes term while retaining non-zero windage alternatives; and
- no absolute family evidence or calibrated family probabilities support the equal-prior mixture.

Accordingly, the component surfaces are suitable only as clearly enabled conditional likelihood proxies/sensitivity factors. The mixture is suitable only as an uncalibrated family-choice sensitivity.

## Deterministic regeneration

From .sources/pleiades-bran2016-forward-inversion:

    node code/build_likelihood_handoff.mjs
    node code/build_likelihood_handoff.mjs --check
    node --test code/likelihood_handoff.test.mjs

The write command regenerates the handoff from the pinned inversion outputs. The check command requires byte-identical output. The test audits schema identity, one-grid joins, area and mass normalization, prior-removal semantics, normalized per-surface hashes, support rules, source hypothesis, and mixture labelling.
