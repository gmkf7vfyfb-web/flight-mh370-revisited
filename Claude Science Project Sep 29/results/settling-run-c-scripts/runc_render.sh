#!/bin/sh
# Render settling's run C products (all rows; speed-capped). Labels from end of flight's run C stratum READMEs and core's run C report.
set -eu
W=$(pwd); SM2="$W/wt-base/Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke"
ARCS="/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/386151e9-859f-412a-8d9d-b8da48899575/repo/Claude Science Project Sep 29/engine/runs/reference-289/run.json"
EOFC=$(cd "$SM2" && git log -1 --format=%h); SETC=9330d4c
export WF_SEEDS=1,2,3,4,5,6,7,8
LAB="core run C split-half NOT converged (min 0.82-0.86 against floor 0.924); rapid descents above 6,500 ft/min and unloading not reachable by the model; residual roll P(left) = 0.8 PROVISIONAL; trim at loss and two-tank takeover NOT applied; families family4_code (ruling 6 as amended)"
export WF_FOOT_SUBS=$(python3 -c "
import json,sys; L=sys.argv[1]
print(json.dumps([['end of flight next-run on core (b)', 'end of flight on core run C'],
 ['Labels: core (b) split-half NOT converged; two-tank bookkeeping only; internal-v1 one-engine flow 2x; dive class (b) and Boeing glide PROVISIONAL-OVERNIGHT', 'Labels: ' + L]]))" "$LAB")
python3 wf_standard.py render "$SM2" "$ARCS" nrc run-c "$SETC" "$EOFC"
export WF_FOOT_SUBS=$(python3 -c "
import json,sys; L=sys.argv[1]
print(json.dumps([['Labels: core split-half NOT converged; two-tank bookkeeping only; dive class (b) PROVISIONAL; point mass cannot unload', 'Labels: ' + L]]))" "$LAB")
WF_FAMILY_MAP=ruling6 python3 wf_family.py render "$SM2" "$ARCS" nrcg run-c "$SETC" "$EOFC"
if [ -e field/nrcgSF2_elements.f64 ]; then
  export WF_FOOT_SUBS=$(python3 -c "
import json,sys; L=sys.argv[1]
print(json.dumps([['end of flight next-run on core (b)', 'end of flight on core run C'],
 ['Labels: core (b) split-half NOT converged; two-tank bookkeeping only; internal-v1 one-engine flow 2x; dive class (b) and Boeing glide PROVISIONAL-OVERNIGHT', 'Labels: ' + L]]))" "$LAB")
  WF_SPEED_CAP_MPS=212 python3 wf_standard.py render "$SM2" "$ARCS" nrcS run-c-speedcap "$SETC" "$EOFC"
  export WF_FOOT_SUBS=$(python3 -c "
import json,sys; L=sys.argv[1]
print(json.dumps([['Labels: core split-half NOT converged; two-tank bookkeeping only; dive class (b) PROVISIONAL; point mass cannot unload', 'Labels: ' + L]]))" "$LAB")
  WF_SPEED_CAP_MPS=212 WF_FAMILY_MAP=ruling6 python3 wf_family.py render "$SM2" "$ARCS" nrcgS run-c-speedcap "$SETC" "$EOFC"
fi
echo RENDER_DONE
