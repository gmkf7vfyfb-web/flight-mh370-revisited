cd /Users/pete/Downloads/flight-mh370-revisited
B=origin/claude-science-sep29; P='Claude Science Project Sep 29'
git show $B:"$P/results/hydroacoustics-digitised-sources.md" | sed -n '83,104p' | cut -c1-420
echo; echo "=== Sci Rep Kadri2019 / JASA Kadri2019 in bibliography"
git show $B:"$P/results/hydroacoustics-bibliography.csv" | tr -d '\r' | grep -i -E "1121/1.5125251|San Juan|Wang" | cut -c1-300
echo; echo "=== Usama Kadri Sep 11.pdf: pages 1-3 text"
python3 - <<'EOF'
import pypdf
r=pypdf.PdfReader('/Users/pete/Downloads/Usama Kadri Sep 11.pdf')
for i in (0,1,2):
    print('--p',i+1, (r.pages[i].extract_text() or '')[:350].replace('\n',' '))
EOF