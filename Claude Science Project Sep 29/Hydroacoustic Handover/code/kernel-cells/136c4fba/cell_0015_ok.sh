I=/Users/pete/Downloads/mh370-inputs/hydroacoustics/imos
ls "$I/MH370" | head -5; echo "..."; find "$I/MH370" -maxdepth 3 -type d | head -20
echo "=== 3376 files around 00:45-01:00 ==="
find "$I" -path "*3376*" -type f | head -8
echo "=== counts ==="
find "$I" -type f | sed 's#.*/##' | sed 's/[0-9]//g' | sort | uniq -c | sort -rn | head -10
echo "=== background dir ==="; ls "$I/background" | head -10; find "$I/background" -maxdepth 2 -type d|head -10
echo "=== du ==="; du -sh "$I"/* 2>/dev/null