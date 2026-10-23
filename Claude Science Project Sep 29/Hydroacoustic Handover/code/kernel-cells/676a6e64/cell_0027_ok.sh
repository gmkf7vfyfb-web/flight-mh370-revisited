set +e
echo "=== disk"; df -k /System/Volumes/Data | tail -1 | awk '{printf "free %.1f GiB of %.0f GiB\n",$4/1048576,$2/1048576}'
echo "=== load"; uptime; sysctl -n hw.ncpu
echo "=== top cpu users"; ps -Ao pcpu,comm -r | head -8
E=/Users/pete/Downloads/mh370-exchange
echo "=== exchange"; ls $E 2>/dev/null
echo "--- hydro"; ls -la $E/hydroacoustics 2>/dev/null; ls $E/hydroacoustics/run-j 2>/dev/null
echo "--- eof run-j"; ls $E/end-of-flight/run-j 2>/dev/null | head; ls $E/end-of-flight/run-j-supplement/reduced 2>/dev/null
echo "--- one seed"; ls -la $E/end-of-flight/run-j/run-j-free/seed-1 2>/dev/null | head -20
echo "--- imos"; ls $E/hydroacoustics/imos* 2>/dev/null | head; du -sh $E/hydroacoustics/* 2>/dev/null
echo "--- ocean transport"; ls $E/ocean-transport 2>/dev/null | head
echo "=== workspace"; ls; ls hydro 2>/dev/null | head