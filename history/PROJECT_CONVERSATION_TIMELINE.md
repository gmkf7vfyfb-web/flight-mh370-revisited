# Reconstructed MH370 project conversation timeline

This chronology is a handoff summary, not a verbatim transcript. The exported
conversation should later be added alongside it.

1. **Received-power challenge.** The project identified the possibility that
   terminal transmit power was precompensated for HGA gain and proposed a
   formal test using MH371 heading changes and known-position MH370 phases.
2. **Integrated estimator definition.** BTO, BFO, received power, aircraft
   performance/trajectory and drift were combined in a Bayesian estimator from
   the post-radar state around 18:11 through the 00:11 arc.
3. **Control and terminal intent.** The modelling scope was widened to allow
   human control, early descent, ditching intent, glide and impact more than
   100 NM from the seventh arc. High-altitude/high-speed flight was not imposed.
4. **Stage-one run.** The integrated through-00:11 estimator produced a broad,
   multimodal southern Indian Ocean posterior centred near 37°S, 89–90°E.
5. **BFO refinement.** Fast random BFO sigma was estimated from available data
   without mixing intermittent bias into the random variance. Separate 00:11
   airborne maps were produced with and without backward-smoothed drift.
6. **Pleiades/BRAN hypothesis.** The northeastern Pleiades candidates were
   treated conditionally. BRAN-anchored diagnostics were run without the CSIRO
   search-area constraint and with terminal seed areas expanded for feasible
   controlled glide.
7. **Multimodal-spike interpretation.** Work examined why the unconditional
   posterior contains southern and northern spikes and why the conditional
   imagery likelihood selects the lower-prior northern component.
8. **No-precompensation sensitivity.** The estimator was rerun under the
   hypothesis of no power precompensation, with and without Pleiades evidence.
9. **Search non-detection.** ATSB and Ocean Infinity searched areas, unpublished
   swath uncertainty, AIS proxies, bathymetric limits and remaining planned
   search areas were gathered and cross-checked.
10. **Paper development.** A *Journal of Navigation* template and first-pass
    introduction/meta-analysis sections were produced. The planned emphasis is
    the integrated model, with Pleiades as a separate conditional scenario.
11. **End-of-flight evidence.** A separate Holland (2017)/radar/Pleiades note
    was developed. The Lido radar loss/regain, disputed altitude labels and
    Pulau Perak eyewitness account motivated a descent/re-climb sensitivity.
12. **Pulau Perak sensitivity.** Fuel and trajectory analysis found little
    posterior effect under the tested anchoring, consistent with approximate
    energy equivalence.
13. **Received-power graphics.** Graphic options were developed to explain the
    side-mounted conformal HGAs, geometry, MH371 natural experiment, measured
    gain pattern and attitude-dependent coverage.
14. **Migration.** The project adopted a hybrid migration: immutable snapshot,
    private GitHub/Git LFS working repository, conversation export, explicit
    handoff dossier and reproducible environment.

