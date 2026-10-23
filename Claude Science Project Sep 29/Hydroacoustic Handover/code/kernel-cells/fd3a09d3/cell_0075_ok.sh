sed -i '' 's/\.to_markdown(index=False)/.to_string(index=False)/g; s/\.to_markdown()/.to_string()/g' /tmp/note_numbers.py
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid
for i in $(seq 1 18); do if [ -f $OUT/raw/passB/tl_grid.csv ]; then break; fi; sleep 30; done
grep paths $OUT/raw/passB.log | tail -1; ls $OUT/raw/passB; grep paths $OUT/raw/passC.log 2>/dev/null | tail -1; date -u