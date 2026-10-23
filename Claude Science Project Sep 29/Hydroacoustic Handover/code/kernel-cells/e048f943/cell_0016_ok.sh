cd hydro/"Claude Science Project Sep 29"
grep -n "7 dB\|STA/LTA\|snr50\|P_D = 0.5\|P_D=0.5\|matched filter\|M1b" results/hydroacoustics-weak-signal-methods.md | head -40
echo ----
ls /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/background/3376 | head -3; d=$(ls -d /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/background/3376/* | head -1); ls $d | head; ls $d/raw 2>/dev/null | head -3; ls $d/raw 2>/dev/null | wc -l
cat engine/hypotheses/hydroacoustics/results-data/weak_signal/README.txt | head -40