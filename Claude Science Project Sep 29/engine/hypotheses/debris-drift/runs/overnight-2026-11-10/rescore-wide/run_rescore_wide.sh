set -u
# Rescoring of the wide-windage legs with the module's offline rescorer (R3 configuration: 25 segments, 4 periods, bandwidths 50/25/100/200 km, 22 exterior finds and shadows).
# Waits for the wide-windage chain; takes the shared heavy lock; 6 processes (memory-safe); output gzip per leg.
C=$HOME/mh370/drift/coef; J=$PWD; mkdir -p out $C/rescore/cfgw $C/rescore/out/R3W
cp $J/*.toml $J/tasks.txt $C/rescore/cfgw/
until grep -q ALL-DONE $C/runs/wide-chain.log 2>/dev/null; do sleep 60; done
exec 9>>$HOME/.mh370-heavy.lock; flock 9
T0=$(date +%s)
cat $C/rescore/cfgw/tasks.txt | xargs -P 6 -I{} sh -c "DRIFT_RESCORE=$C/rescore/cfgw/{}.toml $C/bin-rescore rescore_entry --ignored --nocapture > $C/rescore/cfgw/{}.log 2>&1; echo {} \$? >> $C/rescore/cfgw/status.txt"
echo "seconds $(( $(date +%s) - T0 ))" > out/summary.txt; sort $C/rescore/cfgw/status.txt | awk '{print $2}' | sort | uniq -c >> out/summary.txt
for f in $C/rescore/out/R3W/*.jsonl; do gzip -kf $f; cp $f.gz out/; done
ls -la out >> out/summary.txt
echo ALL-DONE >> out/summary.txt
