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

<!-- memory-records:start (generated by registry/import_memory_records.py; do not edit by hand) -->

## External facts moved from memory (25 October 2026)

These rows are records of what project memory said about external sources. They are not verified facts unless the
status column says VERIFIED or CORRECTED, and even then the check was the memory track's check of the held source.
Status values: VERIFIED (claim found in the source), CORRECTED (claim corrected against the source; use the corrected
text), PARTIAL (part of the claim found), UNVERIFIABLE (no held copy, or the claim was not found). The last column gives
the finding of the independent verifier of 25 October 2026 where there is one. Text that names a restricted source is
withheld here; the memory export row holds it.

| mem_id | written (UTC) | memory text | status | source | method and evidence | corrected text | verifier |
|---|---|---|---|---|---|---|---|
| `mem_fbaab1d46ac2` | 2026-10-08 00:45 | GA Record 2017/13 (Pleiades object tables) is not on the project Google Drive. It is a public Geoscience Australia record under CC BY 4.0: obtain it from GA directly (request network access if needed) and cite it by its own page numbers. It is the only source of the rating-4 object count. | VERIFIED | GA Record 2017/13 Summary of imagery analyses (Drive, text via read_file_content; text incomplete) | full source document read by session model; VERIFIED: GA Record 2017/13 is a public Geoscience Australia record under CC BY 4.0 [printed p. 2] ; VERIFIED: Record contains the Pleiades object tables [printed pp. 13-19] ; NOT_IN_THIS_DOC: It is the only source of the rating-4 object count [n/a] ; NOT_IN_THIS_DOC: Not on the project Google Drive; obtain from GA [n/a] |  |  |
| `mem_7c87cea3dc39` | 2026-10-08 01:19 | GA Record 2017/13 tables (PDF sha256 1812498a..., from the GA CDN at d28rz98at9flks.cloudfront.net/111041/Rec2017_013.pdf): 70 objects; rating 5 = 12, identical to the archive; rating 4 = 27 (1,214 m2), although CSIRO's 2017 press release says 28. PHR_2 has 6 rating-4 objects and no rating-5. Committed as hypotheses/pleiades/data/ga-rec2017-13-objects.csv with MANIFEST.md; the PDF itself is not committed. COSMO-SkyMed positions are in 'ISO Sept 28 Status/decisions/cosmo-skymed-sightings.md'; their source, UTC time, footprint and the F1-F4 labelling are still open. | VERIFIED | GA Record 2017/13 Summary of imagery analyses (Drive, text via read_file_content; text incomplete) | full source document read by session model; VERIFIED: 70 objects [printed pp. 6, 12, 24] ; VERIFIED: rating 5 = 12 [printed pp. 6, 12, 24; tables pp. 13-19] ; VERIFIED: rating 4 = 27 objects totalling 1,214 m2 [printed pp. 13-19 (Tables 1-4)] ; VERIFIED: PHR_2 has 6 rating-4 objects and no rating-5 [printed p. 15 (Table 2); p. 12] |  |  |
| `mem_94251c27c100` | 2026-10-08 14:23 | Geoscience Australia Record 2017/13 is reliably downloaded from its eCat distribution link, https://d28rz98at9flks.cloudfront.net/111041/Rec2017_013.pdf. The link was found with a POST to https://ecat.ga.gov.au/geonetwork/srv/api/search/records/_search. The ATSB mirror of the same report stalls (HTTP/2 reset, then zero bytes). The DOI 10.11636/Record.2017.013 redirects to a GA metadata page that returns 403. GA describes each of the four Pleiades scenes as about 25 km x 20 km, about 100 km apart, all significantly cloud- and glint-affected. | VERIFIED | GA Record 2017/13 Summary of imagery analyses (Drive, text via read_file_content; text incomplete) | full source document read by session model; VERIFIED: Record 2017/13, eCat 111041, DOI 10.11636/Record.2017.013 [printed p. 2 (cover: no printed folio)] ; VERIFIED: Four Pleiades scenes each about 25 km x 20 km, about 100 km apart [printed p. 8 (section 2.1)] ; VERIFIED: All significantly cloud- and glint-affected [printed p. 9 (section 3.1)] ; NOT_IN_THIS_DOC: CloudFront download link, eCat POST search, ATSB mirror stalls, DOI redirect ret [n/a] |  |  |
| `mem_367e91bf34de` | 2026-10-08 14:41 | COSMO-SkyMed contact positions: F1 -34.57416667 91.86888889; F2 -34.95194444 91.68333333; F3 -34.74694444 92.17250000; F4 -35.38527778 89.95388889 (F4 is the isolated south-western point). IDs follow the Malaysian briefing-slide coordinate order, NOT Iannello's article, whose first two are reversed. The slide is dated 23 Mar 2014 and does not name the satellite; Iannello attributes F1-F3 to COSMO-SkyMed on 21 Mar 2014 (private source). F1-F3 is the corroborated reference set and F1-F4 the extension sensitivity; the 21-vs-23 March date is a declared alternative. Footprint and target sizes are unknown and carried as missing: never substitute the F1-F4 bounding box, nominal COSMO swath dimensions, or the 1-23 m optical-object sizes. Also listed in 'ISO Sept 28 Status/decisions/cosmo-skymed-sightings.md'. | UNVERIFIABLE |  | : ; held candidate files existed but the claims were not found in needle snippets or best-ranked full pages; searched: 729 Downloads PDFs + 658 artifact PDFs/texts (text needle search), Drive title search (97 queries), 15 named-report Drive searches |  |  |
| `mem_8df3c8f7becd` | 2026-10-09 06:12 | Pléiades tension is calibrated with Handley & Lemos 2019 (PRD 100, 043504): Bayesian model dimensionality eq. 3 (p.2), tension p eq. 25 (p.5), Proposition 2 d = d̃_A+d̃_B−d̃_AB with moderate tension at p≲0.05 (p.6). It is implemented in prepare/rerun_reference.py tension(). The paper warns that p is only a rough calibration for non-Gaussian posteriors. The companion BMD paper is PRD 100, 023512. | PARTIAL |  | needle snippets from held files; NOT_FOUND: 1 [ART:10.1103_PhysRevD.100.043504.pdf#d7d17b28 (no snippet)] ; VERIFIED: 2 [ART:10.1103_PhysRevD.100.043504.pdf#d7d17b28, printed p. 6 (PDF p. 6)] ; VERIFIED: 3 [ART:10.1103_PhysRevD.100.043504.pdf#d7d17b28, printed p. 16 (PDF p. 16), ref. [50]] |  |  |
| `mem_6198b9493b0a` | 2026-10-10 04:52 | The Pleiades citation-ledger gap for the Taylor (1921) equation location (formula 2σ²T[t − T(1 − e^(−t/T))]) stays open. Both Taylor 1921 (doi:10.1112/plms/s2-20.1.196) and LaCasce 2008 (doi:10.1016/j.pocean.2008.02.002) are closed access from the session, so a library copy from Pete is needed. The shared mh370-ocean integrator is RK2 midpoint with a 1 h step, and the Pleiades release tables cover 85–103 E, 43–25 S at 0.1°. | PARTIAL | api.crossref.org/works/10.1112/plms/s2-20.1.196 (Proc. LMS s2-20(1) 196-212, issued 1922); /10.1016/j.pocean.2008.02.002 (Prog. Oceanogr. 77(1) 1-29, 2008) | Crossref metadata; DOIs and works verified; Taylor is dated 1922 in Crossref (row: 1921). Equation location not checked (papers not held). |  |  |
| `mem_a2c4b8ead1fb` | 2026-10-17 21:59 | 2014 satellite sightings, primary values found 17 Oct 2026 (report research-satellite-imagery-2014.md, artifact 539ce9c6). DIGO sheets (Internet Archive amsa.gov.au/media/incidents/images/DIGO_00718_0{1,2}_14.jpg) give DigitalGlobe 16 Mar 2014 at 0416Z: obj1 43°58'34"S 090°57'37"E ~24 m, obj2 44°03'02"S 091°13'27"E ~5 m. GISTDA THEOS sheets give 24 Mar 03:07:56.153985 UTC, 2 m PAN, incidence 26.982°, zones near 46.5°S 89.4-89.6°E (provisional thumbnail reading). The MRSA/Airbus 23 Mar '122 objects' image is near 44.68°S 90.53°E (11-object table in the MOT PDF 'Maps showing objects reported by MRSA'), NOT the GA Pléiades scenes at 35°S. Japan IGS 26 Mar: 10 km radius about 44°17'S 90°56'E, 00-06 UTC. | PARTIAL |  | needle snippets from held files; NOT_FOUND: 1 [none (no needle found in held candidate files; DIGO_00718_01_14.jpg not among held files)] ; NOT_FOUND: 2 [none (no needle found in held candidate files; DIGO_00718_02_14.jpg not among held files)] ; NOT_FOUND: 3 [known-use-satellites-16-27mar2014.pdf#23ec0fd0 p.1 and satellite-access-counts-7-15mar2014] ; VERIFIED: 4 [mrsa_map_26mar2014.pdf#ce53441c (MOT Malaysia map 'Maps showing objects reported by MRSA')] |  |  |
| `mem_c7b88bb4ef0b` | 2026-10-17 21:59 | No imaged-footprint or non-detection map for the 2014 satellite imagery was found in the ATSB 2017 report, AMSA, JACC, Malaysian MOT or the GA Record. Satellite imagery cannot yet serve as a non-detection term; only the aerial search of the satellite-cued areas (ATSB Table 12) is public. Historical 2014 TLEs for catalogued satellites are available WITHOUT a Space-Track login via the Hugging Face bulk export (see the TLE-sources memory row); a Space-Track login is not needed. Nominal sun-synchronous timing reproduces the THEOS time (implied nadir offset 339 km vs 367 km from the incidence angle; SGP4 with real elements gives 371 km). | CORRECTED | ATSB 2017 The Operational Search for MH370 (Drive operational-search-for-mh370_final_3oct2017.pdf, text via read_file_content) | full source document read by session model; CONTRADICTED: No imaged-footprint map for 2014 satellite imagery in ATSB 2017 [printed p. 119 (PDF p. 128)] ; VERIFIED: Aerial search of satellite-cued areas in ATSB Table 12 [printed p. 24 (PDF p. 33)] ; NOT_IN_THIS_DOC: TLE/SGP4/THEOS timing [n/a] | Apart from ATSB 2017 Figure 90 (printed p. 119, PDF p. 128), which maps only the locations of the four 23 Mar 2014 Pléiades scenes, no imaged-footprint or non-detection map for the 2014 satellite imagery was found in ATSB 2017, AMSA, JACC, Malaysian MOT or the GA Record. Satellite imagery therefore cannot yet serve as a non-detection term. Only the aerial search of the satellite-cued areas is public (ATSB 2017 Table 12, printed p. 24). Historical 2014 TLEs for catalogued satellites are available without a Space-Track login via the Hugging Face bulk export (see the TLE-sources row). Nominal sun-synchronous timing reproduces the THEOS time: implied nadir offset 339 km, against 367 km from the incidence angle; SGP4 with real elements gives 371 km. |  |
| `mem_734597aeb50c` | 2026-10-17 23:17 | The 2014 satellite sightings at 43-46.5 S (DigitalGlobe 16 Mar, Gaofen-1 18 Mar, Airbus/MRSA 23 Mar, THEOS 24 Mar, Japan IGS 26 Mar) lie about 1,000 km south of the Pléiades scenes and well off the 7th arc. They were imaged where the early (pre-28 Mar) search was, not where impacts are likely. They are best used as an empirical false-alarm calibration set for the sightings model (several sensors reporting hundreds of 'objects' where MH370 debris almost certainly was not), as Geoscience Australia recommended. A back-drift check from the sighting positions is proposed but not yet requested of the Pléiades module. | UNVERIFIABLE | ATSB 2017 The Operational Search for MH370 (Drive operational-search-for-mh370_final_3oct2017.pdf, text via read_file_content) | full source document read by session model; held candidate files existed but the claims were not found in needle snippets or best-ranked full pages; searched: 729 Downloads PDFs + 658 artifact PDFs/texts (text needle search), Drive title search (97 queries), 15 named-report Drive searches |  |  |
| `mem_1dff85719963` | 2026-10-18 14:55 | Coordinates used for the satellite sightings and contacts on searched-areas maps: DigitalGlobe 16 Mar object 1 at 43°58′34″ S 090°57′37″ E and object 2 at 44°03′02″ S 091°13′27″ E; Gaofen-1 18 Mar at 44°57′ S 90°13′ E; Airbus/MRSA 23 Mar centroid near 44.68 S, 90.53 E; THEOS 24 Mar near 46.5 S, 89.5 E (provisional); Japan IGS 26 Mar, 10 km circle around 44°17′ S 90°56′ E. Pléiades scenes come from engine/hypotheses/pleiades/data/ga-rec2017-13-objects.csv and COSMO contacts F1–F4 from cosmo-contacts.csv. | VERIFIED | GA Record 2017/13 Summary of imagery analyses (Drive, text via read_file_content; text incomplete) | full source document read by session model; VERIFIED: Pléiades scene positions are taken from GA Record 2017/13 object tables [printed pp. 13-19] ; NOT_IN_THIS_DOC: Airbus/MRSA 23 Mar centroid near 44.68 S, 90.53 E [n/a] ; NOT_IN_THIS_DOC: DigitalGlobe, Gaofen-1, THEOS, Japan IGS coordinates; COSMO F1-F4 from cosmo-con [n/a] |  |  |
| `mem_b8d9373368b2` | 2026-10-20 19:38 | March 2014 TLEs: the Hugging Face dataset juliensimon/space-track-tle-history (public Space-Track bulk export, one Parquet per year, 2014 file 168 MB) holds parsed GP fields (float32 angles, no raw lines) for all catalogued objects; downloads redirect to us.aws.cdn.hf.co, which needed a network approval. It does NOT hold classified objects (KH-11, Lacrosse, SAR-Lupe, Helios, Ofeq, IGS). Amateur sets for those come from Mike McCants' classfd.zip (Wayback captures 2014-03-19 and 2014-10-08 of prismnet.com/~mmccants/tles/) and the SeeSat-L archive (satobs.org/seesat/<Mon-YYYY>/, approved host); in March 2014 only USA 186, USA 245, Lacrosse 5, SAR-Lupe 3 and 5 had fresh sets, the rest were 2-9 months stale, Ofeq 5/7 absent. | PARTIAL | https://huggingface.co/api/datasets/... tree listings (fetched 25 Oct 2026, HTTP 200) | web fetch |  |  |
| `mem_5c4111228e04` | 2026-10-20 20:11 | Proba-1's local time had drifted to about 05:20/17:50 by March 2014 (dawn-dusk), so it had no daylight pass over the area; Formosat-2 (daily repeat orbit) could only reach fixed strips with gaps between them; Resurs-DK1 (70 deg orbit) crossed the box in daylight only twice in 8 days. Classified satellites without March 2014 elements and therefore absent from the maps: IGS Optical 3/4/5 and Radar 3/4, Helios-2A/2B, Ofeq-5/7/9, SAR-Lupe 1/2/4, USA 224, Topaz 1/2. | UNVERIFIABLE |  | : ; held candidate files existed but the claims were not found in needle snippets or best-ranked full pages; searched: 729 Downloads PDFs + 658 artifact PDFs/texts (text needle search), Drive title search (97 queries), 15 named-report Drive searches |  |  |
| `mem_9760eb9c2f6c` | 2026-10-20 21:50 | Satellite literature sweep (20 Oct 2026; review artifact 9146ca84, register 1c65603d, 91 rows): no published orbital-coincidence analysis of imaging satellites vs the MH370 flight or impact area was found (provisional; Hansard/PPRuNe/IG statements not crawled). ATSB 2017 PDF p.125/printed p.116 says imagery over the Malay Peninsula, Malacca Strait and Indian Ocean for the flight time was examined and the aircraft was not identified; no sensor or footprint list. Malaysian SIR 2018 (all 495 pp searched) is silent on satellite imagery except the MTSAT IR weather image (PDF p.142). | PARTIAL | Malaysia Safety Investigation Report MH370, 2 Jul 2018 (Drive PDF); ATSB 2017 The Operational Search for MH370 (Drive operational-search-for-mh370_final_3oct2017.pdf, text via read_file_content) | full source document read by session model; NOT_FOUND: SIR 2018 is silent on satellite imagery except the MTSAT IR weather image (PDF p [PDF p. 142 not supplied] ; NOT_IN_THIS_DOC: ATSB 2017 p.116 imagery statement; literature sweep results [n/a] ; VERIFIED: ATSB 2017 PDF p.125/printed p.116: imagery over Malay Peninsula, Malacca Strait, [printed p. 116 (PDF p. 125)] ; NOT_IN_THIS_DOC: Malaysian SIR 2018, literature sweep [n/a] |  |  |
| `mem_12e0cd2edd9a` | 2026-10-21 00:29 | GEO imager study (21 Oct 2026, notes artifact d52012ae): Chiba Univ CEReS anonymous FTP holds full-resolution MTSAT-2 (native HRIT + 0.04 deg gridded, every scan) and FY-2D (re-encoded HRIT) for 7-8 Mar 2014. FTP is not routable from the Mac sandbox (proxy 502); it works from ssh:deskstar. FY-2D archive has no scans 16:31-19:31 UTC on 7 Mar; the EUMETSAT MVIRI 57E CDR catalogue (EO:EUM:DAT:0881) lacks Meteosat-7 slots 19:00-21:00 UTC (both consistent with equinox eclipse; inference). | UNVERIFIABLE |  | : ; held candidate files existed but the claims were not found in needle snippets or best-ranked full pages; searched: 729 Downloads PDFs + 658 artifact PDFs/texts (text needle search), Drive title search (97 queries), 15 named-report Drive searches |  |  |
| `mem_c56bb03492af` | 2026-10-21 00:29 | MTSAT-2 full disc 17:32 on 7 Mar 2014: HRIT line times 17:31:15.5 (line 1, north) to 17:57:49.5 (line 2750), 0.580 s/line. The Moon was below the horizon at the aircraft for the whole flight after 16:42 UTC (43% illuminated), so a moonlit contrail was impossible; the Sun was below -6 deg until about 23:28 UTC. | UNVERIFIABLE |  | : ; held candidate files existed but the claims were not found in needle snippets or best-ranked full pages; searched: 729 Downloads PDFs + 658 artifact PDFs/texts (text needle search), Drive title search (97 queries), 15 named-report Drive searches |  |  |

<!-- memory-records:end -->
