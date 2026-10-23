W=/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222
du -sh $W/workspaces/* 2>/dev/null | sort -h | tail -8
du -sh $W/artifacts 2>/dev/null
du -sh /Users/pete/Downloads/mh370-exchange/hydroacoustics/* 2>/dev/null | sort -h | tail -4
du -sh /tmp 2>/dev/null
echo "--- biggest new files in child workspaces (last 3h)"; find $W/workspaces -type f -size +200M -mmin -180 2>/dev/null | xargs -I{} du -h {} 2>/dev/null | sort -h | tail -12
echo "--- artifact store recent big"; find $W/artifacts -type f -size +200M -mmin -180 2>/dev/null | xargs -I{} du -h {} 2>/dev/null | sort -h | tail -8