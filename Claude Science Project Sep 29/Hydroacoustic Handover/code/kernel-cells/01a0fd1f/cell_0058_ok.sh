python - <<'EOF'
p='research-radar-infrasound-ohasisbio.md'; md=open(p).read()
old=" Island terrain (Saddle Peak 732 m on North Andaman; Mount Thullier 642 m on Great Nicobar) could raise or mask individual sites. These heights are not from a source read for this review, so treat them as context, not inputs."
assert old in md
md=md.replace(old," Island terrain could raise or mask individual sites. Terrain heights were not sourced in this review.")
open(p,'w').write(md); print('ok')
EOF