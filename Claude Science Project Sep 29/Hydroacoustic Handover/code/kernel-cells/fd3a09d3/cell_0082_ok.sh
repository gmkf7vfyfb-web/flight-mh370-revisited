cd "repo/Claude Science Project Sep 29/results"
python - <<'EOF'
import pathlib; p=pathlib.Path('hydroacoustics-tl-grid-run-j.md'); s=p.read_text()
old="row longitude was fitted as linear in arc distance over the valid cells and evaluated at the offset (fit rms 0.003–0.088°,\n   median 0.010°; rows 41.0–40.5°S extrapolated for every offset, 40.0–39.0°S for some; recorded per point in `sources.csv`)."
new="row longitude was fitted as linear in arc distance over the valid cells and evaluated at the offset (fit rms 0.003–0.070°,\n   median 0.010°; 11 of the 129 points are extrapolations beyond the fitted span: 41.0 and 40.5°S at every offset, 40.0 and\n   39.5°S at −30 and 0 NM, 39.0°S at −30 NM, where run J holds few impacts; recorded per point in `sources.csv`)."
assert old in s; s=s.replace(old,new)
old="Scott Reef ≤ 48 against 107.8; H08N ≤ 54 against 90.2. **At the F-35A upper anchor (η ≈ 2e-4) the median impact is 7–30 dB\nbelow the noise median at every receiver, everywhere on the arc.**"
new="Scott Reef ≤ 48 against 107.8; H08N ≤ 54 against 90.2. **At the F-35A upper anchor (η = 2.1e-4) the median impact at its most\nfavourable arc point is still below the noise median at every receiver: by 3 dB at Perth Canyon 3315 and Portland 3275, 8 dB at\n3376, 10 dB at H01W, 12 dB at H08S, 15 dB at 3274, 33 dB at H08N and 56 dB at Scott Reef.**"
assert old in s; s=s.replace(old,new); p.write_text(s); print('ok')
EOF