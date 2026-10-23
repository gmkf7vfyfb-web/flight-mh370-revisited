cd out && python3 - <<'EOF'
import csv,re
rows=list(csv.reader(open('hydroacoustics-bibliography.csv')))
strip={'Shockley1982','Heaney1991','Heaney2017','Heaney2009','Munk1974','Chapman1988','Franz1959','Orr1976','Turner2007','Blackman2004JASA','Stiassnie2010','Renzi2014','Mei2018','Yamamoto1982','Tolstoy2006','deGrootHedlin1999','Munk1994'}
for r in rows[1:]:
    if r[0] in strip:
        r[4]=re.sub(r'(\d+(\(\d+\))?):[\dA-Z\-]+$',r'\1',r[4]).rstrip('-')
    if r[0]=='Shockley1982': r[1]='Shockley, R.C. et al.'
    if r[0]=='Nielsen2021': r[4]='Pure and Applied Geophysics 178:2557-'
csv.writer(open('hydroacoustics-bibliography.csv','w',newline='')).writerows(rows)
for r in rows[1:]:
    if r[0] in strip: print(r[0],'|',r[4])
EOF