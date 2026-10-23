set -e; export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd repo; B=claude-science-sep29
python3 - <<'EOF'
p="Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j.md"; s=open(p).read()
old="2. **Timing is recovered to within ±0.3 s (5–95 %) once detected** at ≥ +5 dB, and the recovered level is within +1.5 dB of the injected level at 0 dB and within +0.5 dB above +10 dB."
new=("2. **Timing is recovered to within ±0.3 s (5–95 %) once detected at ≥ +5 dB for the τ = 3.3 s cell at every receiver.** Pooled over the three τ cells the 5 % tail is wider where detections are few: −2.5 s at the H08S proxy at +5 dB and −9 to −11 s at 0 dB on 3376 and 3275; at ≥ +10 dB every receiver and τ is within ±0.25 s, and ≥ 96 % of detections lie within ±5 s at every level from 0 dB up. The recovered level is within +1.5 dB of the injected level at 0 dB and within +0.5 dB above +10 dB.")
assert old in s; s=s.replace(old,new)
old2="Timing error = time of the statistic maximum minus the pulse's energy-peak time; the full table by receiver, detector, α, τ and level is `errors.csv`."
new2="Timing error = time of the statistic maximum minus the pulse's energy-peak time. The rows above are means over the three τ cells; the wide 5 % tails at 0 dB and at the H08S proxy at +5 dB come from τ cells with few detections (for τ = 3.3 s alone every receiver is within −0.2 to +0.3 s at +5 dB). The full table by receiver, detector, α, τ and level is `errors.csv`."
assert old2 in s; s=s.replace(old2,new2)
open(p,"w").write(s)
EOF
git fetch -q origin $B 2>/dev/null; export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j.md"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C4=$(git -c user.name="Hydroacoustic Module (block 7 injection-recovery)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 7 note: timing-recovery claim qualified (±0.3 s holds for tau 3.3 s at >= +5 dB; pooled-tau 5 % tails to -2.5 s at H08S proxy +5 dB and -9..-11 s at 0 dB; all within ±0.25 s at >= +10 dB). Review finding.")
git push -q "$URL" $C4:refs/heads/$B 2>/dev/null && echo "PUSHED $C4"
cp "Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j.md" ../