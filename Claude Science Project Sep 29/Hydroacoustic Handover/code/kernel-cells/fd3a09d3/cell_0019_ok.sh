cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/data/ocean_paths"
cat README.txt | head -60; echo; cat export_fix_check.json | head -c 800; echo
grep -rn -i "decade\|95A4\|A5B4\|B5C2\|monthly\|season" ../../../../../coordination/OCEAN_TRANSPORT.md 2>/dev/null | head -10
grep -n -i "woa\|decade\|95A4\|A5B4" /Users/pete/Downloads/mh370-exchange/ocean-transport/paths-calibration/README.md | head
python -c "
import json;print(json.dumps(json.load(open('/Users/pete/Downloads/mh370-exchange/ocean-transport/paths-calibration/af447-H10S_meta.json')))[:1200])"