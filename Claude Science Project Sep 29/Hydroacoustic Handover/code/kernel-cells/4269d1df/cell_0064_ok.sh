mkdir -p jobB && cp jobL/*.toml jobL/legs.txt jobB/ && cp jobsnap/reduce.py jobB/ && python3 - <<'EOF'
import json, numpy as np
meta=json.load(open('jobsnap/meta.json')); times=meta['times']; tg=meta['grid_t']
pts=[]
for la in np.round(np.arange(-35.0,-16.999,0.5),3):
    for lo in np.round(np.arange(96.0,113.001,0.5),3):
        if 96.0<=lo<=106.5 and -31.0<=la<=-21.0: continue
        pts.append((lo,la))
n=int(np.ceil(len(pts)/250))
for i in range(n):
    ch=pts[i*250:(i+1)*250]
    s="releases = ["+", ".join(f"[{lo:.3f}, {la:.3f}, {tg:.1f}]" for lo,la in ch)+"]\n"+"times = ["+", ".join(f"{t:.1f}" for t in times)+"]\n"
    open(f'jobB/spec-E{i}.toml','w').write(s)
json.dump(dict(ext_points=pts,nchunks=n,times=times,grid_t=tg),open('jobB/meta-ext.json','w'))
print(len(pts),n)
EOF
cat > jobB/kadriB.sh <<'EOF'
#!/bin/bash
# Kadri-Haixun conditional, drift leg: (1) L-point likelihood legs, (2) origin-connectivity extension snapshots. Heavy: waits for the
# drift thread's arc-latitude chain, then holds ~/.mh370-heavy.lock for the whole job (no lock drop between legs).
set -u
W=$(pwd); O=$HOME/.claude-science-scratch/ocean
ENG="$HOME/mh370/drift/repo/Claude Science Project Sep 29/engine/hypotheses"
BIN=$HOME/mh370/drift/target/release/deps/mh370_hypotheses-beedacd1154063da
echo "queued $(date -u +%FT%TZ) binsha $(sha256sum $BIN | cut -c1-16)"
while pgrep -f "chain_arclat|run_arclat.sh|aus160/run.sh|chain3" > /dev/null; do sleep 120; done
echo "drift chains gone $(date -u +%FT%TZ)"
exec 9>>"$HOME/.mh370-heavy.lock"; flock 9
echo "lock taken $(date -u +%FT%TZ)"
mkdir -p out runs
while read L; do
  [ -z "$L" ] && continue
  sed "s|OUTROOT|$W/runs|" $W/$L.toml > "$ENG/debris-drift/$L.toml"
  ( cd "$ENG"; env DRIFT_CONFIG="debris-drift/$L.toml" RAYON_NUM_THREADS=88 $BIN pilot --ignored --nocapture > $W/out/$L.log 2>&1 ); RC=$?
  rm -f "$ENG/debris-drift/$L.toml"
  cp $W/runs/$L/nodes.csv $W/out/$L-nodes.csv 2>/dev/null; cp $W/runs/$L/summary.toml $W/out/$L-summary.toml 2>/dev/null
  echo "$L EXIT=$RC $(date -u +%FT%TZ) $(grep -c . $W/out/$L-nodes.csv 2>/dev/null) $(grep oom_kill /sys/fs/cgroup/memory.events | tr '\n' ' ')"
done < $W/legs.txt
# (2) connectivity extension (snapshot harness, 28-day forcing only)
mkdir -p f; cd f
for p in $O/glorys12/grid/glorys12v1_uo_vo_surface-00.json $O/glorys12/grid/glorys12v1_uo_vo_surface-00.f32 \
         $O/era5/era5_u10_v10_3h_15-120E_50-0S_20140307-20141231.json $O/era5/era5_u10_v10_3h_15-120E_50-0S_20140307-20141231.f32 \
         $O/globcurrent/grid/globcurrent_my_p1d_uo_vo_0m-00.json $O/globcurrent/grid/globcurrent_my_p1d_uo_vo_0m-00.f32; do ln -sf $p .; done
echo '{"parts": ["glorys12v1_uo_vo_surface-00.json"]}' > glorys12-mar-apr2014.series.json
echo '{"parts": ["era5_u10_v10_3h_15-120E_50-0S_20140307-20141231.json"]}' > era5-2014.series.json
echo '{"parts": ["globcurrent_my_p1d_uo_vo_0m-00.json"]}' > globcurrent.series.json
cd $W
for M in globcurrent glorys12; do
  C=$W/snapE-$M.toml
  CUR=$W/f/glorys12-mar-apr2014.series.json; [ $M = globcurrent ] && CUR=$W/f/globcurrent.series.json
  sed -e "s|^particles_per_class = .*|particles_per_class = 100|" -e "s|^threads = .*|threads = 88|" \
      -e "s|^domain = .*|domain = [15.0, 120.0, -50.0, 0.0]|" \
      -e "s|^current_manifest = .*|current_manifest = \"$CUR\"|" -e "s|^wind10_manifest = .*|wind10_manifest = \"$W/f/era5-2014.series.json\"|" \
      "$ENG/debris-drift/aus160-$M.toml" > $C
  for S in $(ls spec-E*.toml | sed 's/spec-//; s/.toml//' | sort -V); do
    ( cd "$ENG"; env DRIFT_CONFIG=$C SNAP_SPEC=$W/spec-$S.toml SNAP_OUT=$W/raw-$S-$M.bin RAYON_NUM_THREADS=88 \
        $BIN debris_drift::tests::snapshots --exact --ignored --nocapture > $W/out/snap-$S-$M.log 2>&1 ) || echo "FAIL $S $M"
    echo "snap $S $M $(stat -c %s $W/raw-$S-$M.bin) $(date -u +%FT%TZ)"
  done
  cat $(ls raw-E*-$M.bin | sort -V) > rawE-$M.bin; python3 reduce.py rawE-$M.bin snapE-$M.bin; rm -f raw-E*-$M.bin rawE-$M.bin
done
grep oom /sys/fs/cgroup/memory.events
sha256sum out/*-nodes.csv snapE-*.bin > SHA256SUMS; ls -la out snapE-*.bin; echo "end $(date -u +%FT%TZ)"
EOF
ls jobB | wc -l