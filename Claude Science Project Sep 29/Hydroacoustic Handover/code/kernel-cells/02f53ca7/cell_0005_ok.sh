cd "repo/Claude Science Project Sep 29/results"
wc -l hydroacoustics-blackman-validation.md hydroacoustics-air9-ew0112-source-reference.md hydroacoustics-ram-tl-check.md hydroacoustics-nx2d-corridor.md hydroacoustics-audit/*.md
cat hydroacoustics-air9-tl-verdicts.csv; cat hydroacoustics-air8-control-verdict.json
echo ---; cd "../../../hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; ls prepare; echo; ls results-data; ls results-data/* | head -60; ls data