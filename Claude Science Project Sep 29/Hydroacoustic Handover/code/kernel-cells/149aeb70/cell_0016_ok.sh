R=/Users/pete/Downloads/mh370-exchange/core/run-i; ls -R $R | head -60; echo "=== sizes"; du -sh $R/*; echo "=== run.json keys"; python3 -c "
import json,glob
for f in sorted(glob.glob('$R/*/run.json')):
    d=json.load(open(f))
    print('##',f.split('/')[-2], list(d.keys())[:40])
"