# The next large core run (Pete, 10 Oct 2026): the updated model with every fix and extension

One run, four strata as separate runs of the same model, seeds 1-4, radar scored inside the likelihood.
It replaces `reference-289` and the 9 Oct family runs as the base for every module.

Stack for every stratum, in order:

    config/davey2016-inmarsat.toml                 Inmarsat satellite states (filter audit F2)
    config/sensitivity/no-exhaustion-prior.toml    fuel to 00:11, vertical rate in the BFO, tempered sampler
    config/sensitivity/fuel-fixes/s1-factor.toml   (superseded by s3's kappa; kept for the record)
    config/sensitivity/fuel-fixes/s2-temperature.toml
    config/sensitivity/fuel-fixes/s3-internal.toml internal-v1, kappa N(1.0004, 0.0196), 43,800 - kappa x 7,228 kg
    config/sensitivity/fuel-fixes/s4-ceiling.toml  weight-dependent service ceiling
    config/sensitivity/fuel-fixes/s5-hard-reject.toml
    config/sensitivity/reference-snapshots.toml    hand-offs at m2241 and m0011
    config/sensitivity/early-families/radar-full.toml
    <family overlay>                               none | free.toml | waypoints.toml | descent-climb.toml
    config/sensitivity/next-run/<size>-<stratum>.toml

The binary includes core request 17 (sampler ancestry) and request 14 (in-stage cruise BFO).
Not in this run: C-6 (extrapolation s.d.), C-7 (two fuel tanks; design note), C-8 (climb pricing,
bounded in the paper), wide early Mach beyond the free family's own range.
