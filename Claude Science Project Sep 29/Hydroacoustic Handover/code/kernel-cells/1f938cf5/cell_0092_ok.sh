export HOME=$PWD/home XDG_CONFIG_HOME=$PWD/home/.config; cd repo
git pull -q --rebase 2>&1 | grep -v -E "failed to store|Updating files"
cat >> "Claude Science Project Sep 29/coordination/architecture.md" <<'EOF'

## 2026-10-18 ~04:00Z — Ocean Settling -> architecture, composer (cc Pete): Kadri/Haixun settling leg (Q8) posted

`results/kadri-haixun-conditional-2026-10-18/settling/README.md`. Labels: run J, 00:19 option none (weight column only), settling PROVISIONAL.
- Depth: Haixun first contact 4,589 m (AusSeabed 150 m; GEBCO_2026 4,583, TID 11); second contact 2/3 km W 4,578/4,573 m; bearing x arc 4,466 m (GEBCO TID 40, no AusSeabed).
- Displacement (GLORYS12V1, run J rows in L): detached recorder p90 0.34 km, p99 0.50; engines/gear p99 0.43-0.44; recorder retained in aft fuselage p99 10.3 km (intact 13.9). HYCOM 53.X at Haixun: detached p90 0.46, retained p99 12.9.
- Inverse: impact within 2.2 km (detached, p99) / 11.6 km (retained, p99) of the contact; inside the wide strip; never beyond the 7th arc (gap >= 18.9 km). 0 of 40,000 Kadri draws per branch put a recorder within 2 km of Haixun; with BTO/altitude spread 2.2e-4 (T), 7.5e-5 (C).
- Settling ratio for H_H: 0.98-1.10 (route strata) -> treat as 1. Near-Haixun prior mass ESS 5-60: provisional.
Gaps G-S1..G-S4 in the note. No core change requested.
-- Ocean Settling
EOF
git add "Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/settling" "Claude Science Project Sep 29/coordination/architecture.md"
git diff --cached --name-only | grep -E "\.bin$|fuel-tables\.json|\.xlsm$" && echo BAD || echo audit-ok
git -c user.name="Claude Science" -c user.email="noreply@example.com" commit -q -m "Kadri-Haixun conditional: settling leg (Q8) - seabed depths, recorder/heavy-part displacement (GLORYS12V1, HYCOM sensitivity), inverse region for Haixun beacon" 
git push -q origin claude-science-sep29 2>&1 | grep -v "failed to store"; git log --oneline -1