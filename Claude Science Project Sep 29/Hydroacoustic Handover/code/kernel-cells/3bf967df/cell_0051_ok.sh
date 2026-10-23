cd repo; export HOME=$PWD/../h XDG_CONFIG_HOME=$PWD/../h/.config
git pull -q --rebase origin claude-science-sep29
F="Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/SYNTHESIS.md"
python - "$F" <<'EOF'
import sys
p=sys.argv[1]; s=open(p).read()
old="| Settling | Awaiting Pete's approval card | Open |"
new=("| Settling (`settling/`, 07359a7) | Seabed 4,589 m at Haixun (AusSeabed 150 m), 4,466 m at the crossing (GEBCO, gravity-predicted). Detached recorder rests "
     "0.18/0.34/0.50 km (p50/p90/p99) from impact; recorder kept in the aft fuselage 0.38/2.49/10.27 km. A beacon within 2 km of Haixun needs an impact within "
     "2.2 km (detached) or 11.6 km (retained) of it, never on the arc (gap >= 18.9 km). No Kadri eq. 4 impact puts a recorder within 2 km of Haixun "
     "(< 7.5e-5; 2.2e-4 T / 7.5e-5 C with BTO and altitude spread), so Kadri's straight-line source and a Haixun beacon are not jointly compatible. Settling adds "
     "no information to H_H (ratio 0.98-1.10). | Physics provisional; 00:19 weights not applied; HYCOM at Haixun only |")
assert old in s; s=s.replace(old,new)
s=s.replace("4. Settling leg (awaiting approval).","4. Settling: recorder detachment probability per breakup family is not modelled (G-S1); apply 00:19 option weights to its prior masses.")
s=s.replace("Seabed 4,577 m; P(detect","Seabed 4,577 m (GEBCO 2020; AusSeabed gives 4,589 m); P(detect")
open(p,'w').write(s)
EOF
git add --sparse "$F"; git -c user.name="Claude Science" -c user.email="noreply@example.com" commit -qm "Kadri-Haixun synthesis: add settling leg" && git push -q origin claude-science-sep29; git log -1 --format='%h %s'
cp "$F" ../SYNTHESIS.md