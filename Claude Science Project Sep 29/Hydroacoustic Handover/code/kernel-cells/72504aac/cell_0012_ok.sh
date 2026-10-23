X=/Users/pete/Downloads/mh370-exchange
tail -5 $X/core/run-j/run-j-waypoints/COMPACT.txt | cut -c1-300; ls -la $X/core/run-j/run-j-waypoints/bto-bfo/seed-1 ; ls $X/core/run-j/run-j-waypoints/bto-bfo/seed-1/* | head
ls $X/core/run-j/; ls $X/core/ | head -30; find $X/core/run-j -name "*route*" | head; find $X/core -maxdepth 3 -iname "README*" | head