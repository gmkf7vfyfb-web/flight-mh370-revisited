cd build/at_src/at
export FC=gfortran
FF="-O2 -std=gnu -ffree-line-length-none -mcpu=native -I../misc -I../tslib"
for d in misc tslib Kraken KrakenField Bellhop; do (cd $d && make -k all FC=gfortran FFLAGS="$FF" LAPACK_LIBS="-llapack" > ../build_$d.log 2>&1; echo "$d rc=$?"); done
ls -la bin/ 2>/dev/null; ls Kraken/*.exe KrakenField/*.exe Bellhop/*.exe 2>/dev/null
grep -i -m3 -E 'error' build_*.log