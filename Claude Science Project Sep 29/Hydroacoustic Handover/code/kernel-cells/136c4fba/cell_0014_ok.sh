ls /Users/pete/Downloads/mh370-exchange 2>/dev/null && echo "--- hydro ---" && ls -R /Users/pete/Downloads/mh370-exchange/hydroacoustics 2>/dev/null | head -60
echo "=== mh370-inputs ==="; ls /Users/pete/Downloads/mh370-inputs 2>/dev/null | head; ls /Users/pete/Downloads/mh370-inputs/hydroacoustics 2>/dev/null | head -20
echo "=== imos ==="; ls /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos 2>/dev/null | head -20
echo "=== search for DAT ==="; find /Users/pete/Downloads -maxdepth 5 -iname "*.DAT" 2>/dev/null | head -5
echo "=== search imos dirs ==="; find /Users/pete/Downloads -maxdepth 4 -type d -iname "*imos*" 2>/dev/null | head