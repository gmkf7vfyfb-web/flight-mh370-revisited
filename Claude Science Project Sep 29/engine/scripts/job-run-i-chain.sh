# Copied 2026-10-15 from deskstar J/6a2ec01f-3a06-4810-92bb-b3d4efca768f/job-run-i-chain.sh (J = /home/pete/.claude-science-scratch/.claude-science/jobs), sha256 dac45a64281a47a1421e36650fb6021ebccbeeb0c45eff2d0ed2eddcbf35691c (of the source without this line); no functional change. Core order 2026-10-15b step 2.
# Detached sequencing (12 Oct): wait for the descent-climb job to finish, compact it, then run the
# reproduction stratum and compact it. No live session is needed between strata.
J=/home/pete/.claude-science-scratch/.claude-science/jobs
DC=$J/18b756b6-778f-4681-890c-08a1fa96f8c7
CMP=$J/53d0d251-e343-4b9a-8a2c-cafdfacce879/compact_c.py
tl() { echo "$(date -u +%FT%TZ) $*" >> timeline.txt; }
tl "chain: waiting for descent-climb DONE ($DC)"
n=0; while [ ! -e $DC/DONE ]; do sleep 60; n=$((n+1)); [ $n -gt 300 ] && { tl "chain: descent-climb not DONE after 5 h, NO-GO"; exit 7; }; done
sleep 120   # let descent-climb pack its small files
tl "chain: descent-climb DONE; compacting"
python3 $CMP $DC/runs-i/next-i-descent-climb > compact-dc.log 2>&1; tl "chain: dc compacted (exit $?)"
STRATUM=repro sh job-run-i.sh
R=$(ls -d runs-i/next-i-repro-radar 2>/dev/null)
[ -n "$R" ] && { python3 $CMP $PWD/$R > compact-repro.log 2>&1; tl "chain: repro compacted (exit $?)"; }
touch CHAIN-DONE; tl "chain: done"
