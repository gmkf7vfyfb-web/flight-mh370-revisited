cd /Users/pete/Downloads/flight-mh370-revisited
B=origin/claude-science-sep29; H=origin/hypothesis/hydroacoustics; P='Claude Science Project Sep 29'
rng(){ ref="$1"; f="$2"; a="$3"; b="$4"; echo "--- $f:$a-$b"; git show $ref:"$P/$f" | sed -n "${a},${b}p" | cut -c1-400; }
rng $B results/hydroacoustics-digitised-sources.md 74 78
rng $B results/hydroacoustics-digitised-sources.md 130 133
rng $B results/hydroacoustics-digitised-sources.md 144 157
rng $B results/hydroacoustics-blackman-validation.md 238 245
rng $B results/hydroacoustics-blackman-validation.md 307 311
rng $B results/hydroacoustics-kadri-package-v2.md 60 63
rng $B results/hydroacoustics-kadri-package-v2.md 79 81
rng $B results/hydroacoustics-overnight-2026-10-22-summary.md 19 22
rng $B results/hydroacoustics-overnight-2026-10-22-summary.md 89 92
rng $B results/hydroacoustics-overnight-2026-10-22-summary.md 121 125
rng $B coordination/HYDROACOUSTICS.md 1698 1702