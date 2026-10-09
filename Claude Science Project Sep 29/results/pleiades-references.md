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
