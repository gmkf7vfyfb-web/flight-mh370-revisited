cd "repo/Claude Science Project Sep 29"
cat results/hydroacoustics-run-j-windows.md
echo ---- WEAK SIGNAL (headings + key tables)
grep -n '^#\|P_D\|SNR\|dB\|c1+c2\|template\|M1b' results/hydroacoustics-weak-signal-methods.md | head -120