set -u
# Standard run report for the run-J northern supplement seeds (order D2, 19 Oct 2026). Reads job b6389957's final files
# (read only; nothing there is changed, moved or deleted). Heavy lock: flock on ~/.mh370-heavy.lock (the lock deskstar jobs
# use); no background monitor, so no fd-9 leak.
WORK=$PWD; R0=$HOME/mh370; JB=/home/pete/.claude-science-scratch/.claude-science/jobs/b6389957-e258-4fdf-bbdb-8d4ec4b5daac
tl() { echo "$(date -u +%FT%TZ) $*" >> $WORK/timeline.txt; }; fail() { tl "NO-GO $2"; exit $1; }
exec 9>>$HOME/.mh370-heavy.lock; tl "waiting for heavy lock"; flock -w 36000 9 || fail 8 "heavy lock busy"; tl "heavy lock held"
git -C $R0/repo fetch -q origin claude-science-sep29 && git -C $R0/repo worktree add -f --detach $WORK/wt $REV > /dev/null 2>&1 || fail 2 "worktree"
E="$WORK/wt/Claude Science Project Sep 29/engine"
python3 -m venv $WORK/venv 9>&- && $WORK/venv/bin/pip install -q numpy matplotlib scipy 9>&- > $WORK/pip.log 2>&1 || fail 3 "venv"
$WORK/venv/bin/python -c "import numpy, matplotlib; print(numpy.__version__, matplotlib.__version__)" >> $WORK/timeline.txt
RUNS=""; for s in $(seq 1001 1016); do RUNS="$RUNS $JB/runs/north-$s"; done
python3 "$E/report/merge_seed_runs.py" $WORK/merged $RUNS >> $WORK/timeline.txt 2>&1 || fail 4 "merge"
$R0/bin-3bf0801 summarise $WORK/merged --root "$E" >> $WORK/timeline.txt 2>&1 || fail 5 "summarise"
python3 -c "import json;s=json.load(open('$WORK/merged/summary.json'));print('reference', s['reference']['path'], 'cases', len(s['cases'][0]['replicates']))" >> $WORK/timeline.txt
mkdir -p $WORK/out; cd "$E"; tl "report start"
OMP_NUM_THREADS=4 $WORK/venv/bin/python report/build_supplement_report.py $WORK/merged $WORK/out/run-j-supplement-north-report.pdf > $WORK/report.log 2>&1; tl "report exit $?"
cp $WORK/merged/summary.json $WORK/merged/run.json $WORK/out/; cd $WORK; tar czf report.tgz out
git -C $R0/repo worktree remove --force $WORK/wt 2>/dev/null; git -C $R0/repo worktree prune; rm -rf $WORK/venv
tl "DONE"
