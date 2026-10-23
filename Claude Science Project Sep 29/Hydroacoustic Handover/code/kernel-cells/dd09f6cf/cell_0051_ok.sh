cd lib; R=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j
jobs=""; for st in run-j-waypoints run-j-free run-j-repro-radar run-j-descent-climb; do for sd in $R/$st/seed-*; do k=${sd##*-}; f=../red/${st}_$k.npz; [ -f $f ] || jobs="$jobs $st:$k"; done; done
echo $jobs | tr ' ' '\n' | xargs -P 5 -I{} sh -c 'st=$(echo {} | cut -d: -f1); k=$(echo {} | cut -d: -f2); python reduce_kh.py $st $k ../red/${st}_$k.npz 2>&1 | grep -v -i "pyproj\|_set_context"'
ls ../red | wc -l