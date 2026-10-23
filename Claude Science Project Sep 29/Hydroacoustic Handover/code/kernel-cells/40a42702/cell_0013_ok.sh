cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/
ls run-j/ run-j/primary-tau-eof | head; cat run-j/primary-tau-eof/COLUMNS.txt 2>/dev/null | head -40; ls run-j/primary-tau-eof/* | head -5
echo --- run.json; python -c "import json;d=json.load(open('run-j/primary-tau-eof/run.json'));print({k:(v if len(str(v))<300 else str(v)[:300]) for k,v in d.items()})" 2>/dev/null | head -30
echo --- tl grid; ls run-j-tl-grid/ | head; 
echo --- module results-data
cd "$OLDPWD/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data"
ls blackman_noise stageB ram_check tl_recal_block9 run_i | head -60