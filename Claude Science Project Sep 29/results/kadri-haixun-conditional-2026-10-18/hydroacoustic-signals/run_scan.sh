#!/bin/bash
cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/e930c577-74fa-4f4d-b81c-c962d137f24d/leg"
echo "lock acquired $(date -u +%H:%M:%SZ)"
for st in run-j-free run-j-repro-radar run-j-descent-climb run-j-waypoints; do
  python scan_runj_L.py /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j /Users/pete/Downloads/mh370-exchange/core/run-j "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/e930c577-74fa-4f4d-b81c-c962d137f24d/leg/../erepo/Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke" scan $st 2>&1 | grep -v -i -E 'proj|ca_bundle'
done
echo "done $(date -u +%H:%M:%SZ)"
