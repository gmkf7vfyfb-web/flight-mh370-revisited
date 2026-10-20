#!/bin/bash
echo "chain start $(date -u +%FT%TZ) load $(uptime | sed 's/.*averages: //')"
EOF_CORE=/Users/pete/Downloads/mh370-exchange/core/next-run-c STANDIN_OUT=/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/14a4dd3f-9a30-4bb8-9f1b-d19d4441c1df/abc-repro PAIRS="next-c-descent-climb:1" /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/14a4dd3f-9a30-4bb8-9f1b-d19d4441c1df/standin/sweep_2241_ab_standin.sh
P12=""; for k in 1 2; do for s in free repro-radar routes descent-climb; do P12="$P12 next-d-$s:$k"; done; done
PAIRS="$P12" /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/14a4dd3f-9a30-4bb8-9f1b-d19d4441c1df/standin/sweep_2241_ab_standin.sh
touch /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/14a4dd3f-9a30-4bb8-9f1b-d19d4441c1df/abd/SEEDS12-DONE
P34=""; for k in 3 4; do for s in free repro-radar routes descent-climb; do P34="$P34 next-d-$s:$k"; done; done
[ -e /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/14a4dd3f-9a30-4bb8-9f1b-d19d4441c1df/abd/STOP ] || PAIRS="$P34" /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/14a4dd3f-9a30-4bb8-9f1b-d19d4441c1df/standin/sweep_2241_ab_standin.sh
echo "chain end $(date -u +%FT%TZ)"
