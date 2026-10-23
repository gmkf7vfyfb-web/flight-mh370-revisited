cd "repo/Claude Science Project Sep 29"
grep -n '^#' results/hydroacoustics-weak-signal-methods.md
echo ----
grep -n 'M1b\|template\|c1+c2\|P_D = 0.5\|7 dB\|alpha\|dispersion' results/hydroacoustics-weak-signal-methods.md | head -50