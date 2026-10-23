
t = show(f'{P}/paper/CITATIONS-LEDGER.md')
lines = t.split('\n')
# find main table header at line 197
start = [i for i,l in enumerate(lines) if l.startswith('| Key | Reference (JON Harvard style)')][0]
rows=[]
for l in lines[start+2:]:
    if not l.startswith('|'): break
    cells=[c.strip() for c in l.strip().strip('|').split('|')]
    rows.append(cells)
print(len(rows))
print(collections.Counter(r[2] for r in rows))
print(collections.Counter(r[3] for r in rows))
print(collections.Counter(r[5] for r in rows))
for r in rows:
    if r[5] not in ('-','—','') or 'not' in r[3].lower() or 'NOT' in r[3]:
        print(r[0],'|',r[2],'|',r[3][:60],'|',r[5][:80])
print('-----SAT REGISTER')
s = show(f'{P}/results/satellite-coverage-2014-03/coincidence/literature/satellite-literature-register.csv').replace('\r','')
srows = list(csv.DictReader(io.StringIO(s)))
print(len(srows), list(srows[0].keys()))
for k in srows[0].keys():
    vals=collections.Counter(r[k] for r in srows)
    if len(vals)<12: print(k, dict(vals))
