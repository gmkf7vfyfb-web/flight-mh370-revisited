# Pléiades module: citation ledger

Standing rule of 9 Oct 2026 (~01:20 UTC, location corrected ~02:25 UTC). One entry per source. Page numbers are
the printed page numbers of the source unless stated. Files and commits are on `hypothesis/pleiades`
unless stated.

## Data and primary sources

**[GA2017] Minchin, S., Mueller, N., Lewis, A., Byrne, G., Tran, M. (2017).** *Summary of imagery analyses for
non-natural objects in support of the search for Flight MH370: Results from the analysis of imagery from the
PLEIADES 1A satellite undertaken by Geoscience Australia.* Record 2017/13, Geoscience Australia, Canberra.
doi:10.11636/Record.2017.013 (eCat 111041).
- Supports: every Pléiades object position, pixel count, area and rating
  (`data/ga-rec2017-13-objects.csv`, 9a88b2e): Table 1 pp. 13-14, Table 2 p. 15, Table 3 pp. 16-17, Table 4
  pp. 18-19. The rating scale (1 probably natural ... 5 probably man-made) is footnoted under each table and
  the schema is on p. 9. "12 of the 70 objects" rated 5 is on p. 6. Acquisition on 23 March 2014 is on p. 6.
- Supports: **A_scene = 500 km²**, from "Each scene is approximately 25 km x 20 km in size", p. 8
  (`likelihood.rs`, `prepare/twoepoch.py`). The ~0.5 m pixel is also on p. 8. Scenes "significantly cloud and
  glint affected" is on p. 9.
- Supports: correction of the PHR_2 object 12 lat/lon transposition (Table 2, p. 15).
- Obtained: GA's distribution link `https://d28rz98at9flks.cloudfront.net/111041/Rec2017_013.pdf`,
  sha256 `1812498a5735463293cc125a3b7d964d823d2d581100af337d8650e1254220bd`, 51 pages.
- Licence: CC BY 4.0, except images marked (c) CNES, which covers every object crop. **Crops never committed.**

**[CSIRO2017] CSIRO (2017) press release, "Satellite images add to weight of evidence locating missing MH370".**
Quoted only for its count of 28 "possibly man-made" objects, which disagrees with GA's own tables (27). It is
not used as data.

