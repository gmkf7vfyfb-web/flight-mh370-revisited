# Where the wreckage rests on the seabed, under four impact PDFs (reference-289)

Ocean settling, 9 October 2026, at Pete's request: a greyscale 50/90/99 % map in the project convention of the
seabed wreckage PDF, under three or four versions of the impact PDF, with each impact PDF drawn faintly for
reference. `settling-wreckage-field-289.{pdf,png,json}`.

**Provenance.** End of flight's `reference-289` evidential sweep, read in place: `runs/eof-289-full-s<k>/bto-bfo/seed-<k>/impacts.npy`,
k = 1–4. Prior track **289.7°** and config paths from each `run.json` (`config/davey2016.toml` … `hypotheses/end-of-flight/full/seed-<k>.toml`;
source run `runs/snap289-m0011`; code revision 55c4536-dirty for seed 1, ea07583 for seed 2). Dive class (b) and the Boeing-calibrated glide are
PROVISIONAL-OVERNIGHT; the breakup table is PROVISIONAL. Arcs from core's `runs/reference-289/run.json` (`reference_arcs`).
Settling at `hypothesis/settling` 9823b4e (generator `settling::tests::wreckage_field`, ignored), run.toml baseline:
GLORYS12V1 column (density from its own T and S, TEOS-10), GLORYS12V1 surface current, ERA5 wind, AusSeabed then GEBCO_2026.

**The four impact PDFs.** Chosen to span the seabed-search options table from widest to tightest: (a) the 00:19 bursts held
out, no log-on cause (the depth note's headline); (b) R600 and (c) R1200 under Holland's start-up offset, fuel-exhaustion
log-on (the most informative single-burst treatment there); (d) both bursts, inflated, fuel-exhaustion (the tightest).
Weights are end of flight's `option_posteriors`, imported, not reimplemented.

**Method.** Per option, impacts are systematically resampled per seed (seeds pooled with equal weight): 50,000 per seed for (a),
whose 99 % tail is wide, and 10,000 per seed for (b)–(d). Each resampled impact is carried through the settling transform once
(a repeated impact gets successive, distinct draws), with its own time, position, velocity, energy and end of flight's `debris_class`.
The seabed density gives each draw's **settled** elements the impact's probability in proportion to element mass (multiplicity × piece
mass): a mass-weighted wreckage PDF, dominated by the dense, sonar-detectable pieces. Afloat elements have no seabed position
(18.5 % of mass over all draws) and are not in it. Grid 0.02°, Gaussian 0.1° (6 NM) as in the impact maps, HPD levels on the
smoothed density, areas on the authalic sphere. The impact contours (dashed orange) use every impact at full weight.
"Same impacts" in the table below is the resampled impact set itself, smoothed identically, so that its difference from
the seabed column is settling alone.

| impact PDF | impact ESS | impacts settled | not computed | 90 % area: all impacts | 90 % area: same impacts | 90 % area: seabed | change | 99 % area: same impacts → seabed | settled offset p50 / p90 / p99 (km) | mass > 5 km from impact |
|---|---|---|---|---|---|---|---|---|---|---|
| 00:19 bursts held out, no log-on cause | 12,358,800 | 200,000 | 36 | 711.6k | 700.6k | 701.3k | +0.1 % | 2,029k → 2,032k | 0.36 / 3.42 / 20.97 | 7.1 % |
| R600, Holland start-up offset, fuel-exhaustion | 67,598 | 40,000 | 0 | 246.1k | 246.2k | 247.5k | +0.5 % | 677k → 681k | 0.35 / 3.34 / 21.76 | 7.0 % |
| R1200, Holland start-up offset, fuel-exhaustion | 10,065 | 40,000 | 4 | 166.0k | 166.2k | 167.3k | +0.7 % | 494k → 500k | 0.34 / 1.95 / 19.51 | 5.1 % |
| both bursts, inflated, fuel-exhaustion | 2,042 | 40,000 | 0 | 169.9k | 170.1k | 172.1k | +1.2 % | 442k → 449k | 0.35 / 3.28 / 21.86 | 7.0 % |

Areas in km².

**What it shows.**

1. Settling hardly changes the area of the PDF at this scale: the 90 % region grows by 0.1–1.2 % and the 99 % region by
   0.1–1.7 %. Half the settled mass rests within 0.34–0.36 km of its impact and 90 % within 2–3.4 km, against a 6 NM
   smoothing kernel and impact PDFs hundreds of km long. The tighter the impact PDF, the larger the relative growth (d is
   largest), as expected when a fixed kernel is added to a narrower field.
2. The tail is the floated mass: about 5–7 % of settled mass rests more than 5 km from its impact, and the 99th percentile is
   20–22 km. That is cabin contents and other pieces that float for hours before sinking. It widens the seabed field's edges,
   not its core.
3. So, for search planning, the seabed PDF of the main wreckage is the impact PDF to within about 1 % in area. Settling
   matters at the scale of a single search cell (the debris field and the ±25 % ocean-model sensitivity on the D6 pages), not at
   the scale of the impact PDF. The search area is set by which impact PDF is used, not by settling.

**Not computed.** 37 resampled impacts (36 in a, 4 in c that are one impact drawn four times, out of 200,000 and 40,000) lie north
of 18° S, outside the run.toml ocean window [80, 112] °E × [−45, −18] °. They are recorded as not computed and left out of the
seabed density. They are not treated as impossible. Their share is under 0.02 % of each panel. The window can be widened if
a later option puts real mass there.

**Monte Carlo.** The resampled 90 % impact area is within 1.5 % of the full-weight area in every panel. At 99 % the resampled
area is 5 % below full weight in (a) even with 200,000 impacts (2,029k against 2,131k km²): the far tail is under-filled.
The settling comparison is like-for-like either way. Impact ESS for (d) is 2,042. Its 99 % contours are noisy, and that
noise is shared by the impact and seabed fields alike.

**Run.** 313,472 settling draws, 258,346 distinct impacts: 13.5 min on 2 threads outside the heavy lock, which core held,
on a machine at load about 40. That is over the ~10 min guideline because my estimate (4 min, from a 154k-draw pass) did not
allow for the load. Disclosed in coordination.

**Reproduce.** `python3 wreckage_field_prep.py <end-of-flight smoke dir> <end-of-flight engine/runs>` writes
`field/impacts_in.f64` (bit-identical, sha256 8a01904e…); then `SETTLING_FIELD_IN=field/impacts_in.f64
SETTLING_FIELD_OUT=field/elements.f64 cargo test --release -p mh370-hypotheses settling::tests::wreckage_field -- --ignored`;
then the same prep command with core's `reference-289/run.json` as a third argument draws the map (`wreckage_map.py` alongside).
The element file (1.3 GB) is not kept in the repo.
