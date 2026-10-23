uptime; df -k /System/Volumes/Data | tail -1 | awk '{printf "free %.1f GiB\n",$4/1048576}'
cd repo; export GIT_CONFIG_GLOBAL=/dev/null
git fetch -q origin claude-science-sep29 hypothesis/hydroacoustics 2>/dev/null
echo "=== module branch new commits"; git log --format='%h %ci %s' origin/hypothesis/hydroacoustics | head -8 | cut -c1-150
echo "=== work branch new commits"; git log --format='%h %ci %s' origin/claude-science-sep29 | head -5 | cut -c1-150
ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/ | grep run-j