R=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j
ls $R/summary/ $R/summary/impact-time | head -40
echo ==== README
cat $R/summary/README.md 2>/dev/null | head -150