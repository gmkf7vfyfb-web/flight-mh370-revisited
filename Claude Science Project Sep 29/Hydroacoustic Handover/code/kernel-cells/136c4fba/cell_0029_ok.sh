R=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i-dive
ls $R/next-i-free/seed-1/
echo "=== COLUMNS ==="; cat $R/next-i-free/seed-1/COLUMNS.txt 2>/dev/null | tr ',' '\n' | nl | head -40
echo "=== sizes ==="; du -sh $R/next-i-free/seed-1/* | head
echo "=== tau90 npz ==="; ls $R/next-i-free/seed-1/ | grep -i tau