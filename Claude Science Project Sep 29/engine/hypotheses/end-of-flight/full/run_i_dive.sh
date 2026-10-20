#!/bin/bash
cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/83c5d472-a2a6-4ff0-9602-ceefbdadb1ad/repo/Claude Science Project Sep 29/engine"
B=/Users/pete/Downloads/mh370-exchange/end-of-flight/bin/mh370-eof-ri3
X="hypotheses/end-of-flight/full/c2-silent-aim.toml hypotheses/end-of-flight/full/dive-branch.toml"
EOF_BIN=$B EOF_EXTRA="$X hypotheses/end-of-flight/smoke/children-16.toml" EOF_STRATA=next-i-waypoints EOF_OUT=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i-dive EOF_TAG=RID bash hypotheses/end-of-flight/full/sweep_run_i.sh
rm -f /Users/pete/Downloads/mh370-exchange/end-of-flight/run-i-dive/SWEEP-DONE
EOF_BIN=$B EOF_EXTRA="$X" EOF_STRATA="next-i-free next-i-descent-climb next-i-repro-radar" EOF_OUT=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i-dive EOF_TAG=RID bash hypotheses/end-of-flight/full/sweep_run_i.sh
