OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
mkdir -p $OUT/levels-rerun; ln -sfn /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/draws $OUT/levels-rerun/draws; ls -la $OUT/levels-rerun
ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/logs; grep -h "D0/p0.5" /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/logs/* | head -3
R="repo/Claude Science Project Sep 29"; sed -n 39,62p "$R/results/hydroacoustics-run-j-levels.md"