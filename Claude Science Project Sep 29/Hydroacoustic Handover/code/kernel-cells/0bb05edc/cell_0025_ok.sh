cd fix-metz; P='Claude Science Project Sep 29'
p(){ echo "### $1 : $2"; sed -n "$2p" "$P/$1"; }
p coordination/architecture.md 2191; p coordination/architecture.md 2598; p coordination/architecture.md 2599; p coordination/architecture.md 13468; p coordination/architecture.md 13517; p coordination/architecture.md 13520; p coordination/architecture.md 13524; p coordination/architecture.md 13616; p coordination/architecture.md 13733; p coordination/architecture.md 13734
p coordination/HYDROACOUSTICS.md 1700; p coordination/HYDROACOUSTICS.md 1701
p results/hydroacoustics-digitised-sources.md 76; p results/hydroacoustics-digitised-sources.md 77; p results/hydroacoustics-digitised-sources.md 132; p results/hydroacoustics-digitised-sources.md 146; p results/hydroacoustics-digitised-sources.md 154; p results/hydroacoustics-digitised-sources.md 155
p results/hydroacoustics-blackman-validation.md 241; p results/hydroacoustics-blackman-validation.md 243; p results/hydroacoustics-blackman-validation.md 244; p results/hydroacoustics-blackman-validation.md 309; p results/hydroacoustics-blackman-validation.md 310
p results/hydroacoustics-kadri-package-v2.md 62
p results/hydroacoustics-overnight-2026-10-22-summary.md 21; p results/hydroacoustics-overnight-2026-10-22-summary.md 91; p results/hydroacoustics-overnight-2026-10-22-summary.md 108; p results/hydroacoustics-overnight-2026-10-22-summary.md 109; p results/hydroacoustics-overnight-2026-10-22-summary.md 110; p results/hydroacoustics-overnight-2026-10-22-summary.md 123; p results/hydroacoustics-overnight-2026-10-22-summary.md 124
p results/hydroacoustics-weak-signal-methods.md 371
p results/hydroacoustics-literature-review.md 7
p threads/master-prompts/hydroacoustics.md 284; p threads/master-prompts/hydroacoustics.md 305
grep -n "Copy held\|| y\b\|artifact" "$P/paper/CITATIONS-LEDGER.md" | sed -n '1,6p' | cut -c1-250; awk -F'|' 'NR>197 && $7 !~ /^ - $/ && $7 != "" {print NR": "$7}' "$P/paper/CITATIONS-LEDGER.md" | head -5