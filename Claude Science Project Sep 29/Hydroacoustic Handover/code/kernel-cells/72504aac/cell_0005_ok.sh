X=/Users/pete/Downloads/mh370-exchange
find $X/hydroacoustics/run-j-searches -maxdepth 2 | head -50
echo ===; ls -d $X/composer/run-j-views-v3* ; ls $X/composer/run-j-views-v3*/ | head
echo ===; ls $X/core/run-j/ | head; 
echo ===; ls $X/end-of-flight/run-j/; ls $X/end-of-flight/run-j/run-j-waypoints/ | head -3; ls $X/end-of-flight/run-j/run-j-waypoints/seed-1/
echo ===; ls $X/hydroacoustics/run-j-tl-grid/tables/
grep -rl -E "00:28:38|D preferred" "repo/Claude Science Project Sep 29/results" --include=*.md --include=*.py --include=*.csv 2>/dev/null | head