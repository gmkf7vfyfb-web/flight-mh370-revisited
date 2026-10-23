R=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j
cat $R/README.md | head -120
echo ==== table-0019-mixture.txt
head -60 $R/summary/table-0019-mixture.txt
echo ==== family shares
python -c "import json;d=json.load(open('$R/summary/family-shares-run-j.json'));print(json.dumps(d,indent=1)[:3000])"