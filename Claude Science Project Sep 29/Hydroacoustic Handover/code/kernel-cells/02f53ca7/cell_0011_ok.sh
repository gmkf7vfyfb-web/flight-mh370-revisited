cd repo; git ls-tree -r --name-only HEAD | grep -i "brown\|papers/" | head; cd ..
cd hydro; git ls-tree -r --name-only origin/hypothesis/hydroacoustics | grep -i "papers\|brown" | head; cd ..
ls /Users/pete/Downloads/mh370-inputs/ 2>/dev/null; ls /Users/pete/Downloads/mh370-inputs/hydroacoustics/ 2>/dev/null
find /Users/pete/Downloads -maxdepth 4 -iname "*brown*" 2>/dev/null | head; find /Users/pete/Downloads -maxdepth 5 -iname "*f-35*" -o -maxdepth 5 -iname "*f35*" 2>/dev/null | head
ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/ 2>/dev/null
df -k /System/Volumes/Data | tail -1