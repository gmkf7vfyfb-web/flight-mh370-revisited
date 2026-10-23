X=/Users/pete/Downloads/mh370-exchange/searched-areas/kadri-haixun-2026-10-18
(cd $X && shasum -a 256 -c SHA256SUMS | grep -vc OK)
rm -rf red; rm -f ocean/wind_l4_2014.nc; df -h /Users/pete/Downloads | tail -1