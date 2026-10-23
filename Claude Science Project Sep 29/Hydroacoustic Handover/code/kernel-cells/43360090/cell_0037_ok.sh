cd out && python3 - <<'EOF'
import csv
rows=list(csv.reader(open('hydroacoustics-bibliography.csv')))
add=[
["Heyburn2018","Heyburn, R. et al.",2018,"Hydroacoustic detections of the 2016 US Navy full ship shock trial explosions at H10N (as cited in Brown2026 Table A.4)","not retrieved","not resolved","unknown","secondary only (Brown2026 Table A.4)","LR1;LR3","y"],
["Bittner2024","Bittner, P. et al.",2024,"Detections of the 2021 full ship shock trial at H10N (as cited in Brown2026 Table A.4)","not retrieved","not resolved","unknown","secondary only (Brown2026 Table A.4)","LR1;LR3","y"],
["TrouSansFond2025","(authors not recorded)",2025,"Hydroacoustic signals recorded by CTBTO network suggest a possible submarine landslide in Trou Sans Fond Canyon, offshore Ivory Coast, March 2024","Seismol. Res. Lett. 96(4):2253-","https://pubs.geoscienceworld.org/ssa/srl/article-abstract/96/4/2253/653283/","closed","abstract (search result)","LR6","n"],
]
rows+=add
csv.writer(open('hydroacoustics-bibliography.csv','w',newline='')).writerows(rows); print(len(rows)-1)
EOF
sed -i '' 's/Trou Sans Fond SRL abstract (search result, not in CSV)/TrouSansFond2025 (abstract only)/' hydroacoustics-literature-review.md; grep -n "TrouSansFond" hydroacoustics-literature-review.md | head -3