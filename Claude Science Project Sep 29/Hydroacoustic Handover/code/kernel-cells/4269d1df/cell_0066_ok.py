pc='''E="$HOME/mh370/drift/repo/Claude Science Project Sep 29/engine/hypotheses"; W=$(pwd)
for f in kadri-globcurrent-T-crossing.toml kadri-glorys12-C-haixun.toml kadri-glorys12-ref-anchors.toml; do
  sed "s|OUTROOT|$W/runs|" $f > "$E/debris-drift/$f"
  ( cd "$E"; env DRIFT_CONFIG=debris-drift/$f RAYON_NUM_THREADS=2 timeout 8 $HOME/mh370/drift/target/release/deps/mh370_hypotheses-beedacd1154063da pilot --ignored --nocapture > $W/parse-$f.log 2>&1 ); echo "rc=$? $f"
  rm -f "$E/debris-drift/$f"; grep -v "^$" parse-$f.log | head -6
done; ls -R runs 2>/dev/null | head'''
jp=c.submit_job(command=pc, intent='Parse-check three Kadri drift configs on deskstar (8 s each, 2 threads; config copies removed after)',
   inputs=['jobB/kadri-globcurrent-T-crossing.toml','jobB/kadri-glorys12-C-haixun.toml','jobB/kadri-glorys12-ref-anchors.toml'], outputs=['parse-*.log'], run_timeout_s=300)
print(jp.id)