**[GLORYS12] Copernicus Marine Service, Global Ocean Physics Reanalysis GLORYS12V1**
(GLOBAL_MULTIYEAR_PHY_001_030), doi:10.48670/moi-00021.
- Supports: the surface current in every track (`export.rs`; `ocean-model` = `glorys12v1+era5-wind10`).
- Obtained: by the ocean-transport owner; file sha256 `a1b9122138ddf47ee8da84e77576ba9f415e0e322138497ecc5ebff12af87667`
  (from the integrator's provenance). Licence: Copernicus Marine licence. Full record in `results/ocean-references.md`.

**[ERA5] Hersbach, H. et al. (2020).** The ERA5 global reanalysis. *Q. J. R. Meteorol. Soc.* 146, 1999-2049,
doi:10.1002/qj.3803. Accessed via ARCO-ERA5 (Carver et al. 2023), as recorded by the ocean-transport owner.
- Supports: the 10 m wind in every track (`export.rs`). Licence: Copernicus licence. Full record in
  `results/ocean-references.md`.

**[COSMO-pos] The four contact positions F1-F4** (`data/cosmo-contacts.csv`), as ruled in `coordination/PLEIADES.md`
(9 Oct 2026). The source is a slide headed "French Satellite Images sighted (23 March 2014)" that does not name
the satellite, together with Iannello (July 2021, private source), who attributes F1-F3 to COSMO-SkyMed on
21 March 2014. **Not independently verified by this module.** Source, acquisition time and footprint are open
with Pete.

**[Orbits] Pléiades-1A** (descending node 10:30 LMST) **and COSMO-SkyMed** (dawn-dusk, ascending node 06:00 LT):
eoPortal and WMO OSCAR (Pléiades); eoPortal and ESA (COSMO-SkyMed), as ruled by architecture on 9 Oct 2026.
- Supports: `data/acquisition-times.csv`, the `cosmo-pass` alternative.
- **Not independently verified by this module**; URLs to be added when checked.

**[Prior-archive] Prior Pléiades forward inversion (withdrawn share):**
`Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/pleiades-bran2016-forward-inversion/`
on `claude-science-sep29`.
- Supports: `outputs/model-averaged-impact-density.csv` (s11, D1) and `data/pleiades-rating5-objects.csv` (checked
  against [GA2017]). Its prose is reference only.

**[Ref-run] Project reference posterior `no-exhaustion-prior`:** `results/no-exhaustion-prior-summary.json`
and `-datasheet.md` on `claude-science-sep29`.
- Supports: the unconditional posterior in s11 and D1 (0.25 deg map at 00:19:37). It fails split-half, 0.9020
  against 0.924 (datasheet section 3).

**[EoF-glide] Still-air energy-height best-glide bound of 103.4 NM from 35,000 ft:**
`threads/master-prompts/end-of-flight.md` on `claude-science-sep29`.
- Supports: the upper end of the s11 and D1 descent-reach sweep (fb4e9f5, 9a88b2e).

**[Morph-archive] Archived morphology screen, flaperon cut-out** (2.59 m², 1.68 x 2.32 m, "DGA-dimensioned proxy"),
`Archive ISO Pre Sept 28/.../pleiades-image-morphology-controls/`, as read by architecture on 9 Oct 2026.
- Supports: the closed flaperon size check (`results/pleiades/data-manifest.md`). It is a proxy: cite the
  BEA/DGA identification report before quoting it as a dimension.

## Methods

**[HL2019] Handley, W., Lemos, P. (2019).** Quantifying tensions in cosmological parameters: Interpreting the DES
evidence ratio. *Phys. Rev. D* 100, 043504. doi:10.1103/PhysRevD.100.043504; arXiv:1902.04029.
- Supports: the information ratio log I = D_A + D_B − D_AB (eq. 9) and the suspiciousness
  log S = log R − log I (eq. 10), section II.C, p. 4 of the arXiv version (journal page not checked).
  Also the property that I and R transform alike under prior-volume changes (same page).
  Used in `prepare/d1_tension.py` (9a88b2e; citation corrected at 52e3243, where the code had wrongly cited
  PRD 100, 023512, which is a different paper by the same authors).
- Obtained: open-access arXiv copy via Unpaywall. Licence: arXiv non-exclusive distribution.

**[Taylor1921] Taylor, G. I. (1921).** Diffusion by continuous movements. *Proc. London Math. Soc.* s2-20, 196-212.
doi:10.1112/plms/s2-20.1.196.
- Supports: the dispersion of a displacement with exponentially correlated velocity error,
  var = 2σ²T[t − T(1 − e^(−t/T))], used as the model-error term (`likelihood.rs`, `prepare/twoepoch.py`).
- Equation location within the article: **not yet checked**. Obtained: not yet; cite after reading.

**[ArchK] Shared provisional diffusivity prior,** log-uniform 30-1000 m²/s:
`coordination/OCEAN_TRANSPORT.md` (ocean transport, 9 Oct 2026). Owned and cited by the ocean-transport owner.

## Added 9 Oct 2026, overnight

**[Ref-snapshots] Core reference run `runs/reference-snapshots`**: 8 seeds × 7,000,000 particles, per-seed
`final.npy`, byte-identical to `no-exhaustion-prior` (core, 9 Oct). Read in place from core's run tree.
- Supports: `results/pleiades/rerun-295/` (hypothesis/pleiades 415f4b8). The pooled 0.25° map reproduces
  the run's own `summary.json` map to 5e-10.

**[EoF-reach] End of flight's displacement fractions**: 6.6 % of impact weight ≥ 30 NM and 3.4 % ≥ 50 NM
north-west of the 00:19:37 position, by control axis, smoke scale. From `coordination/PLEIADES.md`
(architecture, 9 Oct morning rulings), drawn from `results/eof-smoke-oct09/` and `results/eof-fullscale-oct09/`.
- Supports: the PROVISIONAL-OVERNIGHT `eof-2f` descent kernel. Stable-glide only (Pete, 9 Oct evening).

## Added 9 Oct 2026, morning (measured transport error; second ocean model)

**[OT-GDP] Ocean transport, GDP drifter replay** `results/ocean-transport-error-gdp-replay.md` and `.json`
(commit 24d4b91, merged 008ad4e; corrections 277ae2b). Configurations `glorys12+0.01era5` and
`globcurrent-p1d+0.01era5`, subset `undrogued/box_MAM`, field `ou_fit`.
- Supports: the measured spread in `engine/hypotheses/pleiades/run.toml`: σ = 0.1153 / 0.1176 m/s,
  T = 6.13 / 4.20 d (GLORYS12 + 1 % ERA5) and σ = 0.1043 / 0.0955 m/s, T = 16.02 / 7.64 d (GlobCurrent + 1 % ERA5),
  east / north. Used in `results/pleiades/rerun-measured/`. The underlying drifter data and their citation are
  ocean transport's.

**[OT-REC] Ocean transport, product recommendation** `results/ocean-product-recommendation.md`; ruled by the
architect, `coordination/architecture.md` ~07:00 UTC 9 Oct 2026: GLORYS12 + ERA5 reference; Copernicus-GlobCurrent
(MULTIOBS_GLO_PHY_MYNRT_015_003, v202411) as the second `ocean-model` value at equal prior weight. Product files and
sha256 values in `results/ocean-data-manifest.md` (ocean transport). Retirement date of v202411: 2026-11-24
(same ruling).

**[HL2019], further locations** (same paper, PDF pages of the copy in hand):
- eq. 3, p. 2: Bayesian model dimensionality, d̃/2 = Var_P[log P/π];
- eq. 25, p. 5: tension probability p from χ²_d at d − 2 log S, and "log S is typically 0 ± √(d/2)";
- Proposition 2, p. 6: d = d̃_A + d̃_B − d̃_AB; moderate tension at p ≲ 0.05, strong at p ≲ 0.003; for non-Gaussian
  posteriors p is "only a rough calibration".
- Used in `prepare/rerun_reference.py` (`tension()`; hypothesis/pleiades 9b7cd52).

**[Prior-Pleiades] Prior work: the Pléiades BRAN2016 forward inversion (withdrawn v01 share)**
`Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/pleiades-bran2016-forward-inversion/`
(`README.md`, `likelihood-handoff.md`, `outputs/summary.json`).
- Supports the settings of the comparison in methods draft §6.3. From `outputs/summary.json`: primary diffusion
  5 NM/day rms (sensitivities 0 and 10); primary endpoint kernel σ 10 km (5 and 20 as sensitivities); windage
  factors 0, 1.2 and 3 %; 64 particles per windage. From `likelihood-handoff.md`: the arithmetic mean of twelve
  10 km Gaussian kernels.
- Its 90 % area of 57,708 km² and mode near 35.3 S 92.2 E are read from Pete's figure as attached on 9 Oct, not
  from a file.
- The windage used in §6.3 is 1.25 %, the nearest node of our 0.25 % grid to the prior work's 1.2 %.

**[Taylor1921] equation location: still open (10 Oct 2026).** Both Taylor (1921, doi:10.1112/plms/s2-20.1.196)
and the secondary source LaCasce (2008, *Prog. Oceanogr.* 77, 1-29, doi:10.1016/j.pocean.2008.02.002) are closed
access from this session. The closed form 2σ²T[t − T(1 − e^(−t/T))] for an exponential velocity autocorrelation
is standard. Its equation number needs a library copy; this is a request for Pete.
