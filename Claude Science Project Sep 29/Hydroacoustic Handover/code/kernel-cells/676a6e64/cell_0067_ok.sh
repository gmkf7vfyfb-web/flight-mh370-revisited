uptime; df -k /System/Volumes/Data | tail -1 | awk '{printf "free %.1f GiB\n",$4/1048576}'
G=/Users/pete/Downloads/mh370-exchange/hydroacoustics; du -sh $G/run-j-gated 2>/dev/null; ls $G/run-j-gated 2>/dev/null | head; ls $G/run-j-gated/*/ 2>/dev/null | head -5
ls -t $G/run-j-tl-grid/tables | head -5; ls $G/run-j-tl-grid | head