cd "repo/Claude Science Project Sep 29/results"
python - <<'EOF'
p='hydroacoustics-injection-recovery-run-j.md'; s=open(p).read()
s=s.replace("Per receiver alone, no single receiver reaches P_D = 0.5 at η ≤ 10⁻²... except 3315, 3275, H01W, H08S at (2.5–6.3) × 10⁻³; 3376 and 3274 do not (section 5, gap G7-5).",
 "Per receiver alone, 3315, 3275, H01W and H08S reach P_D = 0.5 at η = (2.5–6.3) × 10⁻³, while 3376 and 3274 do not reach it below 10⁻² (the difference between co-located loggers is in the TL table, section 5, gap G7-5).")
s=s.replace("and (1–3) × 10⁻³ north of 34°S.", "and mostly (1–3) × 10⁻³ north of 34°S (thin bands scatter more).")
open(p,'w').write(s)
EOF
grep -c "G7-5" hydroacoustics-injection-recovery-run-j.md