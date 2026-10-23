cd /Users/pete/Downloads/flight-mh370-revisited
B=origin/claude-science-sep29; H=origin/hypothesis/hydroacoustics; P='Claude Science Project Sep 29'
rng(){ ref="$1"; f="$2"; a="$3"; b="$4"; echo "--- $f:$a-$b"; git show $ref:"$P/$f" | sed -n "${a},${b}p" | cut -c1-520; }
rng $B coordination/architecture.md 2598 2601
rng $B coordination/architecture.md 3012 3016
rng $B coordination/architecture.md 13524 13525
rng $B coordination/architecture.md 13615 13617
rng $B coordination/architecture.md 13732 13735
rng $B results/hydroacoustics-digitised-sources.md 136 138
rng $B results/hydroacoustics-digitised-sources.md 143 143
rng $B paper/JON-MODEL-PAPERS.md 20 20
rng $B paper/JON-MODEL-PAPERS.md 564 582
rng $B results/evidence-sweep-2026-10-17/research-radar-infrasound-ohasisbio.md 9 9
rng $B results/evidence-sweep-2026-10-17/research-radar-infrasound-ohasisbio.md 148 148
rng $B results/evidence-sweep-2026-10-17/research-radar-infrasound-ohasisbio.md 428 428
rng $H engine/hypotheses/hydroacoustics/data/blackman/receiver_observations_diff_vs_drive.csv 15 15
rng $H engine/hypotheses/hydroacoustics/data/blackman/extraction_method.txt 15 17
rng $H engine/hypotheses/hydroacoustics/prepare/digitise_brown_2026.py 8 12
rng $H engine/hypotheses/hydroacoustics/prepare/tl_recal_block9.py 149 152
rng $H engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22/REQUESTS.txt 76 80
rng $B threads/master-prompts/hydroacoustics.md 283 285
git show $B:"$P/results/satellite-coverage-2014-03/coincidence/literature/satellite-literature-register.csv" | tr -d '\r' | grep -n -E "^O1[03]," | cut -c1-400