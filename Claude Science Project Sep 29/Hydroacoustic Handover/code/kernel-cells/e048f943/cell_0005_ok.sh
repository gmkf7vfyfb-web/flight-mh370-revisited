cd repo/"Claude Science Project Sep 29"
cat results/hydroacoustics-run-j-windows.md > /tmp/notes_windows.txt
cat results/hydroacoustics-tl-grid-run-j.md > /tmp/notes_tl.txt
cp /tmp/notes_windows.txt /tmp/notes_tl.txt "$OLDPWD"/ 2>/dev/null; echo ok