import base64
cfgs={}
for f in ['kadri-globcurrent-T-crossing.toml','kadri-glorys12-C-haixun.toml','kadri-glorys12-ref-anchors.toml']:
    cfgs[f]=base64.b64encode(open('jobB/'+f,'rb').read()).decode()
cmd='mkdir -p /tmp/kparse && cd /tmp/kparse && '
for f,b in cfgs.items():
    cmd+=f"echo {b} | base64 -d | sed 's|OUTROOT|/tmp/kparse/runs|' > '$HOME/mh370/drift/repo/Claude Science Project Sep 29/engine/hypotheses/debris-drift/{f}' && "
cmd+='''cd "$HOME/mh370/drift/repo/Claude Science Project Sep 29/engine/hypotheses"; for f in kadri-globcurrent-T-crossing.toml kadri-glorys12-C-haixun.toml kadri-glorys12-ref-anchors.toml; do env DRIFT_CONFIG=debris-drift/$f RAYON_NUM_THREADS=2 timeout 6 $HOME/mh370/drift/target/release/deps/mh370_hypotheses-beedacd1154063da pilot --ignored --nocapture 2>&1 | grep -v "^$" | head -8; echo "rc=$? $f"; rm -f debris-drift/$f; done; ls /tmp/kparse/runs 2>/dev/null; rm -rf /tmp/kparse'''
r=c.call_command(cmd, intent='Parse-check three Kadri drift configs (6 s timeout each, 2 threads, files removed after)')
print(r.stdout[-3000:], r.stderr[-1500:])