python - <<'EOF'
p='research-radar-infrasound-ohasisbio.md'; md=open(p).read()
old="and tentatively locates 5 events between 00:16 and 01:06."
assert md.count(old)==1
md=md.replace(old,"and tentatively finds 5 acoustic events between 00:16 and 01:06 (Royer's count). Table 2 lists them as 6 location solutions (A, B, C1, C2, D1, D2), because C1/C2 and D1/D2 are mutually exclusive alternative associations of the same records.")
old2="### Q4 data table B: Royer (2016) candidate events, 8 March 2014 (Table 2; standard errors)"
assert md.count(old2)==1
md=md.replace(old2,"### Q4 data table B: Royer (2016) candidate solutions, 8 March 2014 (Table 2; standard errors; 5 events, 6 solutions, because C1/C2 and D1/D2 are alternatives)")
open(p,'w').write(md); print('ok')
EOF