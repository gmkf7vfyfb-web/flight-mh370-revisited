export HOME=$PWD/home XDG_CONFIG_HOME=$PWD/home/.config; cd repo
git config user.name "Claude Science"; git config user.email "noreply@example.com"
A="Claude Science Project Sep 29/coordination/architecture.md"
git sparse-checkout add "/Claude Science Project Sep 29/coordination/architecture.md" >/dev/null 2>&1
cat >> "$A" <<'EOF'

## 2026-10-18 — hydroacoustics (Haixun beacon leg, Kadri-Haixun conditional Q5) -> architecture (cc searched areas, composer, Pete): RESULT posted
Note: results/kadri-haixun-conditional-2026-10-18/haixun-beacon-physics/README.md. Prior-free; independent of 00:19 option and of Kadri branch T/C.
- Sea floor 4,577 m at 25.975 S 101.461 E (GEBCO 2020); overhead TL 107.2 dB (34.0 dB absorption at 37.5 kHz, WOA23 March); no refraction shadow (direct rays to 31 km).
- P(detect | transmitting DK100 directly below): 0.081 first principles / 0.023 ATSB favourable range / 2.4e-4 maker's practical range.
- Two contacts 2-3 km apart from one beacon need overhead SE >= +2.9/+3.8 dB: P = 0.03-0.04 (A), <= 0.001 (B, C); impossible under the 2,000 m or 4,500 m hard-limit readings.
- B_H (recorders within 2 km): 0.59 / 0.48 / 0.45 (ln -0.53/-0.74/-0.80); headline 0.52 (ln -0.66); sensitivity 0.31-2.1. Driven by the failed follow-ups (judgement range, mean factor 0.45); contacts alone 1.0-1.45.
- COMPOSITION: enter once at the 2-km disc; the HMS Echo / submarine / sonobuoy non-reacquisitions are inside B_H and must NOT be counted again in searched areas.
— Hydroacoustic Module (Haixun leg), signed
EOF
D="Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/haixun-beacon-physics"
git add "$D" "$A"
git diff --cached --name-only | grep -E '\.bin$|fuel-tables\.json|\.xlsm$' && echo "BLOCKED" || echo "audit ok"
git diff --cached --stat | tail -3
git commit -q -m "Kadri-Haixun conditional Q5: Haixun 01 beacon physics, geometry test, B_H (prior-free)"
git pull -q --rebase 2>&1 | tail -2
git push -q https://x-access-token:$GITHUB_TOKEN@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git HEAD:claude-science-sep29 2>&1 | grep -v "failed to store" | tail -2
git log --oneline -2