# Seabed wreckage PDF under the four 00:19 priority hypotheses (reference-289)

Ocean settling, 9 October 2026, at Pete's request. This redoes `results/settling-wreckage-field-289/` with his four
priority hypotheses: (a) held out; (b) R600 as observed, not adjusted by Holland's offset (as Ashton et al.);
(c) Holland H1; (d) Holland H2. Files: `settling-wreckage-field-289-priorities.{pdf,png,json}`.

**Definitions.** The options are end of flight's (architecture 20:40 UTC, item iv), so the panels can be set beside its
`impact-map-0019-priorities-greyscale`:
(a) `none` × other;
(b) `r600/no-offset` × fuel-exhaustion (end of flight's choice: Ashton holds the log-on request BFO accurate and reads the log-on as possible fuel exhaustion);
(c) H1 = `both/startup-offset` × fuel-exhaustion;
(d) H2 = `both/no-offset` × other.
Panels are side by side and never mixed by evidence (architecture ruling). The H1/H2 mixture is not drawn because its weight depends on W, the log-on
window under `other`, which is Pete's choice.

**Provenance.** End of flight `runs/eof-289-full-s<k>/bto-bfo/seed-<k>/impacts.npy`, k = 1–4, read in place.
- Prior track 289.7° and config paths come from each `run.json`; source run `runs/snap289-m0011`.
- Dive class (b) and the Boeing-calibrated glide are PROVISIONAL-OVERNIGHT.
- Weights are end of flight's `option_posteriors` (imported).
- Settling: `hypothesis/settling` 9823b4e, run.toml baseline. That is the real ocean (GLORYS12V1 column with TEOS-10 density, GLORYS12V1 surface current, ERA5 wind, AusSeabed then GEBCO_2026), with a PROVISIONAL breakup table and the implosion and occupants alternatives off.
- Arcs come from core `runs/reference-289/run.json`.
- No seabed-search evidence is applied.

**Method.** As in the earlier map: systematic resampling per seed (seeds pooled with equal weight); one settling draw per resampled impact, with a
repeated impact getting successive distinct draws; seabed density weighted by settled mass; 0.02° grid, Gaussian 0.1°. Every chart
carries its footnote.
- Panel (a) uses the identical 200,000-impact sample as before. Its elements are taken from that run, and re-running the generator on 500 of its impacts reproduces them bit for bit.
- Panels (b)–(d) are new: 10,000 per seed, Generator(20261011).

| impact PDF | impact ESS | draws on distinct impacts | not computed | 90 % area: all impacts | 90 % area: same impacts → seabed | 99 % area: same impacts → seabed | settled offset p50 / p90 / p99 (km) | mass > 5 km | status |
|---|---|---|---|---|---|---|---|---|---|
| (a) held out, no log-on cause | 12,358,800 | 200,000 on 200,000 | 36 | 711.6k | 700.6k → 701.3k (+0.1 %) | 2,029.2k → 2,031.5k (+0.1 %) | 0.36 / 3.42 / 20.97 | 7.1 % | estimable |
| (b) R600 as observed (no offset), fuel-exhaustion | 59,512 | 40,000 on 37,693 | 0 | 266.8k | 265.7k → 266.5k (+0.3 %) | 687.5k → 691.2k (+0.5 %) | 0.36 / 3.64 / 21.10 | 7.4 % | estimable |
| (c) Holland H1: both bursts, start-up offset, fuel-exhaustion | 36 | 40,000 on 281 | 0 | 41.3k | 41.2k → 42.6k (+3.3 %) | 101.0k → 106.8k (+5.7 %) | 0.36 / 3.10 / 20.53 | 6.5 % | **NOT ESTIMABLE** |
| (d) Holland H2: both bursts, no offset, other | 82 | 40,000 on 427 | 0 | 57.5k | 57.5k → 59.3k (+3.0 %) | 137.3k → 143.6k (+4.6 %) | 0.35 / 2.88 / 20.06 | 6.2 % | **NOT ESTIMABLE** |

Areas in km². Afloat mass excluded: 18.2–18.3 % in every panel.

**What it shows.**
1. **(a) and (b) are estimable.** Settling adds 0.1 % and 0.3 % to the 90 % area (0.1 % and 0.5 % at 99 %). The seabed PDF of the main
   wreckage is the impact PDF, and R600 as observed narrows the 90 % region from 701,000 to 267,000 km². That narrowing is
   end of flight's result, carried through unchanged.
2. **(c) H1 and (d) H2 are NOT ESTIMABLE on this run.** Pooled impact ESS is 36 and 82 (281 and 427 distinct impacts behind 40,000 draws).
   Their panels show where a few dozen impacts lie. They are not posteriors, so their areas (41,000 and 58,000 km² at 90 %) must not be quoted
   as H1 or H2 search areas. Settling's larger relative effect there (+3 %) belongs to the same artefact: a field made of a few
   dozen point clusters is widened proportionally more by a fixed 0.35–3.6 km kernel.
3. Settled-offset statistics do not depend on the hypothesis: p50 0.35–0.36 km, p90 2.9–3.6 km, p99 20–21 km, and 6–7 % of the mass
   beyond 5 km. Settling is a near-identical kernel under every 00:19 interpretation. The 00:19 choice sets the area; settling does not.

**For H1 and H2 to become estimable,** end of flight needs the per-hypothesis proposals Pete asked for (20:55 UTC: H1 conditioned on
exhaustion between the 6th and 7th arcs, H2 on all trajectories). This map is re-run, unchanged, on those impacts when they land.

**Not computed.** 36 impacts in (a), all north of 18° S, fall outside the run.toml ocean window. They are excluded, not treated as impossible (<0.02 %).

**Reproduce.** The commands are in the docstring of `wreckage_map_priorities_run.py`: `wreckage_field_prep_keys.py` for sets A and B, the
`settling::tests::wreckage_field` generator, then the run script. A re-run reproduces the JSON byte for byte. Run cost: 6.5 min on 2
threads for set B, outside the heavy lock (core holds it). Set A was not re-run.
