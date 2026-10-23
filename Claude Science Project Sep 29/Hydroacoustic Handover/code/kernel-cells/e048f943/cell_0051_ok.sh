cd repo/"Claude Science Project Sep 29"/results
python - <<'EOF'
import pathlib
p=pathlib.Path('hydroacoustics-run-j-levels.md'); s=p.read_text()
s=s.replace("(99 % two-sided band about 40.4–26.1 °S; the 99th-percentile northern contour is 26.1 °S under D0′ and 25.7–26.6 °S over the other keys, so 20 °S is the span)",
            "(1st–99th percentile of the weighted mass 39.0–26.1 °S under D0′; the 99th-percentile northern contour is 25.7–26.6 °S over the 12 keys, so 20 °S is the span)")
s=s.replace("E q05/q50/q95 = 0.33 / 1.16 / 9.8 GJ under D0′ p0.5 (D4: median 10 GJ, P(E ≥ 10 GJ) = 0.50 as the brief states)",
            "E q05/q50/q95 = 0.35 / 1.16 / 11.4 GJ under D0′ p0.5 (D4 p0.5: median 10.0 GJ, P(E ≥ 10 GJ) = 0.50 as the brief states; D3 p0.5 median 6.3 GJ)")
p.write_text(s)
EOF
grep -c "" hydroacoustics-run-j-levels.md
cp ../../../charts_out/hydroacoustics-run-j-levels-*.png ../../../charts_out/hydroacoustics-run-j-levels-*.pdf . ; ls hydroacoustics-run-j-levels-* | wc -l