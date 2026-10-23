python - <<'EOF'
p='research-radar-infrasound-ohasisbio.md'; md=open(p).read()
old="Either the map labels or the H01W table entries may carry an extra 16 s shift. The report does not say which, so this is **unresolved**."
assert md.count(old)==1
new=("Either the map labels or the H01W table entries may carry an extra 16 s shift. The report does not say which, so this is **unresolved**. "
"One further observation points one way. On the H01W-2 spectrogram panels, the event bars and visible energy sit at the **map-label** times: about 00:52:00 (Fig. 4), about 01:34:50 (Figs 6–7) and about 01:29:50–01:30:05 (Fig. 8). They do not sit at the Table 5 picks (00:51:41–43, 01:34:29–33, 01:29:40–42). "
"IMS H01W data are natively in UTC. This pattern is therefore consistent with the GPS−UTC 16 s correction having been applied, in error, to the H01W picks in Table 5. If the inversions used those picks, the H01W arrivals would be about 16 s too early. This remains a hypothesis; it should be put to Royer before any re-inversion.")
md=md.replace(old,new)
open(p,'w').write(md); print('ok')
EOF