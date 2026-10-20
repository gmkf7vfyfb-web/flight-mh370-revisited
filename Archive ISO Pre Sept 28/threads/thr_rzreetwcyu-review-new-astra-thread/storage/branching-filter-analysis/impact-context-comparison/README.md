# Impact, search and acoustic-context maps

env MH370_REPORT_PYTHON=/tmp/mh370-acoustic-venv/bin/python /jackbox/home/MH370/target/iteration/mh370 report-flight-drift --context-only --analysis /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis --output /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/impact-context-comparison --inline-output /jackbox/home/MH370/mh370-impact-context.html

For each mapped target and selected flight/contact model, show the highest-flight-weight retained route within 150 km and the closest retained geographic neighbour. Same endpoint choices are deduplicated in drawings. These are illustrative selections among 213 retained exact histories, not samples from an acoustic-conditioned posterior. Report actual distances and contact weights; geographical proximity alone does not establish a satellite or acoustic match.

Broad cruise source: 1,020,000 initial candidates, caps 16 turn/8 Mach/8 altitude starts after 18:25; stated mode/frequency and fuel priors remain.
The paired maps differ only by the supplied CMEMS nine-recovery, isotope and Australian coastal non-recovery compatibility factors. Gain and acoustic evidence are not multiplied into them.
Seventh arc is the archived official FL400 reference; impact altitude is sea level. No impact is forced onto that reference curve.
Historical 2014–17 survey data extents, Bluefin display footprints and approximate 2018 outline are shown as context. Proposed renewed-search bands and AIS tracks are not labelled as searched seabed.
No calibrated searched-area non-detection likelihood is applied. Current campaign swath completion is not known from these outlines.
Kadri target coordinates are conditional geometric constructions. A/B are catalogue entries without recovered corresponding peaks in the published trace. C is unlocalised on the southern arc. D is the preferred reported candidate. E/F are exploratory timing pairs with periodic interference.
These model-conditioned impact PDFs remain numerically and physically provisional.

Normalized Gaussian smoothing of original weighted impacts on a padded equal-area grid; thresholds rank display density to enclose at least each requested probability. Cell discretization and contour interpolation give approximate geographic boundaries. No impact or observation weight is changed. Grid spacing 5 km; Gaussian standard deviation 25 km. Both original weights and display grids are saved in each NPZ file.

Impact time = arrival time minus great-circle distance / effective celerity at the exact plotted point. For E/F, intersect the two station intervals, allowing each path its own celerity within the declared range. No station time correction is fitted. Scenario bounds at fixed coordinates, not a confidence interval, acoustic association or precision claim. Location, bearing and propagation-model errors are not integrated. Nominal 1.50 km/s estimates are diagnostics only.

The small frozen timing input is prepared by the external prepare_impact_context_timings.py script and checked against the original plotted coordinates, station configuration and acoustic-speed bounds. The reporting command does not rerun inference or terminal traces.
