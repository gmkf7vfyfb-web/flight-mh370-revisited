C="repo/Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md"
wc -l "$C"; grep -n "^## \|^### " "$C" | tail -8
echo ====TAIL====
tail -c 7000 "$C"
echo; echo ====EXCHANGE====
ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/
ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-windows/ 2>&1 | head
ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/ /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables 2>&1 | head -40