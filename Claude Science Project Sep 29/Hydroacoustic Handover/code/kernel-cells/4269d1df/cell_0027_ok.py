
red = r'''
import struct, sys, os
# reduce snapshot binary (88-byte records, 9 times) to: u8 rel, env, class, fate + f32 lon/lat at time idx 4..7
src, dst, ntimes = sys.argv[1], sys.argv[2], 9
R = 16 + 8*ntimes
with open(src,'rb') as f, open(dst,'wb') as g:
    while True:
        b = f.read(R*65536)
        if not b: break
        out = bytearray()
        for i in range(0, len(b), R):
            r = b[i:i+R]
            out += r[0:4] + r[16+8*4:16+8*8]
        g.write(out)
print('reduced', os.path.getsize(src)//R, 'records')
'''
open('jobsnap/reduce.py','w').write(red)
sh = r'''#!/bin/bash
set -u
W=$(pwd); O=$HOME/.claude-science-scratch/ocean
ENG="$HOME/mh370/drift/repo/Claude Science Project Sep 29/engine/hypotheses"
BIN=$HOME/mh370/drift/target/release/deps/mh370_hypotheses-beedacd1154063da
echo "bin sha $(sha256sum $BIN | cut -c1-16) start $(date -u +%FT%TZ)"
mkdir -p f; cd f
for p in $O/glorys12/grid/glorys12v1_uo_vo_surface-00.json $O/glorys12/grid/glorys12v1_uo_vo_surface-00.f32 \
         $O/era5/era5_u10_v10_3h_15-120E_50-0S_20140307-20141231.json $O/era5/era5_u10_v10_3h_15-120E_50-0S_20140307-20141231.f32 \
         $O/globcurrent/grid/globcurrent_my_p1d_uo_vo_0m-00.json $O/globcurrent/grid/globcurrent_my_p1d_uo_vo_0m-00.f32; do ln -sf $p .; done
echo '{"parts": ["glorys12v1_uo_vo_surface-00.json"]}' > glorys12-mar-apr2014.series.json
echo '{"parts": ["era5_u10_v10_3h_15-120E_50-0S_20140307-20141231.json"]}' > era5-2014.series.json
echo '{"parts": ["globcurrent_my_p1d_uo_vo_0m-00.json"]}' > globcurrent.series.json
cd $W
for M in globcurrent glorys12; do
  C=$W/snap-$M.toml
  CUR=$W/f/glorys12-mar-apr2014.series.json; [ $M = globcurrent ] && CUR=$W/f/globcurrent.series.json
  sed -e "s|^particles_per_class = .*|particles_per_class = PPC|" -e "s|^threads = .*|threads = 16|" \
      -e "s|^domain = .*|domain = [15.0, 120.0, -50.0, 0.0]|" \
      -e "s|^current_manifest = .*|current_manifest = \"$CUR\"|" -e "s|^wind10_manifest = .*|wind10_manifest = \"$W/f/era5-2014.series.json\"|" \
      "$ENG/debris-drift/aus160-$M.toml" > $C.tmpl
  grep -n "^particles_per_class\|^threads\|^domain\|manifest =\|c_wind_product\|^release_unix_s\|sigma_m_s\|^env_seeds" $C.tmpl
  for S in L G0 G1 G2 G3 G4 G5 G6 G7; do
    PPC=100; [ $S = L ] && PPC=8334
    sed "s|PPC|$PPC|" $C.tmpl > $C
    ( cd "$ENG"; env DRIFT_CONFIG=$C SNAP_SPEC=$W/spec-$S.toml SNAP_OUT=$W/raw-$S-$M.bin RAYON_NUM_THREADS=16 \
        /usr/bin/time -v $BIN debris_drift::tests::snapshots --exact --ignored --nocapture > $W/log-$S-$M.txt 2>&1 ) || { echo "FAIL $S $M"; tail -20 $W/log-$S-$M.txt; exit 3; }
    grep -E "Maximum resident|Elapsed" $W/log-$S-$M.txt | tr '\n' ' '; echo " $S $M $(stat -c %s $W/raw-$S-$M.bin)"
  done
  cat $W/raw-G?-$M.bin > $W/rawG-$M.bin; python3 $W/reduce.py $W/rawG-$M.bin $W/snapG-$M.bin; rm -f $W/raw-G?-$M.bin $W/rawG-$M.bin
  mv $W/raw-L-$M.bin $W/snapL-$M.bin
done
cat /sys/fs/cgroup/memory.events | grep oom
sha256sum snap*.bin > SHA256SUMS; ls -la snap*.bin; echo "end $(date -u +%FT%TZ)"
'''
open('jobsnap/run.sh','w').write(sh)
print(sorted(os.listdir('jobsnap')))
