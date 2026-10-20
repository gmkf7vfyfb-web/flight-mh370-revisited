# Deliverable 3: the Pléiades position likelihood (PROVISIONAL)

2026-10-09, Pléiades module. Code: `likelihood.rs`, `lib.rs`, `export.rs`. Run config: `run.toml`.

**What it returns.** For every impact sample s and choice of (`pleiades-origin`, `object-rating`,
`cluster-weight`, `ocean-model`): 0 under not-H, and ln Σ_c w_c p(y_c|s)·A_scene under H. With the
composer's mixture over the prior on H this reproduces the brief's ln[(1−π) + π Σ_c w_c p/q_c], with
q_c = 1/500 km². `absolute_scale` = true. **No identity likelihood**: shape and size enter nowhere. The
cluster weights are the declared `cluster-weight` forms (equal, count), and ρ4 sweeps rating 4 at
{0, 0.25, 0.5, 1}. Observation ID `ga-rec2017-13:pleiades-objects`.

**The spread is analytic and normalised (brief §9).**
- p(y|s) is a mixture of normalised Gaussians around deterministic `mh370-ocean` tracks. The tracks
  come from a 0.1° release table at 00:20 UTC on 8 March, interpolated bilinearly.
- The mixture runs over the windage prior (21 nodes, 0-5 %) and the K prior (8 Gauss-Legendre nodes,
  log-uniform 30-1000 m²/s). The variance is 2KΔt + OU model error (σ_e 0.05 m/s, T_e 2 d) + 0.5 km².
- No random number is used anywhere. Outside the table, or where a track left the field, the result
  is NaN ("not computed").

**Tests** (`cargo test -p mh370-hypotheses pleiades`; RAYON 2, test-threads 2):
- p(y|s) integrates to one over the plane to 2e-3 for a representative s.
- The column is bit-identical across two independent constructions. There is no seed, which is the
  seed-independence requirement met by construction.
- Interpolation is exact for a uniform flow, and NaN outside the table.
- The variance matches its closed form, with the OU part's diffusive limit checked.
- Gauss-Legendre quadrature is exact on x⁴, and the targets file sums to one in every arm.
- Ignored test against the real table: the column is finite across the grid and bit-identical twice.

The two transport tests brief §8 asks to port (constant-current analytic displacement, random-walk
RMS) **already exist in the shared crate** (`crates/ocean/tests/transport.rs`:
`constant_current_matches_analytic_displacement`, `random_walk_reproduces_declared_daily_rms`). Not
ported again.

**Not yet in it:**
- COSMO-SkyMed (deliverable 4: the joint kernel, which must not multiply independent likelihoods over
  13 shared drift days).
- A second ocean-model option.
- The Poisson term for unseen debris and the footprints (brief §13).

The 15-day spread at the reference parameters is about 33 km (K = 30) to 60 km (K = 1000) per
component, before the windage mixture widens it further. So p·A_scene peaks at about 0.02-0.08, and a
single Pléiades cluster can only ever be weak evidence about s. The composer's P(H|D) will show that
directly.
