#!/bin/bash
set -u
C=$HOME/mh370/drift/coef; J=$PWD; mkdir -p out
exec 9>>$HOME/.mh370-heavy.lock; flock 9
mkdir -p $C/rescore && tar xzf cfg.tgz -C $C/rescore
for v in R1-oldwindow R2-allcoasts R3-allcoasts-4periods R4-4periods; do mkdir -p $C/rescore/out/$v; done
T0=$(date +%s)
cat $C/rescore/cfg/tasks.txt | xargs -P 24 -I{} sh -c "DRIFT_RESCORE=$C/rescore/cfg/{}.toml $C/bin-rescore rescore_entry --ignored --nocapture > $C/rescore/cfg/{}.log 2>&1; echo {} \$? >> $C/rescore/status.txt"
echo "seconds $(( $(date +%s) - T0 ))" > out/summary.txt; sort $C/rescore/status.txt | awk '{print $2}' | sort | uniq -c >> out/summary.txt
cd $C/rescore/out && for v in *; do (cd $v && wc -l *.jsonl | tail -1) ; done >> $J/out/summary.txt
cd $C/rescore && tar czf rescore-out.tgz out cfg/*-meta.json && ls -la rescore-out.tgz >> $J/out/summary.txt
