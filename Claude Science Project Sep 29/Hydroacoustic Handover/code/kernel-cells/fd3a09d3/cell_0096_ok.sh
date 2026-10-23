cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import pathlib
p=pathlib.Path('tl_grid_table.py'); s=p.read_text()
old="more strongly into the deep channel (5-13 dB lower TL at the IMS triads, about 100 dB\n                                       lower at Portland than the neighbouring rows)."
new="more strongly into the deep channel (5-13 dB lower TL at H01W and 8-31 dB at H08S, growing\n                                       with frequency; about 100 dB lower at Portland than the neighbouring rows)."
assert old in s; p.write_text(s.replace(old,new))
p=pathlib.Path('../../../../../../repo/Claude Science Project Sep 29/results/hydroacoustics-tl-grid-run-j.md'); s=p.read_text()
old="water at the source): the adiabatic model couples the 10 m source far more strongly into the deep channel, giving 5–13 dB\nlower TL at H01W/H08S and ~100 dB lower raw TL at Portland than the neighbouring rows;"
new="water at the source): the adiabatic model couples the 10 m source far more strongly into the deep channel, giving 5–13 dB\nlower TL at H01W, 8–31 dB at H08S (growing with frequency) and ~100 dB lower raw TL at Portland than the neighbouring rows;"
assert old in s; p.write_text(s.replace(old,new)); print('ok')
EOF