cd repo
echo "=== module branch hydro files (data/configs)"; git ls-tree -r FETCH_HEAD --name-only | grep -i 'hypotheses/hydroacoustics' | grep -v -E '\.(png|pdf)$' | grep -i -E 'kadri|table|fig|digit|poster|royer|blackman|csv|json|toml|prepare/.*\.py' | head -80
cd "Claude Science Project Sep 29"
echo; echo "=== kadri table1 test headings"; grep -n '^#' results/hydroacoustics-kadri-table1-test.md | head -30
echo; echo "=== filter mentions in kadri/critique/lit notes"; grep -n -i -E 'band-?pass|filter(ed)? (between|at|from)|[0-9]+ ?[-–] ?[0-9]+ Hz' results/hydroacoustics-prior-work-critique.md results/hydroacoustics-literature-review.md results/hydroacoustics-kadri-table1-test.md | cut -c1-260 | head -30
echo; echo "=== poster mentions"; grep -rn -i 'poster' results/hydroacoustics-*.md | cut -c1-240 | head -15
echo; echo "=== blackman validation headings + verdict lines"; grep -n -E '^#|verdict|slope|RMS|median residual' results/hydroacoustics-blackman-validation.md | cut -c1-220 | head -40
echo; echo "=== air9 tl verdicts csv"; cat results/hydroacoustics-air9-tl-verdicts.csv | head -20
echo; echo "=== ram tl check / nx2d headings"; grep -n -E '^#' results/hydroacoustics-ram-tl-check.md results/hydroacoustics-nx2d-corridor.md | cut -c1-200 | head -30